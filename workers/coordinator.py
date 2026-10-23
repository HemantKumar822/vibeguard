"""Run separately: uv run python -m workers.coordinator. API never controls Docker."""
import secrets
import signal
import time
import threading
from backend.adapters.storage import Storage
from backend.core.settings import Settings
from backend.core.lifecycle import Lifecycle
from backend.core.cleanup import Cleanup
from workers.launcher import Launcher

def run_once(lifecycle, cleanup, token):
    if not lifecycle.lease(token):
        raise RuntimeError('Another coordinator holds the lease')
    # Recovery/deletion must stop daemon-side work before the next claim.
    stopped = threading.Event()
    lost = threading.Event()
    def heartbeat():
        while not stopped.wait(3):
            try:
                if not lifecycle.lease(token):
                    lost.set()
                    return
            except Exception:
                lost.set()
                return
    pulse = threading.Thread(target=heartbeat, daemon=True)
    pulse.start()
    try:
        cleanup.sweep()
    finally:
        stopped.set()
        pulse.join(timeout=5)
    if lost.is_set() or not lifecycle.lease(token):
        raise RuntimeError('Coordinator lease lost')
    scan=lifecycle.claim(token)
    if scan:
        lifecycle.unavailable(scan.scan_id,token)
        cleanup.sweep()
    return scan

def main():
    settings=Settings.environment()
    if settings is None: raise SystemExit('Private runtime configuration is required')
    store=Storage(settings); lifecycle=Lifecycle(store); launcher=Launcher()
    cleanup=Cleanup(store,launcher.stop); token=secrets.token_hex(16); running=True
    def shutdown(*_):
        nonlocal running
        running=False
    signal.signal(signal.SIGINT,shutdown); signal.signal(signal.SIGTERM,shutdown)
    try:
        while running:
            # Story 1.4 installs trusted adapters. Version probes never count
            # as coverage, so dispatch currently fails explicitly and safely.
            run_once(lifecycle,cleanup,token)
            time.sleep(1)
    finally:
        with store.connect() as db:
            db.execute('DELETE FROM coordinator WHERE token=?',(token,))

if __name__=='__main__': main()
