# Measured scanner acceptance

Controlled transport uses actual pinned workers with local acquisition fixtures. Live observations have no accuracy denominator.

| Transport | Mode | Variant | Status | Seconds | TP | FP | FN |
|---|---|---|---|---:|---:|---:|---:|
| controlled | codebase | vulnerable | complete | 11.813 | 4 | 0 | 0 |
| controlled | codebase | corrected | complete | 11.093 | 0 | 0 | 0 |
| controlled | codebase | clean | complete | 11.079 | 0 | 0 | 0 |
| controlled | repository | vulnerable | complete | 11.719 | 4 | 0 | 0 |
| controlled | repository | corrected | complete | 11.11 | 0 | 0 | 0 |
| controlled | repository | clean | complete | 11.562 | 0 | 0 | 0 |
| live | repository | observation | complete | 18.219 | — | — | — |
| live | website | observation | partial | 36.296 | — | — | — |
| controlled | website | vulnerable | complete | 22.203 | 5 | 2 | 0 |
| controlled | website | corrected | complete | 22.907 | 0 | 3 | 0 |
| controlled | website | clean | complete | 21.641 | 0 | 3 | 0 |

Remaining source directories: 0.

Release blockers (exit zero only means executed checks passed):

- Public labeled vulnerable/corrected deployments not available.
- Teammate prompt usefulness judgment unassessed.
- Live website capture remains partial due explicit exclusions.
- Unlabelled extra passive alerts retained as FP relative to selected labels; human adjudication pending.
- 200% browser zoom, reduced-motion emulation and complete rendered recovery/state matrix remain unassessed.
