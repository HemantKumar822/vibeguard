"""Authoritative intake limits for safety-v1."""
import hashlib
import json

POLICY_ID = 'safety-v1'
LIMITS = {'aggregate_bytes': 25 * 1024 * 1024, 'files': 5000, 'file_bytes': 2 * 1024 * 1024,
          'path_depth': 20, 'path_bytes': 240, 'metadata_bytes': 2 * 1024 * 1024, 'header_bytes': 8192}
FINGERPRINT = hashlib.sha256(json.dumps(LIMITS, sort_keys=True).encode()).hexdigest()
