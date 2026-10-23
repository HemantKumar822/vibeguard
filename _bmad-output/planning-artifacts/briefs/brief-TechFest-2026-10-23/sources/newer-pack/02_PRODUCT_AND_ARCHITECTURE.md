# 02 — Product and Modular Architecture

**Goal:** a real visual application, **not a chat interface with scanner text**.

**Frontend behavior reference:** [`04_FRONTEND_UX.md`](04_FRONTEND_UX.md). `DESIGN.md` remains the visual style source of truth.

## One bounded pipeline

```text
React / TypeScript graphical UI
        │  ZIP upload, status polling, findings, compare
        ▼
FastAPI — validation, scan jobs, reports
        ▼
Safe ZIP extraction + simple project inventory
        ▼
Restricted scan coordinator (fixed commands, timeouts)
        ├─────────┬──────────┐
        ▼         ▼          │
     Gitleaks   Semgrep      │ per-tool success/failure
        └─────────┬──────────┘
                  ▼
Normalize + sanitize findings + preserve evidence/coverage
                  ▼
ONE AI review call on redacted structured evidence
                  ▼
Report + consolidated repair prompt
                  ▼
Corrected ZIP → same checks → honest before/after comparison
```

No complex autonomous agent runtime. The coordinator selects and runs **preapproved tools**; the AI explains results and writes repair instructions only.

## Module boundaries

| Module | Responsibility | Key rule |
| --- | --- | --- |
| `intake` | ZIP size/file-count limits, safe extraction, project inventory | Reject traversal, symlinks and hostile archives; never execute upload |
| `coordinator` | Job IDs, restricted scanner execution, deadlines and tool outcomes | No AI-generated shell commands; do not hide tool failures |
| `adapters` | Call Gitleaks/Semgrep; interpret JSON, exit codes and rule IDs | Preserve original evidence but never publish raw secrets |
| `findings` | Consistent records, redaction, deduplication, risk/confidence labels | Retain source, line, scanner rule and coverage |
| `ai_review` | Explain evidence; generate **one** actionable repair prompt | Only bounded sanitized data; do not invent findings |
| `compare` | Match findings and coverage across scans | `not_detected` is not automatically `verified_fixed` |
| `frontend` | Visual workflow and all user interactions | Rendering cannot conceal errors or fake a security score |

A simple local temporary store + SQLite metadata is enough for the demo. A bounded worker and status polling are enough; no large task queue or WebSocket infrastructure required initially.

## Contract to agree before parallel coding

```json
{
  "scan_id": "scan-001",
  "status": "complete",
  "tools": {
    "gitleaks": {"status": "complete", "version": "pinned-version"},
    "semgrep": {"status": "complete", "version": "pinned-version"}
  },
  "findings": [
    {
      "id": "candidate-id",
      "scanner": "semgrep",
      "rule_id": "security-rule-name",
      "title": "Potential unsafe input handling",
      "severity": "medium",
      "confidence": "needs_review",
      "path": "src/api/example.ts",
      "line": 42,
      "evidence_redacted": "Untrusted input reaches a sensitive operation",
      "explanation": "...",
      "repair": "...",
      "human_action": null
    }
  ],
  "repair_prompt": "..."
}
```

`tools.*.status`: `queued`, `running`, `complete`, `failed`, `skipped` or `timed_out`. Overall `status`: `running`, `complete`, `partial`, `failed`. **Zero findings and a failed scan are never the same.** Use actual versions in running builds; example version text above is a placeholder.

### Minimal proposed endpoints

- `POST /scans` — accept valid ZIP, create run and return `scan_id`.
- `GET /scans/{id}` — status, tool states and report when available.
- `POST /scans/{id}/rescan` — accept corrected ZIP and link it to baseline.
- `GET /scans/{baseline_id}/compare/{new_id}` — comparison and coverage.

Keep scanner-level JSON as implementation detail; frontend consumes the normalized contract. Prepare mock responses early so frontend and scanner work proceed simultaneously.

## Rescan semantics

| State | Meaning |
| --- | --- |
| `still_detected` | Corresponding finding appears in both comparable scans |
| `not_detected` | Finding absent on a completed comparable repeat scan; not proof of exploit removal |
| `newly_detected` | Found in the second comparable scan only |
| `unverified` | Tool error, missing coverage, changed rules or uncertain matching |
| `verified_fixed` | Use only if an appropriate repeatable behavior test actually confirms repair (not necessary in MVP) |

Matching should use rule, normalized path and safe source context, not line number alone or a hash exposing secret contents. Track scanner versions and rule-set versions; changes may invalidate comparisons.

## One strong graphical UX (styling from your `DESIGN.md`)

This can be **one cohesive workspace with three states**, rather than six separate pages:

1. **Submission + live progress:** Drop ZIP, show recognized project and a visual two-scanner pipeline with real running/completed/failed states.
2. **Findings + repair:** Severity overview, filters, issue cards, selected finding details with masked source evidence, code location, impact and a contextual copyable master repair prompt.
3. **Before/after:** Side-by-side findings and completed-check coverage; show remaining, new, not detected and unverified; manual credential rotation stays visible.

The detailed UI requirements, interactive states and acceptance criteria are in [`04_FRONTEND_UX.md`](04_FRONTEND_UX.md). The UI must handle loading, empty, error and smaller-screen states, keyboard focus and readable contrast. **No imaginary health score** and no chat-first product. `DESIGN.md` is the single source of truth for type, palette, spacing, visual system and motion when the team supplies it.

## LLM and secret boundaries

- Read uploaded files as **untrusted data**, not instructions for the AI.
- Prepare *small relevant evidence*, redact suspected secrets **before** persistence, logging, UI rendering or model calls. A redactor is not a mathematically perfect guarantee; do not claim zero possible leakage.
- AI must refer to supplied source locations and scanner rules, explain confidence, and avoid fabricating line numbers or verified exploitability.
- Have a deterministic fallback repair prompt so an unavailable model doesn't break the demo.
- For real leaked keys, include a separate **manual revoke/rotate** instruction. Never paste a redacted placeholder as a credential value.

## Suggested repo shape (guidance only)

```text
frontend/             React + TypeScript UI
backend/api/          FastAPI endpoints
backend/core/         jobs, findings and comparison
backend/scanners/     Gitleaks + Semgrep adapters
backend/security/     intake, worker policy, redaction
backend/ai/           explanation/prompt + fallback
fixtures/             vulnerable / corrected / clean samples
```

BMAD can turn these modules into epics and story dependencies. These reference docs intentionally contain **no pre-generated backlog**.
