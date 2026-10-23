"""Session authentication and stable, nonreflective errors."""
import secrets
from fastapi import Request

class IntakeError(Exception):
    def __init__(self, status, code, field='request'):
        self.status, self.code, self.field = status, code, field

def owner(request: Request, storage, settings, mutation=False):
    token = request.cookies.get('vibeguard_session', '')
    csrf = storage.session(token)
    if not csrf:
        raise IntakeError(403, 'session_required')
    if mutation and (request.headers.get('origin') != settings.origin or not secrets.compare_digest(request.headers.get('x-csrf-token', ''), csrf)):
        raise IntakeError(403, 'request_not_authorized')
    return token
