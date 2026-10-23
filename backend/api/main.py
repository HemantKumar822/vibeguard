"""API v1: authorized source admission only; accepted scans remain queued."""
import json
import asyncio
from contextlib import asynccontextmanager, suppress
import re
import secrets
import shutil
import time
from threading import BoundedSemaphore
from datetime import datetime, timezone
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from pydantic.json_schema import models_json_schema
from backend.adapters.intake import receive
from backend.adapters.storage import Storage
from backend.api.session import IntakeError, owner
from backend.core.contracts import Health, PUBLIC_MODELS, Scan, SessionResponse, Capabilities, ErrorResponse, Deletion
from backend.core.policy import POLICY_ID, LIMITS, FINGERPRINT
from backend.core.settings import Settings
from backend.core.lifecycle import Lifecycle
from backend.core.cleanup import Cleanup


def queued_scan(scan_id, accepted, exclusions):
    coverage = dict(required_count=2, completed_count=0, inspected=[], exclusions=exclusions,
                    rules_fingerprint=None, revision_or_observation=scan_id, scope_complete=False)
    tools = []
    for name in ['gitleaks', 'semgrep', 'zap', 'asset_secrets']:
        applicable = name in {'gitleaks', 'semgrep'}
        tools.append(dict(name=name, applicable=applicable, required=applicable,
            status='queued' if applicable else 'skipped', reason=None if applicable else 'not_applicable',
            version=None, rules_fingerprint=None, started_at=None, finished_at=None, error=None,
            coverage={**coverage, 'required_count': 1 if applicable else 0}))
    return Scan(contract_version='v1', scan_id=scan_id, baseline_id=None, mode='codebase', status='queued',
        policy_id=POLICY_ID, policy_fingerprint=FINGERPRINT, created_at=datetime.now(timezone.utc),
        started_at=None, finished_at=None, input=dict(display_name='Submitted source tree', revision=None,
        repository=None, target_redacted=None, observation_id=None), tools=tools, coverage=coverage,
        findings=[], repair=None, warnings=['Accepted source inventory: ' + str(len(accepted)) + ' files. No scanner has run.',
        'Waiting for the trusted coordinator. Trusted source adapters are unavailable.'], error=None)


def create_app(settings=None):
    @asynccontextmanager
    async def lifespan(api):
        if api.state.storage:
            await asyncio.to_thread(Cleanup(api.state.storage).sweep)
        async def sweep():
            while True:
                if api.state.storage:
                    await asyncio.to_thread(Cleanup(api.state.storage).sweep)
                await asyncio.sleep(60)
        task=asyncio.create_task(sweep())
        try:
            yield
        finally:
            task.cancel()
            with suppress(asyncio.CancelledError): await task
    api = FastAPI(title='VibeGuard API', version='0.1.0', docs_url=None, redoc_url=None, lifespan=lifespan)
    settings = settings or Settings.environment()
    storage = Storage(settings.validate()) if settings else None
    api.state.storage = storage
    api.state.intake_guard = BoundedSemaphore(1)
    def runtime():
        if storage is None:
            raise IntakeError(503, 'runtime_unavailable')
        return storage
    @api.exception_handler(IntakeError)
    async def safe_error(request, exc):
        return JSONResponse(status_code=exc.status, content={'error': {'code': exc.code,
            'message': 'The request could not be accepted.', 'request_id': secrets.token_hex(8),
            'details': {exc.field: exc.code}}})
    @api.exception_handler(RequestValidationError)
    async def invalid_request(request, exc):
        return await safe_error(request, IntakeError(422, 'invalid_request'))
    @api.exception_handler(Exception)
    async def unavailable(request, exc):
        return await safe_error(request, IntakeError(503, 'runtime_unavailable'))
    @api.get('/api/v1/health', response_model=Health)
    def health():
        return Health(status='ok', contract_version='v1')
    errors = {code: {'model': ErrorResponse} for code in [400, 403, 404, 409, 413, 422, 429, 503]}
    origin_header = {'name': 'Origin', 'in': 'header', 'required': True, 'schema': {'type': 'string'}}
    @api.post('/api/v1/session', response_model=SessionResponse, responses=errors,
              openapi_extra={'parameters': [origin_header]})
    def session(request: Request):
        store = runtime()
        if request.headers.get('origin') != settings.origin:
            raise IntakeError(403, 'origin_not_allowed')
        token = request.cookies.get('vibeguard_session', '')
        csrf = store.session(token)
        if csrf is None:
            token, csrf = store.new_session()
        response = JSONResponse({'csrf_token': csrf})
        response.set_cookie('vibeguard_session', token, httponly=True, samesite='strict',
                            secure=not settings.loopback_http, max_age=86400, path='/api/v1')
        return response
    @api.get('/api/v1/capabilities', response_model=Capabilities, responses=errors)
    def capabilities(request: Request):
        owner(request, runtime(), settings)
        return dict(policy_id=POLICY_ID, policy_fingerprint=FINGERPRINT, permitted_modes=['codebase'],
                    limits=LIMITS, ai_available=False, unavailable_modes=['repository', 'website'])
    @api.post('/api/v1/scans', status_code=202, response_model=Scan, responses=errors,
        openapi_extra={'parameters': [origin_header, *[{'name': name, 'in': 'header', 'required': True,
            'schema': {'type': 'string'}} for name in ['X-CSRF-Token', 'Idempotency-Key']]],
            'requestBody': {'required': True, 'content': {'multipart/form-data': {'schema': {
            'type': 'object', 'required': ['metadata'], 'properties': {'metadata': {'type': 'string',
            'description': 'JSON CodebaseMetadata; additional named binary parts map each part_id exactly once.'}},
            'additionalProperties': {'type': 'string', 'format': 'binary'}}}}}})
    async def submit(request: Request):
        store = runtime()
        session_id = owner(request, store, settings, mutation=True)
        key = request.headers.get('idempotency-key', '')
        if not re.fullmatch(r'[A-Za-z0-9_-]{1,128}', key):
            raise IntakeError(422, 'idempotency_key_required', 'Idempotency-Key')
        if not api.state.intake_guard.acquire(blocking=False):
            raise IntakeError(429, 'intake_busy')
        directory = None
        published = False
        try:
            directory = store.staging / secrets.token_hex(16)
            directory.mkdir(mode=0o700)
            metadata, accepted, exclusions, digest = await receive(request, directory)
            scan = queued_scan(directory.name, accepted, exclusions)
            scan.accepted_files = accepted
            scan.allow_external_ai = metadata.allow_external_ai
            scan, published = Lifecycle(store).admit(scan, session_id, key, digest, metadata.allow_external_ai)
            return scan
        finally:
            try:
                if directory is not None and not published:
                    shutil.rmtree(directory)
            finally:
                api.state.intake_guard.release()
    @api.get('/api/v1/scans/{scan_id}', response_model=Scan, responses=errors)
    def read_scan(scan_id: str, request: Request):
        store = runtime()
        try:
            session_id = owner(request, store, settings)
        except IntakeError:
            raise IntakeError(404, 'not_found') from None
        return Lifecycle(store).read(scan_id, session_id)
    @api.delete('/api/v1/scans/{scan_id}', status_code=202, response_model=Deletion, responses=errors,
                openapi_extra={'parameters': [origin_header, {'name': 'X-CSRF-Token', 'in': 'header', 'required': True, 'schema': {'type': 'string'}}]})
    def delete_scan(scan_id: str, request: Request):
        store = runtime()
        try:
            session_id = owner(request, store, settings)
        except IntakeError:
            raise IntakeError(404, 'not_found') from None
        owner(request, store, settings, mutation=True)
        return Cleanup(store).delete(scan_id, session_id)
    @api.get('/api/v1/deletions/{operation_id}', response_model=Deletion, responses=errors)
    def read_deletion(operation_id: str, request: Request):
        store = runtime()
        try:
            session_id = owner(request, store, settings)
        except IntakeError:
            raise IntakeError(404, 'not_found') from None
        return Cleanup(store).operation(operation_id, session_id)
    @api.middleware('http')
    async def private_headers(request, call_next):
        response = await call_next(request)
        response.headers['Cache-Control'] = 'no-store'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        return response
    def contract_openapi():
        if api.openapi_schema is None:
            schema = get_openapi(title=api.title, version=api.version, routes=api.routes)
            _, definitions = models_json_schema([(model, 'validation') for model in PUBLIC_MODELS], ref_template='#/components/schemas/{model}')
            schema.setdefault('components', {}).setdefault('schemas', {}).update(definitions['$defs'])
            api.openapi_schema = schema
        return api.openapi_schema
    api.openapi = contract_openapi
    return api

app = create_app()

