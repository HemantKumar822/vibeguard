"""Private metadata store. No scanner or worker writes exist in this story."""
import os
import secrets
import subprocess
import stat
import sqlite3
import time
from contextlib import contextmanager

class Storage:
    def __init__(self, settings):
        self.root = settings.runtime_dir.resolve()
        self.root.mkdir(parents=True, exist_ok=True, mode=0o700)
        # Inspect with lstat before opening SQLite or traversing a source directory.
        descendants = []
        pending = [self.root]
        while pending:
            path = pending.pop()
            info = path.lstat()
            if stat.S_ISLNK(info.st_mode) or getattr(info, 'st_file_attributes', 0) & 0x400:
                raise ValueError('Unsafe runtime descendant')
            if path != self.root:
                descendants.append(path)
            if stat.S_ISDIR(info.st_mode):
                pending.extend(path.iterdir())
            elif not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
                raise ValueError('Unsafe runtime descendant')
        if os.name == 'nt':
            # Restrict the runtime directory to its owner; children inherit this ACL.
            identity = subprocess.run(['whoami', '/user', '/fo', 'csv', '/nh'], capture_output=True, text=True, check=True).stdout.strip()
            import csv
            sid = next(csv.reader([identity]))[1]
            # Replace, rather than append to, a possibly permissive existing ACL.
            script = (
                '$id = New-Object System.Security.Principal.SecurityIdentifier($env:VG_RUNTIME_SID); '
                '$paths = New-Object System.Collections.Generic.Stack[string]; '
                '$paths.Push($env:VG_RUNTIME_PATH); while ($paths.Count -gt 0) { '
                '$path = $paths.Pop(); $attrs = [System.IO.File]::GetAttributes($path); '
                'if (($attrs -band 1024) -ne 0) { throw "Unsafe runtime descendant" }; '
                '$isDir = ($attrs -band 16) -ne 0; '
                'if ($isDir) { $acl = New-Object System.Security.AccessControl.DirectorySecurity } '
                'else { $acl = New-Object System.Security.AccessControl.FileSecurity }; '
                '$acl.SetOwner($id); $acl.SetAccessRuleProtection($true,$false); '
                '$inherit = if ($isDir) { "ContainerInherit,ObjectInherit" } else { "None" }; '
                '$rule = New-Object System.Security.AccessControl.FileSystemAccessRule('
                '$id,"FullControl",$inherit,"None","Allow"); $acl.AddAccessRule($rule); '
                'if ($isDir) { [System.IO.Directory]::SetAccessControl($path,$acl); '
                'foreach ($child in [System.IO.Directory]::GetFileSystemEntries($path)) { $paths.Push($child) } } '
                'else { [System.IO.File]::SetAccessControl($path,$acl) } }'
            )
            subprocess.run(['powershell', '-NoProfile', '-NonInteractive', '-Command',
                            script], capture_output=True, check=True,
                           env={**os.environ, 'VG_RUNTIME_PATH': str(self.root), 'VG_RUNTIME_SID': sid})
        else:
            os.chmod(self.root, 0o700)
            for path in descendants:
                os.chmod(path, 0o700 if path.is_dir() else 0o600)
        self.staging = self.root / 'sources'
        self.staging.mkdir(mode=0o700, exist_ok=True)
        self.database = self.root / 'metadata.sqlite3'
        with self.connect() as db:
            db.executescript('''CREATE TABLE IF NOT EXISTS sessions (id TEXT PRIMARY KEY, csrf TEXT, touched REAL);
            CREATE TABLE IF NOT EXISTS scans (id TEXT PRIMARY KEY, owner TEXT, idem TEXT, digest TEXT, created REAL, sharing INTEGER, payload TEXT, UNIQUE(owner,idem));''')
        os.chmod(self.database, 0o600)

    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.database, timeout=10)
        try:
            with db:
                yield db
        finally:
            db.close()

    def session(self, token):
        now = time.time()
        with self.connect() as db:
            row = db.execute('SELECT csrf,touched FROM sessions WHERE id=?', (token,)).fetchone()
            if row and row[1] > now - 86400:
                db.execute('UPDATE sessions SET touched=? WHERE id=?', (now, token))
                return row[0]
        return None

    def new_session(self):
        token, csrf = secrets.token_urlsafe(32), secrets.token_urlsafe(32)
        with self.connect() as db:
            db.execute('INSERT INTO sessions VALUES (?,?,?)', (token, csrf, time.time()))
        return token, csrf


