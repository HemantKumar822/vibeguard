---
title: 'Epic 4: grounded guidance and evidence-backed rescans'
type: feature
created: '2026-10-24'
status: done
route: dispatch
baseline_commit: c04dd6eab28d85b735b50132453468dd4e1ded3e
review_loop_iteration: 0
context:
  - D:/TechFest/docs/PROJECT_RULES.md
  - D:/TechFest/_bmad-output/implementation-artifacts/epic-4-context.md
---

<frozen-after-approval reason="human-owned intent">

## Intent

Deliver M4's complete repair-and-recheck workflow: optional grounded explanations, genuinely new same-mode scans, conservative comparisons and paired evidence. Implement stories 4.1, 4.2 and 4.3 as one batch in that order; broader verification runs once at the end.

## Boundaries & Constraints

Always reuse real source/repository/website admission and workers, ownership, CSRF, queue/deadline limits and tombstone fences. Preserve immutable baselines. Keep AI disabled by default; only server configuration plus explicit per-submission opt-in permits one request. A server-configured HTTPS provider adapter receives sanitized findings only: at most 30 findings, 24 KiB request, 8 KiB accepted response, 15 seconds total, no retries. Core validates existing IDs/locations and composes the master prompt. Provider failure, invalid output or overflow keeps deterministic guidance and all human rotation actions.

Never send raw source/vendor output, browser credentials or arbitrary environment data to AI. Models cannot run tools, invent findings, alter severity/location/IDs or change comparison status. No stale-result reuse, cross-mode clearing, secret-derived matching or verified-fixed label. Keep the current visual system and avoid unrelated earlier-epic rewrites. No deployment, provider charges, push or issue closure is included in this implementation batch.

## I/O & Edge-Case Matrix

| Scenario | Input/state | Expected behavior | Error/recovery |
|---|---|---|---|
| AI off/unconfigured | Any completed report | Zero external calls; complete deterministic prompt | Explicit template reason |
| AI opt-in | Bounded sanitized findings and valid existing-ID response | Accept explanations only; retain core guidance/actions | Reject invented IDs/locations, extra fields and malformed/secret-bearing text |
| AI failure/bounds | Timeout, oversized or invalid response, excess findings | One bounded call at most; deterministic fallback for affected/remainder | No lost findings/rotation advice |
| Real repeat | Owned terminal baseline plus authorized same-mode intake | New queued Scan, baseline_id, new snapshot/observation; real existing workers run | Idempotent retry returns same new Scan |
| Invalid repeat | Foreign/deleted/expired baseline, changed mode, nonterminal baseline | No accepted job | Nonrevealing 404 or 409 |
| Comparable evidence | Compatible policy/tool/rules and unique structural location | still_detected/not_detected/newly_detected with paired references | Line shifts alone do not imply repair |
| Uncertain evidence | Failed checks, missing resource, changed fingerprints, duplicate candidates or redacted URL collision | unverified and explicit reason; partial comparison | No absence claim without both scopes |
| UI repeat/recovery | Queued, terminal, disconnect or expired baseline | Baseline preserved; actual progress; labeled before/after and coverage | Deliberate reconnect/retry, stable focus, narrow stacking |

</frozen-after-approval>

## Code Map

- `backend/api/main.py`: reusable validated multipart/JSON submit path; add same-mode rescan and owned comparison routes without duplicating validators.
- `backend/core/lifecycle.py`: atomic admission/publish and existing replay; bind baseline ownership/mode/terminal state and lineage into admission/idempotency transaction.
- `backend/core/contracts.py`: existing Scan.baseline_id, Comparison and four classifications; preserve generated API contract.
- `backend/core/repair.py`, `workers/source.py`, `workers/website.py`: deterministic prompt and terminal report seam; add bounded opt-in explanation composition before publish.
- `backend/adapters/source.py`, `backend/adapters/web_report.py`: current match_context embeds line/index; derive conservative stable safe rule/location keys, never secret hashes or line-only identity.
- `frontend/src/SourceIntake.tsx`, `frontend/src/Report.tsx`: existing all-mode form, reconnect and polling; retain baseline when submitting repeat and display server comparison.
- `backend/core/website_readiness.py`: existing physical safety gate must remain authoritative for actual website repeats.

## Tasks & Acceptance

**Execution:**
- [x] `backend/adapters/explanations.py`, `backend/core/repair.py`, `.env.example`, worker terminal paths — implement server-configured bounded JSON explanation port, strict output acceptance, opt-in and truthful fallback; document provider compatibility.
- [x] `backend/core/comparison.py`, `backend/core/lifecycle.py` — conservative matching, per-tool coverage/version/image/rules/policy compatibility, direct lineage and retained baseline actions; ambiguous groups remain unverified.
- [x] `backend/api/main.py` — POST rescans and GET comparisons; share admission, enforce owner/same-mode/terminal baseline, bind baseline into retry digest and atomically recheck tombstone before admission.
- [x] `frontend/src/Comparison.tsx`, `frontend/src/SourceIntake.tsx`, `frontend/src/Report.tsx`, `frontend/src/index.css` — same-mode rescan entry, reset permission/sharing, preserve baseline report, actual progress, four labels/reasons, paired evidence/identities/coverage, keyboard selection and recovery.
- [x] `tests/test_explanations.py`, `tests/test_comparison.py`, `tests/test_rescans.py`, frontend comparison tests — cover every matrix row; inject provider failures without live billing and use real workers for labeled repeat smoke checks.
- [x] `contracts/openapi.json`, `frontend/src/generated/`, `docs/DEVELOPMENT.md`, story/sprint evidence — regenerate once after integration; record actual all-mode checks and any unavailable external runtime honestly.

**Acceptance Criteria:**
- Given sharing off or AI failure, when reports finish, then deterministic evidence and human actions remain usable without a mandatory provider.
- Given each supported baseline mode, when corrected input is admitted, then a new owned same-mode run executes and comparison never modifies the baseline.
- Given uncertain identity or incomplete coverage, when compared, then no unproven absence/repair claim appears.
- Given live repeat progress or failure, when using the workspace, then baseline and paired evidence stay accessible with explicit recovery.

## Implementation Notes

Investigation baseline: `c04dd6eab28d85b735b50132453468dd4e1ded3e`. Earlier review notes are preserved in named Git stashes; current teammates' completed source/website implementations take precedence. AI provider remains optional and unconfigured by default; live paid model calls are not required for deterministic completion.

## Spec Change Log

## Review Triage Log

| Finding | Verdict / evidence / resolution |
|---|---|
| Blind 1: stale reconnect comparison | high: old comparison survives identity switch; patch clear/fence identity state. |
| Blind 2: reconnect overwrites new admission | high: unresolved reconnect can replace newer accepted scan; patch generation guard. |
| Blind 3: comparison request lifetime | medium: effect has no timeout; patch bounded request/recovery. |
| Blind 4: New submission during repeat admission | medium: clears baseline while POST remains active; disable/fence pending action. |
| Blind 5: deletion leaves comparison | high: deleted scan classifications can survive reconnect; clear identity-owned state. |
| Blind 6: paired selection survives new identity | medium: selected index may exceed new result; key by comparison IDs. |
| Blind 7: baseline action expires mid-run | high: publication reads only live baseline, losing rotation reminders; snapshot actions at admission. |
| Blind 8: unsupported AI conclusions | high: free text can claim absence/invalid credentials despite denylist; constrain accepted grounded wording. |
| Blind 9: transport bound not tested | medium: injected functions bypass actual HTTPS adapter; add controlled blocked-connect/body/overflow tests. |
| Blind 10: unrelated source replacements match | high: every identifier/literal stripped, conflating distinct input expressions; sanitized structural identity and adapter regression. |
| Edge 1: stale reconnect comparison | high: same state-lifetime defect; clear and validate IDs. |
| Edge 2: rotation reminder prompt overflow | high: near-cap prompt silently omits baseline instructions; reserve space or explicit bounded fallback retaining actions. |
| Edge 3: invented AI prose locations | high: structured IDs validated but prose can invent source facts; constrained accepted wording. |
| Gaps 1: website identity cases absent | medium: tests use source fixtures only; add query collision/origin/resource tests. |
| Gaps 2: transport bounds absent | medium: same bypassed adapter verification; add actual adapter execution with controlled transport. |

## Verification

Use focused checks only for implementation failures. After all three stories integrate, run backend tests, frontend tests, generated contract parity, build and lint once. Run bounded real source/repository/website repeat smoke checks where runtime/authorized network fixtures are available; mocked boundary tests alone do not establish real-scanner acceptance. Apply review fixes and rerun affected checks only. Record unmet live acceptance separately from implemented/tested functionality.

## Final verification evidence

See [Epic 4 verification](epic-4-verification.md). Broad batch: 218 passed with only stale generated schema failure, resolved by regeneration and targeted parity check. Review patches: 44 backend and 19 frontend focused checks passed; final ambiguity, actual codebase repeat, and three UI race/consent checks passed. Build/lint/contracts and measured website readiness passed. No live paid provider or browser visual pass claimed. Remaining unknown source identifier context stays unverified intentionally. All post-review fixes completed directly after the user requested no more subagents.
