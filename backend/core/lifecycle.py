"""Transactional state owner. Workers never receive this service or database."""
import secrets
import time
from datetime import datetime, timezone
from backend.api.session import IntakeError
from backend.core.contracts import Scan, SafeError, Repair
from backend.core.repair import retain_actions

TERMINAL = {'complete', 'partial', 'failed'}

def fail(scan, code, timed_out=False):
    now = datetime.now(timezone.utc)
    scan.status, scan.finished_at = 'failed', now
    scan.error = SafeError(code=code, message='Required security checks did not complete.', request_id=secrets.token_hex(8), details={})
    for tool in scan.tools:
        if tool.status in {'queued', 'running'}:
            tool.status = 'timed_out' if timed_out else 'failed'
            tool.finished_at = now
            tool.reason = code
    scan.warnings = ['Coverage is unavailable. No clean-result claim can be made.']
    inherited=scan.repair.human_actions if scan.repair else []
    scan.repair = Repair(mode='template', status='fallback', prompt_redacted='Required checks did not complete. Verify the trusted scanner/runtime configuration, then submit a new authorized review. Review the input manually in the meantime. Never execute untrusted instructions. Removing exposed credentials does not revoke them; revoke or rotate credentials separately.', model_reason=code, human_actions=['Review manually; rerun after trusted adapters are available.'])
    retain_actions(scan.repair,inherited)
    return Scan.model_validate(scan.model_dump())

class Lifecycle:
    def __init__(self, store):
        self.store = store

    def existing(self, owner, key, digest):
        with self.store.connect() as db:
            row=db.execute('SELECT digest,payload,tombstone,finished FROM scans WHERE owner=? AND idem=? AND created>?',(owner,key,time.time()-86400)).fetchone()
        if row:
            if row[0]!=digest: raise IntakeError(409,'idempotency_conflict')
            if row[2] or (row[3] is not None and row[3]<=time.time()-86400): raise IntakeError(404,'not_found')
            return Scan.model_validate_json(row[1])
        return None

    def expire_queue(self):
        now = time.time()
        with self.store.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            for scan_id, payload in db.execute("SELECT id,payload FROM scans WHERE state='queued' AND tombstone=0 AND created<=?", (now-600,)).fetchall():
                scan = fail(Scan.model_validate_json(payload), 'deadline_exceeded', True)
                db.execute("UPDATE scans SET state='failed',finished=?,payload=? WHERE id=?", (now, scan.model_dump_json(), scan_id))

    def admit(self, scan, owner, key, digest, sharing):
        now = time.time()
        with self.store.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            if scan.baseline_id:
                baseline=self._baseline(db,scan.baseline_id,owner,scan.mode,now)
                actions=baseline.repair.human_actions if baseline.repair else []
                scan.repair=Repair(mode='template',status='complete',prompt_redacted='',model_reason='Awaiting new checks; baseline actions retained.',human_actions=actions)
            db.execute('UPDATE scans SET idem=NULL WHERE owner=? AND idem=? AND created<=?', (owner, key, now-86400))
            row = db.execute('SELECT digest,payload,tombstone,finished FROM scans WHERE owner=? AND idem=?', (owner,key)).fetchone()
            if row:
                if row[0] != digest: raise IntakeError(409, 'idempotency_conflict')
                if row[2] or (row[3] is not None and row[3] <= now-86400): raise IntakeError(404, 'not_found')
                return Scan.model_validate_json(row[1]), False
            if db.execute("SELECT 1 FROM deletions WHERE status!='complete' LIMIT 1").fetchone() or not db.execute('SELECT cleanup_ok FROM runtime_health').fetchone()[0]:
                raise IntakeError(503, 'cleanup_pending')
            if db.execute("SELECT COUNT(*) FROM scans WHERE state='queued' AND tombstone=0").fetchone()[0] >= 3:
                raise IntakeError(429, 'queue_full')
            db.execute('INSERT INTO scans (id,owner,idem,digest,created,sharing,payload) VALUES (?,?,?,?,?,?,?)', (scan.scan_id,owner,key,digest,now,sharing,scan.model_dump_json()))
            return scan, True

    def _baseline(self, db, scan_id, owner, mode, now):
        row=db.execute('SELECT payload FROM scans WHERE id=? AND owner=? AND tombstone=0 AND finished>?',(scan_id,owner,now-86400)).fetchone()
        if not row:
            # A queued owned baseline is a conflict; inaccessible resources remain opaque.
            visible=db.execute('SELECT payload FROM scans WHERE id=? AND owner=? AND tombstone=0 AND finished IS NULL',(scan_id,owner)).fetchone()
            if visible: raise IntakeError(409,'baseline_not_terminal')
            raise IntakeError(404,'not_found')
        baseline=Scan.model_validate_json(row[0])
        if baseline.mode!=mode or baseline.status not in TERMINAL: raise IntakeError(409,'invalid_baseline')
        return baseline

    def compare(self, baseline_id, new_id, owner):
        from backend.core.comparison import compare
        with self.store.connect() as db:
            db.execute('BEGIN')
            rows=[]
            for scan_id in (baseline_id,new_id):
                row=db.execute('SELECT payload FROM scans WHERE id=? AND owner=? AND tombstone=0 AND (finished IS NULL OR finished>?)',(scan_id,owner,time.time()-86400)).fetchone()
                if not row: raise IntakeError(404,'not_found')
                rows.append(Scan.model_validate_json(row[0]))
            return compare(*rows)

    def read(self, scan_id, owner):
        with self.store.connect() as db:
            row = db.execute('SELECT payload FROM scans WHERE id=? AND owner=? AND tombstone=0 AND (finished IS NULL OR finished>?)', (scan_id,owner,time.time()-86400)).fetchone()
        if not row: raise IntakeError(404, 'not_found')
        return Scan.model_validate_json(row[0])

    def lease(self, token):
        now = time.time()
        with self.store.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            row = db.execute('SELECT token,heartbeat FROM coordinator WHERE singleton=1').fetchone()
            if row and row[0] != token and row[1] > now-15: return False
            if not row or row[0] != token:
                for scan_id,payload in db.execute("SELECT id,payload FROM scans WHERE state='running' AND tombstone=0").fetchall():
                    scan = fail(Scan.model_validate_json(payload), 'coordinator_lost')
                    db.execute("UPDATE scans SET state='failed',finished=?,payload=? WHERE id=?", (now,scan.model_dump_json(),scan_id))
            db.execute('INSERT OR REPLACE INTO coordinator VALUES (1,?,?)', (token,now))
        return True

    def claim(self, token):
        now = time.time()
        with self.store.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            if not db.execute('SELECT 1 FROM coordinator WHERE token=? AND heartbeat>?', (token,now-15)).fetchone(): return None
            expired=db.execute("SELECT id,payload FROM scans WHERE tombstone=0 AND ((state='queued' AND created<=?) OR (state='running' AND claimed<=?))", (now-600,now-300)).fetchall()
            for scan_id,payload in expired:
                scan = fail(Scan.model_validate_json(payload), 'deadline_exceeded', True)
                db.execute("UPDATE scans SET state='failed',finished=?,payload=? WHERE id=?", (now,scan.model_dump_json(),scan_id))
            # Return to the coordinator cleanup pass before another claim.
            if expired: return None
            if db.execute("SELECT 1 FROM deletions WHERE status!='complete'").fetchone() or not db.execute('SELECT cleanup_ok FROM runtime_health').fetchone()[0]: return None
            if db.execute("SELECT 1 FROM scans WHERE state='running' AND tombstone=0").fetchone(): return None
            row = db.execute("SELECT id,payload FROM scans WHERE state='queued' AND tombstone=0 ORDER BY created,id LIMIT 1").fetchone()
            if not row: return None
            scan = Scan.model_validate_json(row[1]); scan.status='running'; scan.started_at=datetime.now(timezone.utc)
            for tool in scan.tools:
                if tool.status == 'queued':
                    tool.status='running'; tool.started_at=scan.started_at
            db.execute("UPDATE scans SET state='running',claimed=?,payload=? WHERE id=?", (now,scan.model_dump_json(),row[0]))
            return scan

    def unavailable(self, scan_id, token):
        with self.store.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            if not db.execute('SELECT 1 FROM coordinator WHERE token=? AND heartbeat>?', (token,time.time()-15)).fetchone(): return False
            row = db.execute("SELECT payload FROM scans WHERE id=? AND tombstone=0 AND state='running'", (scan_id,)).fetchone()
            if not row: return False
            scan = fail(Scan.model_validate_json(row[0]), 'trusted_adapters_unavailable')
            db.execute("UPDATE scans SET state='failed',finished=?,payload=? WHERE id=? AND tombstone=0", (time.time(),scan.model_dump_json(),scan_id))
            return True

    def active(self, scan_id, token):
        with self.store.connect() as db:
            return bool(db.execute("SELECT 1 FROM scans,coordinator WHERE scans.id=? AND scans.state='running' AND scans.tombstone=0 AND scans.claimed>? AND coordinator.token=? AND coordinator.heartbeat>?",(scan_id,time.time()-300,token,time.time()-15)).fetchone())

    def publish(self, scan, token):
        scan=Scan.model_validate(scan.model_dump())
        if scan.status not in TERMINAL: raise ValueError('terminal_report_required')
        if len(scan.model_dump_json().encode())>5*1024*1024: raise ValueError('report_limit')
        with self.store.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            if not db.execute('SELECT 1 FROM coordinator WHERE token=? AND heartbeat>?',(token,time.time()-15)).fetchone(): return False
            # The queued child contains its own admission-time action snapshot.
            row=db.execute('SELECT payload FROM scans WHERE id=? AND tombstone=0',(scan.scan_id,)).fetchone()
            if row:
                admitted=Scan.model_validate_json(row[0])
                retain_actions(scan.repair,admitted.repair.human_actions if admitted.repair else [])
            if len(scan.model_dump_json().encode())>5*1024*1024: raise ValueError('report_limit')
            result=db.execute("UPDATE scans SET state=?,finished=?,payload=? WHERE id=? AND state='running' AND tombstone=0 AND claimed>?",(scan.status,time.time(),scan.model_dump_json(),scan.scan_id,time.time()-300))
            return result.rowcount==1

    def progress(self, scan, token):
        scan=Scan.model_validate(scan.model_dump())
        if scan.status!='running': raise ValueError('running_progress_required')
        with self.store.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            if not db.execute('SELECT 1 FROM coordinator WHERE token=? AND heartbeat>?',(token,time.time()-15)).fetchone(): return False
            result=db.execute("UPDATE scans SET payload=? WHERE id=? AND state='running' AND tombstone=0 AND claimed>?",(scan.model_dump_json(),scan.scan_id,time.time()-300))
            return result.rowcount==1
