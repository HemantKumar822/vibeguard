---
title: Clear scan activity workspace
type: feature
created: '2026-10-24'
status: in-progress
route: oneshot
---

<frozen-after-approval>
## Intent
Make the security review workspace less cluttered and easier to follow, with real check-by-check progress and a timestamped activity view. Use the existing sanitized scan snapshots; never simulate rule execution, percentages, or raw scanner logs. User expanded scope: wire the existing optional AI adapter to Groq and add downloadable reports with repair guidance. Preserve source/repository/website intake, consent, reconnect, evidence, repair and rescan actions. Run only lightweight focused checks as requested.
</frozen-after-approval>

## Implementation Notes
- Small frontend-only change: App, SourceIntake, Report, new ScanActivity, shared CSS and focused component tests. No contract or scanner changes required.
- Reuse backend tool statuses, timestamps, applicability and coverage. Queued tools are waiting, not passed. Completion of execution and completeness of coverage are distinct.
- Design: slate background #101722, panel #17212e, border #344354, muted #aab8c8, blue #b6d9ff, green #b4ddc9. Bahnschrift restrained headings, Segoe UI body, Consolas event data. Compact header → input disclosure → checks → evidence. Signature is a quiet chronological execution ledger, not a simulated terminal.
- Remove redundant large introductory blocks and repeated scope presentation. Keep secondary options and technical detail discoverable through native disclosures. Existing safety and accessibility requirements from EXPERIENCE.md remain applicable.
- Validation: focused React checks, TypeScript, lint; no backend/Docker/full acceptance reruns.

- User explicitly expanded the intent during implementation to Groq configuration and report generation. Keep existing grounded AI validation and template fallback; implement the provider wire format only. Add a Markdown report download from sanitized data.
