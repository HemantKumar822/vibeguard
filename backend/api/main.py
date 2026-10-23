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
from backend.adapters.repository import identity, retrieve, request_digest
from backend.adapters.storage import Storage
from backend.adapters.explanations import configuration as ai_configuration
from backend.api.session import IntakeError, owner
from backend.core.contracts import Health, PUBLIC_MODELS, Scan, SessionResponse, Capabilities, ErrorResponse, Deletion, Intake, Comparison
from backend.adapters.web_capture import target as website_target, display as website_display, LIMITS as WEB_LIMITS, CaptureError
from backend.core.website_readiness import ready as website_ready
from pydantic import ValidationError
from backend.core.policy import POLICY_ID, LIMITS, FINGERPRINT
from backend.core.settings import Settings
from backend.core.lifecycle import Lifecycle
from backend.core.cleanup import Cleanup


def bound_digest(digest, baseline_id):
    import hashlib
    return hashlib.sha256((digest+':baseline:'+baseline_id).encode()).hexdigest() if baseline_id else digest


def queued_scan(scan_id, accepted, exclusions, mode='codebase'):
    coverage = dict(required_count=2, completed_count=0, inspected=[], exclusions=exclusions,
                    rules_fingerprint=None, revision_or_observation=scan_id, scope_complete=False)
    tools = []
    for name in ['gitleaks', 'semgrep', 'zap', 'asset_secrets']:
        applicable = name in ({'zap','asset_secrets'} if mode=='website' else {'gitleaks', 'semgrep'})
        tools.append(dict(name=name, applicable=applicable, required=applicable,
            status='queued' if applicable else 'skipped', reason=None if applicable else 'not_applicable',
            version=None, rules_fingerprint=None, started_at=None, finished_at=None, error=None,
            coverage={**coverage, 'required_count': 1 if applicable else 0}))
    return Scan(contract_version='v1', scan_id=scan_id, baseline_id=None, mode=mode, status='queued',
        policy_id=POLICY_ID, policy_fingerprint=FINGERPRINT, created_at=datetime.now(timezone.utc),
        started_at=None, finished_at=None, input=dict(display_name='Submitted source tree', revision=None,
        repository=None, target_redacted=None, observation_id=None), tools=tools, coverage=coverage,
        findings=[], repair=None, warnings=['Accepted source inventory: ' + str(len(accepted)) + ' files. No scanner has run.',
        'Waiting for the trusted coordinator. No required check has completed.'], error=None)


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
        enabled=website_ready()
        return dict(policy_id=POLICY_ID, policy_fingerprint=FINGERPRINT, permitted_modes=['codebase', 'repository']+(['website'] if enabled else []),
                    limits={**LIMITS,**{'website_'+key:value for key,value in WEB_LIMITS.items()}}, ai_available=ai_configuration() is not None, unavailable_modes=[] if enabled else ['website'])
    @api.post('/api/v1/scans', status_code=202, response_model=Scan, responses=errors,
        openapi_extra={'parameters': [origin_header, *[{'name': name, 'in': 'header', 'required': True,
            'schema': {'type': 'string'}} for name in ['X-CSRF-Token', 'Idempotency-Key']]],
            'requestBody': {'required': True, 'content': {'application/json': {'schema': {'$ref':'#/components/schemas/Intake'}}, 'multipart/form-data': {'schema': {
            'type': 'object', 'required': ['metadata'], 'properties': {'metadata': {'type': 'string',
            'description': 'JSON CodebaseMetadata; additional named binary parts map each part_id exactly once.'}},
            'additionalProperties': {'type': 'string', 'format': 'binary'}}}}}})
    async def submit(request: Request):
        return await submit_intake(request)

    async def submit_intake(request: Request, baseline_id: str | None = None):
        store = runtime()
        session_id = owner(request, store, settings, mutation=True)
        baseline = Lifecycle(store).read(baseline_id, session_id) if baseline_id else None
        if baseline and baseline.status not in {'complete','partial','failed'}: raise IntakeError(409,'baseline_not_terminal')
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
            repository=None
            website=None
            if request.headers.get('content-type','').split(';')[0].strip()=='application/json':
                body=bytearray()
                async with asyncio.timeout(15):
                    async for chunk in request.stream():
                        body.extend(chunk)
                        if len(body)>8192: raise IntakeError(413,'metadata_too_large')
                try:
                    metadata=Intake.model_validate_json(body).root
                except (ValueError,ValidationError):
                    raise IntakeError(422,'invalid_repository_submission') from None
                if metadata.mode=='repository':
                    identity(metadata.repository_url,metadata.ref)
                else:
                    if not website_ready(): raise IntakeError(503,'website_safety_unverified')
                    try: website=website_target(metadata.target_url)
                    except CaptureError: raise IntakeError(422,'invalid_website_target','target_url') from None
                if baseline and baseline.mode!=metadata.mode: raise IntakeError(409,"rescan_mode_mismatch")
                digest=bound_digest(request_digest(metadata),baseline_id)
                existing=Lifecycle(store).existing(session_id,key,digest)
                if existing: return existing
                if website:
                    accepted,exclusions=[],[]
                    (directory/'website.json').write_text(json.dumps({'target_url':website}),encoding='utf-8')
                else:
                    retrieval=asyncio.create_task(asyncio.to_thread(retrieve,metadata,directory))
                    try:
                        accepted,exclusions,repository,requested,commit=await asyncio.shield(retrieval)
                    except asyncio.CancelledError:
                        # Do not remove private scratch while the bounded retrieval thread still writes it.
                        with suppress(Exception): await retrieval
                        raise
            else:
                metadata, accepted, exclusions, digest = await receive(request, directory)
            if baseline and baseline.mode!=metadata.mode: raise IntakeError(409,"rescan_mode_mismatch")
            if metadata.mode=="codebase": digest=bound_digest(digest,baseline_id)
            scan = queued_scan(directory.name, accepted, exclusions,'website' if website else 'codebase')
            if website:
                scan.input.display_name='Authorized website review'
                scan.input.target_redacted=website_display(website)
                scan.input.observation_id=scan.scan_id
                scan.warnings=['Website accepted. No response has been fetched or check completed.',
                               'Waiting for bounded passive capture; browser JavaScript and private backend source are outside scope.']
            if repository:
                scan.mode='repository'
                scan.input.repository=repository
                scan.input.display_name=repository.removeprefix('https://github.com/')
                scan.input.revision=commit
                scan.input.requested_ref=requested
                scan.coverage.revision_or_observation=commit
                for tool in scan.tools: tool.coverage.revision_or_observation=commit
            scan.baseline_id = baseline_id
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
    @api.post('/api/v1/scans/{scan_id}/rescans', status_code=202, response_model=Scan, responses=errors,
              openapi_extra={'parameters': [origin_header, *[{'name': name, 'in': 'header', 'required': True, 'schema': {'type': 'string'}} for name in ['X-CSRF-Token','Idempotency-Key']]],
                            'requestBody': {'required': True, 'content': {'application/json': {'schema': {'$ref':'#/components/schemas/Intake'}}, 'multipart/form-data': {'schema': {'type':'object','required':['metadata'],'properties':{'metadata':{'type':'string'}},'additionalProperties':{'type':'string','format':'binary'}}}}}})
    async def rescan(scan_id: str, request: Request):
        return await submit_intake(request, scan_id)

    @api.get('/api/v1/scans/{baseline_id}/comparisons/{new_id}', response_model=Comparison, responses=errors)
    def comparison(baseline_id: str, new_id: str, request: Request):
        store=runtime()
        try: session_id=owner(request,store,settings)
        except IntakeError: raise IntakeError(404,'not_found') from None
        return Lifecycle(store).compare(baseline_id,new_id,session_id)

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

