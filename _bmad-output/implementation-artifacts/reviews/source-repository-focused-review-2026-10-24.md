# Focused source/repository review — 2026-10-24

Scope: batch `56270eeb4386b36da5a1f5171e7c5e1f34f6fb38..30fc01b`, plus corrections below. User requested one fast security/UI boundary review and push; broader independent review and rendered accessibility testing remain deferred. BMAD edge-case lens executed inline without review subagents.

Checked source report normalization/secret masking, fixed-provider public-IP/TLS/redirect/archive boundaries, lease/tombstone publication fencing, daemon-side cleanup and UI response lifetimes. No source code or credentials were sent to external models.

## Findings

```json
[
  {
    "lens": "edge-case-hunter",
    "location": "backend/adapters/intake.py:safe_paths",
    "trigger_condition": "A submitted filename contains a newer provider credential token format",
    "guard_snippet": "Reject github_pat_, sk-proj-, sk_live_ and ASIA credential-like paths before admission",
    "potential_consequence": "Credential-like filename values could appear in inventory, reports and repair prompts"
  },
  {
    "lens": "edge-case-hunter",
    "location": "frontend/src/SourceIntake.tsx:polling and remove",
    "trigger_condition": "An old polling or deletion response arrives after a new report is selected",
    "guard_snippet": "Ignore aborted polling responses; clear a deleted report only when its Scan ID matches",
    "potential_consequence": "The UI could discard a newly accepted report and obscure its reconnect identity"
  }
]
```

Both findings fixed. New filename regressions verify safe 422 responses, no reflected token, no stored Scan and empty staging. New asynchronous UI regression verifies that a stale 404 cannot clear the newer Scan. Existing polling/deletion, submission, retry, reconnect and repository rejection tests remain covered by the focused frontend run.

Verification: targeted unsafe/credential-filename Python cases; SourceIntake DOM tests; strict production build including fixture exclusion; frontend lint. Earlier batch tests and actual pinned scanner/public repository integration evidence remain in [the batch record](../source-repository-batch-verification.md). No full suite was restarted for this review.

No unresolved blocker found within this focused scope. Broader review, real rendered accessibility and later-mode acceptance remain pending. Both epics and all batch story issues remain open; pushing this branch does not close or merge them.
