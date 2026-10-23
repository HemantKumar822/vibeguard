"""Bootstrap only: live health endpoint; no scanner/session/intake routes yet."""
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from pydantic.json_schema import models_json_schema

from backend.core.contracts import Health, PUBLIC_MODELS

app = FastAPI(title='VibeGuard API', version='0.1.0', docs_url=None, redoc_url=None)


@app.get('/api/v1/health', response_model=Health)
def health() -> Health:
    return Health(status='ok', contract_version='v1')


def contract_openapi():
    if app.openapi_schema is None:
        schema = get_openapi(title=app.title, version=app.version, routes=app.routes)
        _, definitions = models_json_schema(
            [(model, 'validation') for model in PUBLIC_MODELS],
            ref_template='#/components/schemas/{model}')
        schema.setdefault('components', {}).setdefault('schemas', {}).update(definitions['$defs'])
        app.openapi_schema = schema
    return app.openapi_schema


app.openapi = contract_openapi
