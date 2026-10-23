"""Tombstone-first cleanup; unsuccessful removal remains durable and blocks intake."""
import secrets
import shutil
import time
from backend.api.session import IntakeError
from backend.core.contracts import Deletion

class Cleanup:
    def __init__(self, store, stop=None):
        self.store, self.stop = store, stop

    def delete(self, scan_id, owner, internal=False):
        with self.store.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            row = db.execute('SELECT id FROM scans WHERE id=? AND owner=? AND (finished IS NULL OR finished>?)', (scan_id,owner,0 if internal else time.time()-86400)).fetchone()
            if not row: raise IntakeError(404,'not_found')
            existing = db.execute('SELECT id FROM deletions WHERE scan=?', (scan_id,)).fetchone()
            operation = existing[0] if existing else secrets.token_hex(16)
            db.execute('UPDATE scans SET tombstone=1 WHERE id=?', (scan_id,))
            db.execute("INSERT OR IGNORE INTO deletions VALUES (?,?,?,'pending',?)", (operation,scan_id,owner,time.time()))
        return self.operation(operation,owner)

    def operation(self, operation, owner):
        with self.store.connect() as db:
            row = db.execute('SELECT scan,status FROM deletions WHERE id=? AND owner=?', (operation,owner)).fetchone()
        if not row: raise IntakeError(404,'not_found')
        return Deletion(operation_id=operation,scan_id=row[0],status=row[1],error=dict(code='cleanup_failed',message='Cleanup is incomplete; the coordinator will retry.',request_id=operation,details={}) if row[1]=='failed' else None)

    def sweep(self):
        now=time.time()
        from backend.core.lifecycle import Lifecycle
        Lifecycle(self.store).expire_queue()
        with self.store.connect() as db:
            expired=db.execute('SELECT id,owner FROM scans WHERE tombstone=0 AND (finished<=? OR owner NOT IN (SELECT id FROM sessions WHERE touched>?))',(now-86400,now-86400)).fetchall()
        for scan_id,owner in expired: self.delete(scan_id,owner,internal=True)
        with self.store.connect() as db:
            rows=db.execute("SELECT id,scan,created,status FROM deletions WHERE status!='complete'").fetchall()
            terminal=db.execute("SELECT id FROM scans WHERE state IN ('complete','partial','failed') AND tombstone=0").fetchall()
        for operation,scan_id,created,previous in rows:
            status='failed'
            try:
                # Only the trusted coordinator supplies daemon-side cancellation.
                if self.stop is None:
                    status='failed' if now-created>=60 or previous=='failed' else 'pending'
                else:
                    self.stop(scan_id)
                    path=self.store.staging/scan_id
                    if path.exists(): shutil.rmtree(path)
                    status='complete'
            except Exception: pass
            with self.store.connect() as db:
                db.execute("UPDATE deletions SET status=? WHERE id=? AND status!='complete'",(status,operation))
                if status=='complete': db.execute("UPDATE scans SET payload='{}' WHERE id=?",(scan_id,))
        for (scan_id,) in terminal:
            try:
                path=self.store.staging/scan_id
                if self.stop is not None and path.exists():
                    self.stop(scan_id)
                    if path.exists(): shutil.rmtree(path)
            except Exception:
                self.delete(scan_id, self._owner(scan_id))

        # Staging names without a persisted admission are abandoned uploads.
        # Active uploads are bounded to 120s; allow a generous 600s grace.
        with self.store.connect() as db:
            known={row[0] for row in db.execute('SELECT id FROM scans')}
            db.execute('DELETE FROM sessions WHERE touched<=?',(now-86400,))
        healthy=True
        try:
            for path in self.store.staging.iterdir():
                if path.name not in known and path.stat().st_mtime <= now-600:
                    shutil.rmtree(path)
        except OSError:
            healthy=False
        with self.store.connect() as db:
            db.execute('UPDATE runtime_health SET cleanup_ok=?',(int(healthy),))
            # Only content-free tombstones survive until their retry-key TTL.
            db.execute("DELETE FROM deletions WHERE status='complete' AND scan IN (SELECT id FROM scans WHERE tombstone=1 AND created<=?)", (now-86400,))
            db.execute("DELETE FROM scans WHERE tombstone=1 AND created<=? AND NOT EXISTS (SELECT 1 FROM deletions WHERE scan=scans.id AND status!='complete')", (now-86400,))

    def _owner(self, scan_id):
        with self.store.connect() as db:
            return db.execute('SELECT owner FROM scans WHERE id=?',(scan_id,)).fetchone()[0]

