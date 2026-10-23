# Team delivery guide

[Milestones](https://github.com/HemantKumar822/vibeguard/milestones) · [Issues](https://github.com/HemantKumar822/vibeguard/issues) · [Exact issue and milestone identities](../_bmad-output/github-issues/publication.json)

## How work is organized

An epic is a parent issue with native story sub-issues and an `epic:N` label. A milestone groups that epic and its stories around a demonstrable delivery outcome. Check the milestone's open/closed story counts together with the epic's sub-issue progress; the parent epic is also counted as an issue. Close a story only after its acceptance and verification pass; close the epic after all its stories and the epic outcome pass.

| Milestone | Epic | Delivery outcome |
| --- | --- | --- |
| [M1 — Safe source review](https://github.com/HemantKumar822/vibeguard/milestone/1) | 1 | Source intake, isolated jobs, real masked findings and repair prompt |
| [M2 — Repository review](https://github.com/HemantKumar822/vibeguard/milestone/2) | 2 | Resolved public GitHub revision reviewed in the same workspace |
| [M3 — Website review with OWASP ZAP](https://github.com/HemantKumar822/vibeguard/milestone/3) | 3 | Controlled networking, ZAP observations and visible-asset secrets |
| [M4 — Repair guidance and real rescans](https://github.com/HemantKumar822/vibeguard/milestone/4) | 4 | Grounded opt-in AI, real repeat checks and honest paired evidence |
| [M5 — Validated hackathon demo](https://github.com/HemantKumar822/vibeguard/milestone/5) | 5 | Actual acceptance evidence, accessible recovery and rehearsed demo |

Milestone numbers describe outcomes, not a requirement to finish each whole milestone before starting the next. M2 and M3 can overlap once their story prerequisites are met. AI Story 4.1 can start after 1.5; comparison UI does not depend on AI. No due dates or person assignments have been invented.

## Parallel work and dependencies

All issues are open and have no native blocking relationships. Stories remain native sub-issues of their epic and belong to the matching milestone. GitHub also shows sub-issues in the main issue list; that does not mean they are outside their epic.

Dependencies remain in issue descriptions as coordination guidance. The team can work in parallel by agreeing shared API contracts, fixtures and ownership. Preserve required integration and acceptance checks before closing a story; open access does not remove technical dependencies.

[Story 1.1](https://github.com/HemantKumar822/vibeguard/issues/6) is the recommended foundation. Source, repository, website and UI work can be coordinated across teammates using the documented boundaries. Choose one accountable owner per active story and use reviewed pull requests.
