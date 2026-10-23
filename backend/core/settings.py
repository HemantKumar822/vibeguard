"""Explicit external runtime configuration; imports never create storage."""
import os
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlsplit

@dataclass(frozen=True)
class Settings:
    runtime_dir: Path
    origin: str = 'http://127.0.0.1:8000'
    loopback_http: bool = False

    def validate(self):
        root = self.runtime_dir
        checkout = Path(__file__).resolve().parents[2]
        if not root.is_absolute() or root.is_symlink():
            raise ValueError('Unsafe runtime configuration')
        resolved = root.resolve()
        if resolved == checkout or checkout in resolved.parents or any('onedrive' in p.casefold() for p in resolved.parts):
            raise ValueError('Unsafe runtime configuration')
        for parent in [root, *root.parents]:
            if parent.is_symlink() or (parent.exists() and hasattr(parent, 'is_junction') and parent.is_junction()):
                raise ValueError('Unsafe runtime configuration')
        url = urlsplit(self.origin)
        if url.path or url.query or url.fragment or url.username or not url.hostname:
            raise ValueError('Unsafe origin configuration')
        if url.scheme != 'https' and not (self.loopback_http and url.scheme == 'http' and url.hostname in {'127.0.0.1', 'localhost', '::1'}):
            raise ValueError('HTTPS or explicit loopback development is required')
        return self

    @classmethod
    def environment(cls):
        value = os.environ.get('VIBEGUARD_RUNTIME_DIR')
        if not value:
            return None
        return cls(Path(value), os.environ.get('VIBEGUARD_ORIGIN', 'http://127.0.0.1:8000'),
                   os.environ.get('VIBEGUARD_LOOPBACK_HTTP') == '1').validate()

