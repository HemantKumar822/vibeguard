"""Optional server-owned HTTPS JSON port. One request, no redirects or retries."""
import http.client
import json
import os
import queue
import socket
import threading
import time
from urllib.parse import urlsplit


def configuration():
    endpoint=os.environ.get('VIBEGUARD_AI_ENDPOINT','')
    parsed=urlsplit(endpoint)
    if (os.environ.get('VIBEGUARD_AI_ENABLED')!='1' or parsed.scheme!='https' or not parsed.hostname
        or parsed.username or parsed.password or parsed.fragment or parsed.query):
        return None
    return parsed


def explain(payload, timeout=15):
    endpoint=configuration()
    if endpoint is None: raise ValueError('ai_unconfigured')
    body=json.dumps(payload,ensure_ascii=False).encode()
    if len(body)>24*1024: raise ValueError('ai_request_limit')
    deadline=time.monotonic()+min(15,max(0,timeout))
    connection=http.client.HTTPSConnection(endpoint.hostname,endpoint.port or 443,timeout=15)
    result=queue.Queue(maxsize=1)
    stopped=threading.Event()
    def remaining():
        value=deadline-time.monotonic()
        if stopped.is_set() or value<=0: raise TimeoutError('ai_timeout')
        if connection.sock: connection.sock.settimeout(value)
        return value
    def request():
        try:
            # DNS may be uninterruptible on some systems. No request is sent if it returns late.
            connection.connect()
            remaining()
            headers={'Content-Type':'application/json','Accept':'application/json'}
            token=os.environ.get('VIBEGUARD_AI_TOKEN')
            if token: headers['Authorization']='Bearer '+token
            connection.request('POST',endpoint.path or '/',body=body,headers=headers)
            remaining()
            response=connection.getresponse()
            if response.status!=200: raise ValueError('ai_provider_failed')
            data=bytearray()
            while True:
                remaining()
                chunk=response.read1(min(1024,8193-len(data)))
                if not chunk: break
                data.extend(chunk)
                if len(data)>8192: raise ValueError('ai_response_limit')
            remaining()
            result.put((bytes(data),None))
        except Exception as exc:
            result.put((None,exc))
        finally:
            connection.close()
    threading.Thread(target=request,daemon=True).start()
    try:
        try: value,error=result.get(timeout=max(.001,deadline-time.monotonic()))
        except queue.Empty: raise TimeoutError('ai_timeout') from None
        if error: raise error
        return value
    finally:
        stopped.set()
        if connection.sock:
            try: connection.sock.shutdown(socket.SHUT_RDWR)
            except OSError: pass
        connection.close()
