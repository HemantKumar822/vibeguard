import json
import socket
import time
from unittest.mock import Mock
import pytest
from backend.adapters import web_capture as web


@pytest.mark.parametrize('value',[
    'http://127.0.0.1/','http://169.254.169.254/','http://10.0.0.1/','http://[::1]/',
    'http://[::ffff:127.0.0.1]/','https://example.com:8443/','http://example.com:443/',
    'https://user:password@example.com/','https://example.com/#x','file:///etc/passwd',
    'https://example.com/?token=synthetic','https://example.com/\r\nInjected','https://example.com\\evil/',
    'https://example.com/'+'x'*4096])
def test_reject_unsafe_target(value):
    with pytest.raises(web.CaptureError): web.target(value)


def test_target_and_redacted_query():
    assert web.target('https://EXAMPLE.com:443')=='https://example.com/'
    assert web.display(web.target('https://example.com/page?q=not-a-secret'))=='https://example.com/page?query=redacted'


@pytest.mark.parametrize('ip',['10.1.2.3','169.254.169.254','127.0.0.1','::1','::ffff:10.0.0.1','224.0.0.1'])
def test_connection_time_private_dns_rejected(monkeypatch,ip):
    family=socket.AF_INET6 if ':' in ip else socket.AF_INET
    monkeypatch.setattr(web.socket,'getaddrinfo',lambda *a,**kw:[(family,socket.SOCK_STREAM,6,'',(ip,443))])
    with pytest.raises(web.CaptureError): web.resolve('example.com',443,1)


def test_dns_rebinding_rechecks_each_connection(monkeypatch):
    resolver=Mock(side_effect=[[(2,1,6,'',('93.184.216.34',443))],[(2,1,6,'',('127.0.0.1',443))]])
    monkeypatch.setattr(web.socket,'getaddrinfo',resolver)
    assert web.resolve('example.com',443,1)[0][4][0]=='93.184.216.34'
    with pytest.raises(web.CaptureError): web.resolve('example.com',443,1)
    assert resolver.call_count==2


def test_connection_pins_numeric_peer_and_rejects_changed_peer(monkeypatch):
    monkeypatch.setattr(web,'resolve',lambda *args:[(2,1,6,'',('93.184.216.34',80))])
    sock=Mock();sock.getpeername.return_value=('127.0.0.1',80)
    monkeypatch.setattr(web.socket,'socket',Mock(return_value=sock))
    with pytest.raises(web.CaptureError): web.PinnedHTTP('example.com',80,timeout=1).connect()
    sock.connect.assert_called_once_with(('93.184.216.34',80))
    sock.close.assert_called_once()


def test_encoded_credential_path_rejected():
    with pytest.raises(web.CaptureError): web.target('https://example.com/sk%2Dproj%2D'+'SyntheticCredential'*3)


def fake_response(url,body=b'<html></html>',mime='text/html',status=200,headers=None):
    return {'url':url,'status':status,'headers':[('Content-Type',mime),*(headers or [])],'body':body}


def fake_fetch(routes,visited):
    def fetch(url,budget):
        budget.before();visited.append(url)
        result=routes[url]
        budget.consume(len(result['body']))
        return {**result}
    return fetch


def test_capture_discovers_only_same_origin_without_script_execution():
    start='https://example.com/'
    routes={start:fake_response(start,b'<a href="/next">next</a><script src="/app.js"></script><script>fetch("/runtime.js")</script><script src="https://elsewhere.example/script.js"></script>'),
            start+'next':fake_response(start+'next'),start+'app.js':fake_response(start+'app.js',b'const x=1','application/javascript')}
    visited=[];result=web.capture(start,fetcher=fake_fetch(routes,visited))
    assert set(visited)==set(routes)
    assert not result['complete']
    assert any(item['reason']=='cross_origin_not_fetched' for item in result['exclusions'])
    assert not any('runtime.js' in url for url in visited)


@pytest.mark.parametrize('destination',['http://127.0.0.1/','https://elsewhere.example/'])
def test_unsafe_redirect_never_fetched(destination):
    start='https://example.com/'; visited=[]
    result=web.capture(start,fetcher=fake_fetch({start:fake_response(start,status=302,headers=[('Location',destination)])},visited))
    assert visited==[start] and not result['complete']


def test_redirects_count_and_stop_after_three():
    start='https://example.com/'
    routes={start+str(i):fake_response(start+str(i),status=302,headers=[('Location','/'+str(i+1))]) for i in range(5)}
    visited=[]; result=web.capture(start+'0',fetcher=fake_fetch(routes,visited))
    assert len(visited)==4 and result['requests']==4 and not result['complete']


@pytest.mark.parametrize('limit,kind',[('pages','page'),('assets','asset')])
def test_crawl_limits_stop_before_send(monkeypatch,limit,kind):
    monkeypatch.setitem(web.LIMITS,limit,1)
    start='https://example.com/'
    html=b'<a href="/next">next</a>' if kind=='page' else b'<script src="/a.js"></script><script src="/b.js"></script>'
    routes={start:fake_response(start,html),start+'next':fake_response(start+'next'),
            start+'a.js':fake_response(start+'a.js',b'const x=1','application/javascript'),start+'b.js':fake_response(start+'b.js',b'x','application/javascript')}
    visited=[]; result=web.capture(start,fetcher=fake_fetch(routes,visited))
    assert not result['complete'] and len(visited)==(1 if kind=='page' else 2)


def test_request_and_byte_budget_prevents_further_send(monkeypatch):
    budget=web.Budget(requests=200)
    with pytest.raises(web.CaptureError,match='request_limit'): budget.before()
    monkeypatch.setitem(web.LIMITS,'response_bytes',4)
    budget=web.Budget()
    with pytest.raises(web.CaptureError,match='response_byte_limit'): budget.consume(5)
    with pytest.raises(web.CaptureError,match='capture_timeout'): web.Budget(deadline=time.monotonic()-1).before()
    with pytest.raises(web.CaptureError,match='job_cancelled'): web.Budget(active=lambda:False).before()


def test_body_cap_terminates_connection(monkeypatch):
    response=Mock(status=200)
    response.getheaders.return_value=[('Content-Type','text/plain')]
    response.getheader.return_value='identity'
    response.read1.return_value=b'0123456789'
    connection=Mock();connection.getresponse.return_value=response
    monkeypatch.setattr(web,'PinnedHTTPS',Mock(return_value=connection))
    monkeypatch.setitem(web.LIMITS,'body_bytes',8)
    with pytest.raises(web.CaptureError,match='body_limit'): web.fetch('https://example.com/',web.Budget())
    connection.close.assert_called_once()


def test_har_preserves_bytes_and_only_get_requests(tmp_path):
    record=fake_response('https://example.com/',b'<html>\xff</html>')
    web.write_har([record],tmp_path/'capture.har')
    import base64
    har=json.loads((tmp_path/'capture.har').read_text())['log']['entries'][0]
    assert har['request']['method']=='GET' and har['request']['cookies']==[]
    assert base64.b64decode(har['response']['content']['text'])==record['body']
