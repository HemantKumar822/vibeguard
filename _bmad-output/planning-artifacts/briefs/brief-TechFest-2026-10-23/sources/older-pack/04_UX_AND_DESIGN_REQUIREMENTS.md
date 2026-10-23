# Visual Product Experience — Requirements, not a design system
Status: Interface behavior requirements. The team's forthcoming `DESIGN.md` owns visual design choices.

## Product principle
The user should understand the *state of their security review at a glance*, without a chat conversation. A contextual AI explanation is useful but secondary to evidence and workflow.

## Required screens
| Screen | Key interactions | Critical states |
|---|---|---|
| Project intake | Upload ZIP; show limits and validated project types | invalid ZIP, oversized, unsupported files |
| Scan progress | Scanner-by-scanner status, elapsed/finished indications | pending, running, completed, skipped, failed |
| Findings explorer | Severity and tool filters, category grouping, findings count | zero results, partial scan, false-positive caveat |
| Finding detail | File/line, redacted snippet, source rule, reason, copy fix guidance | missing snippet, unverified suspicion |
| Repair workflow | Consolidated copyable prompt with specific changes and test advice | AI unavailable (template fallback) |
| Rescan compare | Side-by-side counts and per-finding comparison | disappeared, persists, new, cannot verify |

## Non-negotiable interaction standards
- Use clear hierarchy, charts only when they encode real measurements, and meaningful scan-status visualization.
- Never use a fabricated numerical 'security score' or celebrate incomplete scans as safe.
- Support keyboard navigation, contrast, visible focus, text labels for icons and responsive layouts.
- Mask sensitive values everywhere (including copy actions).
- Give transparent progress and errors; never pretend a scanner ran.
- The same finding IDs should link progress, findings and rescan comparison.

## Design handoff
When the user supplies `DESIGN.md`, implement its palette, type scale, spacing, component language, interaction patterns and motion preferences. Keep requirements above stable unless the team explicitly revises them.
