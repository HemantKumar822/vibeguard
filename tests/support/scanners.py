"""Shared deterministic test doubles and synthetic website captures."""
import json

FAKE='SyntheticCredential_1234567890'
URL='https://example.com/'

def leak(path='app/src/main.ts',line=1):
    return {'RuleID':'vg-secret-assignment','File':path,'StartLine':line,
            'Secret':FAKE,'Match':FAKE,'Unknown':{'nested':FAKE}}


class StubScanner:
    versions={'gitleaks':'8.30.1','semgrep':'1.182.1'}
    def scan(self,tool,source,scan_id,active):
        assert active()
        if tool=='gitleaks': return json.dumps([leak()]).encode()
        return json.dumps({'results':[],'errors':[],'paths':{'scanned':['/source/app/src/main.ts']}}).encode()


def observed(url,active):
    assert active()
    return {'entries':[{'url':URL,'status':200,'headers':[('Content-Type','text/html')],
        'body':f'<html><script>const password = "{FAKE}";</script></html>'.encode(),'mime':'text/html'}],
        'exclusions':[],'complete':True,'requests':1,'bytes':100,'pages':1,'assets':0}
