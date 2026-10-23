"""GET-only bounded capture. Every connection resolves and pins a public peer."""
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from html.parser import HTMLParser
import http.client
import ipaddress
import json
import base64
import queue
import re
import socket
import ssl
import threading
import time
from urllib.parse import urlsplit, urlunsplit, urljoin, parse_qsl, urldefrag, unquote
from backend.core.policy import WEB_LIMITS as LIMITS

SECRET=re.compile(r'(?:AKIA|ASIA)[A-Z0-9]{16}|gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|sk-(?:[A-Za-z0-9_-]{20,})|sk_live_[A-Za-z0-9]{20,}')
PRIVATE_PARAMETER=re.compile(r'(?:token|secret|password|credential|auth|api.?key)',re.I)
TEXT_TYPES={'application/javascript','text/javascript','text/css','application/json','text/plain','application/xml','text/xml'}


class CaptureError(ValueError): pass


def target(value):
    try:
        if not isinstance(value,str) or len(value.encode())>LIMITS['url_bytes'] or not value or any(ord(c)<=32 or ord(c)==127 for c in value) or '#' in value or '\\' in value or SECRET.search(unquote(value)): raise ValueError
        parsed=urlsplit(value)
        if parsed.scheme not in {'http','https'} or parsed.username is not None or parsed.password is not None or not parsed.hostname: raise ValueError
        host=parsed.hostname.encode('idna').decode().lower()
        if '%' in host or host.endswith('.') or not re.fullmatch(r'[a-z0-9.:-]+',host): raise ValueError
        port=parsed.port or (443 if parsed.scheme=='https' else 80)
        if port != (443 if parsed.scheme=='https' else 80): raise ValueError
        if any(PRIVATE_PARAMETER.search(key) or SECRET.search(value) for key,value in parse_qsl(parsed.query,keep_blank_values=True)): raise ValueError
        try:
            address=ipaddress.ip_address(host)
        except ValueError: pass
        else:
            if not public(address): raise ValueError
        netloc=f'[{host}]' if ':' in host else host
        return urlunsplit((parsed.scheme,netloc,parsed.path or '/',parsed.query,''))
    except (ValueError,UnicodeError,TypeError): raise CaptureError('invalid_or_sensitive_target') from None


def origin(url):
    parsed=urlsplit(url)
    return parsed.scheme,parsed.hostname,443 if parsed.scheme=='https' else 80


def display(url):
    parsed=urlsplit(url)
    return urlunsplit((parsed.scheme,parsed.netloc,parsed.path,'query=redacted' if parsed.query else '', ''))


def public(address):
    mapped=getattr(address,'ipv4_mapped',None)
    return address.is_global and not address.is_multicast and (mapped is None or mapped.is_global)


def resolve(host,port,timeout):
    answer=queue.Queue(maxsize=1)
    def lookup():
        try: answer.put(socket.getaddrinfo(host,port,type=socket.SOCK_STREAM))
        except Exception: answer.put(None)
    threading.Thread(target=lookup,daemon=True).start()
    try: records=answer.get(timeout=max(.01,min(5,timeout)))
    except queue.Empty: raise CaptureError('dns_timeout') from None
    if not records: raise CaptureError('dns_unavailable')
    for _,_,_,_,address in records:
        if not public(ipaddress.ip_address(address[0])): raise CaptureError('blocked_destination')
    return records


class PinnedHTTP(http.client.HTTPConnection):
    tls=False
    def connect(self):
        deadline=time.monotonic()+self.timeout
        records=resolve(self.host,self.port,self.timeout)
        for family,kind,proto,_,address in records:
            sock=socket.socket(family,kind,proto)
            try:
                remaining=deadline-time.monotonic()
                if remaining<=0: raise TimeoutError
                sock.settimeout(remaining); sock.connect(address)
                peer=ipaddress.ip_address(sock.getpeername()[0])
                if not public(peer) or peer!=ipaddress.ip_address(address[0]): raise CaptureError('blocked_peer')
                remaining=deadline-time.monotonic()
                if remaining<=0: raise TimeoutError
                sock.settimeout(remaining)
                self.sock=ssl.create_default_context().wrap_socket(sock,server_hostname=self.host) if self.tls else sock
                return
            except Exception:
                sock.close()
        raise CaptureError('connection_failed')


class PinnedHTTPS(PinnedHTTP): tls=True


@dataclass
class Budget:
    deadline: float=field(default_factory=lambda:time.monotonic()+LIMITS['seconds'])
    requests: int=0
    bytes: int=0
    pages: int=0
    assets: int=0
    active: object=field(default=lambda:True,repr=False)
    def check(self):
        if time.monotonic()>=self.deadline: raise CaptureError('capture_timeout')
        if not self.active(): raise CaptureError('job_cancelled')
    def before(self):
        self.check()
        if self.requests>=LIMITS['requests']: raise CaptureError('request_limit')
        self.requests+=1
    def consume(self,amount):
        self.check(); self.bytes+=amount
        if self.bytes>LIMITS['response_bytes']: raise CaptureError('response_byte_limit')


def fetch(url,budget):
    budget.before()
    parsed=urlsplit(url); scheme,host,port=origin(url)
    connection=(PinnedHTTPS if scheme=='https' else PinnedHTTP)(host,port,timeout=min(5,budget.deadline-time.monotonic()))
    def abort():
        try:
            sock=connection.sock
            if sock: sock.shutdown(socket.SHUT_RDWR)
        except OSError: pass
        connection.close()
    stopped=threading.Event()
    def watch():
        while not stopped.wait(.25):
            if time.monotonic()>=budget.deadline or not budget.active(): abort(); return
    guard=threading.Thread(target=watch,daemon=True); guard.start()
    try:
        connection.request('GET',urlunsplit(('', '',parsed.path or '/',parsed.query,'')),headers={
            'User-Agent':'VibeGuard/1.0 authorized-passive-review','Accept':'text/html, application/javascript, text/css, application/json, text/plain;q=0.8','Accept-Encoding':'identity','Connection':'close'})
        response=connection.getresponse()
        headers=response.getheaders()
        header_size=sum(len(k.encode())+len(v.encode())+4 for k,v in headers)
        if header_size>65536: raise CaptureError('header_limit')
        budget.consume(header_size)
        if response.getheader('Content-Encoding','identity').lower() not in {'identity',''}: raise CaptureError('unsupported_content_encoding')
        body=bytearray()
        while True:
            budget.check()
            if connection.sock: connection.sock.settimeout(min(5,max(.01,budget.deadline-time.monotonic())))
            chunk=response.read1(min(65536,LIMITS['body_bytes']+1-len(body)))
            if not chunk: break
            budget.consume(len(chunk)); body.extend(chunk)
            if len(body)>LIMITS['body_bytes']: raise CaptureError('body_limit')
        return {'url':url,'status':response.status,'headers':headers,'body':bytes(body)}
    finally:
        stopped.set(); connection.close()


class Links(HTMLParser):
    def __init__(self): super().__init__(convert_charrefs=True); self.links=[]; self.truncated=False
    def handle_starttag(self,tag,attributes):
        attrs=dict(attributes)
        value=attrs.get('href') if tag in {'a','link'} else attrs.get('src') if tag=='script' else None
        if value and len(value)<=4096:
            if len(self.links)>=1000: self.truncated=True; return
            if tag=='a': self.links.append((value,'page'))
            elif tag=='script' or 'stylesheet' in attrs.get('rel','').lower(): self.links.append((value,'asset'))


def capture(start,active=lambda:True,fetcher=fetch):
    start=target(start); allowed=origin(start); budget=Budget(active=active)
    pending=deque([(start,'page',0)]); scheduled={start}; entries=[]; exclusions=[]; incomplete=False
    while pending:
        url,kind,redirects=pending.popleft()
        try:
            budget.check()
            if kind=='page' and budget.pages>=LIMITS['pages']: raise CaptureError('page_limit')
            if kind=='asset' and budget.assets>=LIMITS['assets']: raise CaptureError('asset_limit')
            record=fetcher(url,budget)
            record['kind']=kind; entries.append(record)
            if kind=='page': budget.pages+=1
            else: budget.assets+=1
            headers={key.lower():value for key,value in record['headers']}
            if record['status'] in {301,302,303,307,308}:
                destination=target(urldefrag(urljoin(url,headers.get('location','')))[0])
                if not headers.get('location') or origin(destination)!=allowed or redirects>=LIMITS['redirects'] or destination in scheduled: raise CaptureError('blocked_or_looping_redirect')
                scheduled.add(destination); pending.appendleft((destination,kind,redirects+1)); continue
            if record['status']<200 or record['status']>=300: raise CaptureError('http_error')
            mime=headers.get('content-type','').split(';')[0].strip().lower()
            record['mime']=mime
            if mime in {'text/html','application/xhtml+xml'} and kind=='page':
                parser=Links(); parser.feed(record['body'].decode('utf-8',errors='replace'))
                if parser.truncated: incomplete=True; exclusions.append({'resource_key':display(url),'reason':'link_discovery_limit'})
                for href,next_kind in parser.links:
                    try:
                        discovered=target(urldefrag(urljoin(url,href))[0])
                        if origin(discovered)!=allowed: raise CaptureError('cross_origin_not_fetched')
                        if discovered in scheduled: continue
                        if len(scheduled)>=LIMITS['requests']: raise CaptureError('discovery_limit')
                        scheduled.add(discovered); pending.append((discovered,next_kind,0))
                    except CaptureError as exc:
                        incomplete=True; exclusions.append({'resource_key':f'omitted-link-{len(exclusions):04d}','reason':str(exc)})
            elif mime not in TEXT_TYPES:
                incomplete=True; exclusions.append({'resource_key':display(url),'reason':'non_text_or_unexpected_content'})
        except Exception as exc:
            if not budget.active(): raise CaptureError('job_cancelled') from None
            incomplete=True
            code=str(exc) if isinstance(exc,CaptureError) else 'fetch_failed'
            exclusions.append({'resource_key':display(url),'reason':code})
            if code in {'capture_timeout','request_limit','response_byte_limit'}: break
        if len(exclusions)>=1000: incomplete=True; break
    # Runtime-loaded and cross-origin resources are never claimed as assessed.
    return {'entries':entries,'exclusions':exclusions[:1000],'complete':bool(entries) and not incomplete and not pending,
            'requests':budget.requests,'bytes':budget.bytes,'pages':budget.pages,'assets':budget.assets}


def write_har(records,path):
    entries=[]
    for record in records:
        body=base64.b64encode(record['body']).decode('ascii')
        entries.append({'startedDateTime':datetime.now(timezone.utc).isoformat(),'time':1,
            'request':{'method':'GET','url':record['url'],'httpVersion':'HTTP/1.1','headers':[{'name':'Host','value':urlsplit(record['url']).netloc}],'cookies':[],'queryString':[],'headersSize':-1,'bodySize':0},
            'response':{'status':record['status'],'statusText':http.client.responses.get(record['status'],'Response'),
                'httpVersion':'HTTP/1.1','headers':[{'name':key,'value':value} for key,value in record['headers']],
                'cookies':[],'content':{'size':len(record['body']),'mimeType':record.get('mime','text/plain'),'text':body,'encoding':'base64'},'redirectURL':'','headersSize':-1,'bodySize':len(record['body'])},
            'cache':{},'timings':{'send':0,'wait':1,'receive':0}})
    path.write_text(json.dumps({'log':{'version':'1.2','creator':{'name':'VibeGuard','version':'1'},'entries':entries}}),encoding='utf-8')
