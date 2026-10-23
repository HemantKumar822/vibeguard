"""Authoritative intake limits for safety-v1."""
import hashlib
import json

POLICY_ID = 'safety-v1'
LIMITS = {'aggregate_bytes': 25 * 1024 * 1024, 'files': 5000, 'file_bytes': 2 * 1024 * 1024,
          'path_depth': 20, 'path_bytes': 240, 'metadata_bytes': 2 * 1024 * 1024, 'header_bytes': 8192}
WEB_LIMITS={'requests':200,'pages':50,'assets':50,'body_bytes':2*1024*1024,
            'response_bytes':20*1024*1024,'seconds':60,'redirects':3,'url_bytes':4096}
FINGERPRINT = hashlib.sha256(json.dumps({'source':LIMITS,'website':WEB_LIMITS,
    'website_profile':'connection-pinned-get-and-network-none-passive-har-v1'}, sort_keys=True).encode()).hexdigest()
