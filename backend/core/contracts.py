"""Version-one public shapes. Validation is not scanner/network enforcement."""
from datetime import datetime
from pathlib import PurePosixPath
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, RootModel, field_validator, model_validator

Mode = Literal['codebase', 'repository', 'website']
ToolName = Literal['gitleaks', 'semgrep', 'zap', 'asset_secrets']
Classification = Literal['still_detected', 'not_detected', 'newly_detected', 'unverified']


class Contract(BaseModel):
    model_config = ConfigDict(extra='forbid')


class Health(Contract):
    status: Literal['ok']
    contract_version: Literal['v1']


class SafeError(Contract):
    code: str
    message: str
    request_id: str
    details: dict[str, str]


class ErrorResponse(Contract):
    error: SafeError


class AuthorizedInput(Contract):
    authorization_confirmed: Literal[True]
    allow_external_ai: bool = Field(strict=True)

    @field_validator('authorization_confirmed', mode='before')
    @classmethod
    def explicit_permission(cls, value):
        if value is not True:
            raise ValueError('Explicit boolean permission is required')
        return value


class RepositoryIntake(AuthorizedInput):
    mode: Literal['repository']
    repository_url: str
    ref: str | None = None


class WebsiteIntake(AuthorizedInput):
    mode: Literal['website']
    target_url: str


class Intake(RootModel[Annotated[RepositoryIntake | WebsiteIntake, Field(discriminator='mode')]]):
    """JSON admission shape; real URL/content validation belongs to intake adapters."""


class FileMapping(Contract):
    part_id: str
    relative_path: str


class CodebaseMetadata(AuthorizedInput):
    mode: Literal['codebase']
    files: list[FileMapping]


class InputIdentity(Contract):
    display_name: str
    revision: str | None
    repository: str | None
    target_redacted: str | None
    observation_id: str | None


class Exclusion(Contract):
    resource_key: str
    reason: str


class Coverage(Contract):
    required_count: int = Field(ge=0)
    completed_count: int = Field(ge=0)
    inspected: list[str]
    exclusions: list[Exclusion]
    rules_fingerprint: str | None
    revision_or_observation: str
    scope_complete: bool

    @model_validator(mode='after')
    def counts(self):
        if self.completed_count > self.required_count:
            raise ValueError('Completed coverage cannot exceed required coverage')
        if self.scope_complete and self.completed_count != self.required_count:
            raise ValueError('Complete scope requires all coverage checks complete')
        return self


class Tool(Contract):
    name: ToolName
    applicable: bool
    required: bool
    status: Literal['queued', 'running', 'complete', 'failed', 'timed_out', 'skipped']
    reason: str | None
    version: str | None
    rules_fingerprint: str | None
    started_at: datetime | None
    finished_at: datetime | None
    coverage: Coverage
    error: SafeError | None

    @model_validator(mode='after')
    def applicability(self):
        if self.status == 'skipped' and not (self.reason and self.reason.strip()):
            raise ValueError('Skipped tools require an explicit reason')
        if not self.applicable and (self.required or self.status != 'skipped' or self.reason != 'not_applicable'):
            raise ValueError('Nonapplicable tools must be explicitly skipped and not required')
        return self


class SourceLocation(Contract):
    kind: Literal['source']
    path: str
    line_start: int | None = Field(ge=1)
    line_end: int | None = Field(ge=1)

    @field_validator('path')
    @classmethod
    def relative_path(cls, value):
        if not value or '\\' in value or ':' in value or PurePosixPath(value).is_absolute() or '..' in PurePosixPath(value).parts:
            raise ValueError('Source location must use a safe relative POSIX path')
        return value

    @model_validator(mode='after')
    def line_order(self):
        if self.line_end is not None and (self.line_start is None or self.line_end < self.line_start):
            raise ValueError('Invalid source line range')
        return self


class WebLocation(Contract):
    kind: Literal['web']
    url_redacted: str
    resource_key: str
    part: Literal['header', 'response', 'asset', 'url']
    parameter_redacted: str | None
    line_start: int | None = Field(ge=1)


class Finding(Contract):
    id: str
    scanner: ToolName
    rule_id: str
    category: Literal['credential', 'unsafe_input', 'insecure_configuration', 'access_check', 'other']
    title: str
    severity: Literal['critical', 'high', 'medium', 'low', 'info']
    confidence: Literal['high', 'medium', 'needs_review']
    confidence_reason: str
    location: Annotated[SourceLocation | WebLocation, Field(discriminator='kind')]
    evidence_redacted: str | None
    explanation: str
    fix_guidance: str
    verification_steps: list[str]
    human_actions: list[str]
    match_context: str


class Repair(Contract):
    mode: Literal['ai_assisted', 'template']
    status: Literal['complete', 'fallback']
    prompt_redacted: str
    model_reason: str | None
    human_actions: list[str]


class Scan(Contract):
    contract_version: Literal['v1']
    scan_id: str
    baseline_id: str | None
    mode: Mode
    status: Literal['queued', 'running', 'complete', 'partial', 'failed']
    policy_id: str
    policy_fingerprint: str
    created_at: datetime
    started_at: datetime | None
    finished_at: datetime | None
    input: InputIdentity
    tools: list[Tool]
    coverage: Coverage
    findings: list[Finding]
    repair: Repair | None
    warnings: list[str]
    error: SafeError | None

    @model_validator(mode='after')
    def completion(self):
        expected = {'zap', 'asset_secrets'} if self.mode == 'website' else {'gitleaks', 'semgrep'}
        names = [t.name for t in self.tools]
        if len(set(names)) != len(names) or set(names) != {'gitleaks', 'semgrep', 'zap', 'asset_secrets'}:
            raise ValueError('All four tools must have one explicit applicability record')
        required = [t for t in self.tools if t.required]
        if {t.name for t in required} != expected or any(t.applicable != (t.name in expected) for t in self.tools):
            raise ValueError('Required tools do not match input mode')
        if self.coverage.required_count != len(required):
            raise ValueError('Required check count does not match tools')
        completed = sum(t.status == 'complete' and t.coverage.scope_complete for t in required)
        if self.coverage.completed_count != completed:
            raise ValueError('Completed count must reflect actual tools and scope')
        if self.status == 'complete' and (completed != len(required) or not self.coverage.scope_complete):
            raise ValueError('Complete scan requires all required checks and scope')
        if self.status in {'complete', 'partial', 'failed'} and (self.finished_at is None or self.repair is None):
            raise ValueError('Terminal scans require timestamp and deterministic repair guidance')
        if self.status in {'complete', 'partial', 'failed'} and any(t.status in {'queued', 'running'} for t in self.tools):
            raise ValueError('Terminal scans cannot retain nonterminal tools')
        return self


class ComparisonItem(Contract):
    baseline_finding_id: str | None
    new_finding_id: str | None
    status: Classification
    reason_code: str
    baseline_evidence_ref: str | None
    new_evidence_ref: str | None

    @model_validator(mode='after')
    def observed_identity(self):
        baseline, new = bool(self.baseline_finding_id), bool(self.new_finding_id)
        if not baseline and not new:
            raise ValueError('A comparison item requires an observed finding')
        expected = {'still_detected': (True, True), 'not_detected': (True, False), 'newly_detected': (False, True)}
        if self.status in expected and (baseline, new) != expected[self.status]:
            raise ValueError('Finding identities do not match comparison classification')
        if (baseline, new) != (bool(self.baseline_evidence_ref), bool(self.new_evidence_ref)):
            raise ValueError('Observed findings require corresponding evidence references')
        return self


class Comparison(Contract):
    baseline_id: str
    new_id: str
    status: Literal['comparable', 'partial']
    baseline_input: InputIdentity
    new_input: InputIdentity
    baseline_coverage: Coverage
    new_coverage: Coverage
    items: list[ComparisonItem]
    human_actions: list[str]


class Deletion(Contract):
    operation_id: str
    scan_id: str
    status: Literal['pending', 'complete', 'failed']
    error: SafeError | None

    @model_validator(mode='after')
    def failure_reason(self):
        if self.status == 'failed' and self.error is None:
            raise ValueError('Failed cleanup requires an explicit error')
        return self


PUBLIC_MODELS = [Health, Intake, CodebaseMetadata, Scan, Comparison, Deletion, ErrorResponse]
