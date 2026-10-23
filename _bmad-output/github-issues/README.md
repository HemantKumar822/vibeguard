# Team story board

**5 epics · 16 prepared stories · implementation not started.**

Each story explains the outcome, scope, requirements, dependencies, acceptance and verification. Only Story 1.1 is initially unblocked. `ready-for-dev` means its handoff exists; it does not mean its prerequisites are complete.

## Stories and dependencies

| Story | Proposed owner role | Blocked by | Unblocks |
| --- | --- | --- | --- |
| [1.1 · Set up initial project from starter template and freeze contracts](../implementation-artifacts/1-1-set-up-initial-project-from-starter-template-and-freeze-contracts.md) | Full-stack / platform | None — start here | 1.2 |
| [1.2 · Accept an authorized bounded source tree](../implementation-artifacts/1-2-accept-an-authorized-bounded-source-tree.md) | Backend / intake | 1.1 | 1.3 |
| [1.3 · Run isolated jobs with owned status and deletion](../implementation-artifacts/1-3-run-isolated-jobs-with-owned-status-and-deletion.md) | Backend / worker lifecycle | 1.2 | 1.4, 3.1 |
| [1.4 · Detect and sanitize source findings with trusted rules](../implementation-artifacts/1-4-detect-and-sanitize-source-findings-with-trusted-rules.md) | Security / scanner adapters | 1.3 | 1.5, 2.1, 3.2 |
| [1.5 · Investigate findings and copy a deterministic repair prompt](../implementation-artifacts/1-5-investigate-findings-and-copy-a-deterministic-repair-prompt.md) | Frontend / source workflow | 1.4 | 2.2, 3.4, 4.1 |
| [2.1 · Retrieve a bounded public repository snapshot](../implementation-artifacts/2-1-retrieve-a-bounded-public-repository-snapshot.md) | Backend / repository adapter | 1.4 | 2.2 |
| [2.2 · Review repository findings with commit attribution](../implementation-artifacts/2-2-review-repository-findings-with-commit-attribution.md) | Frontend / repository workflow | 2.1, 1.5 | 4.2 |
| [3.1 · Enforce authorized website networking and budgets](../implementation-artifacts/3-1-enforce-authorized-website-networking-and-budgets.md) | Security / networking | 1.3 | 3.2 |
| [3.2 · Produce located ZAP baseline findings](../implementation-artifacts/3-2-produce-located-zap-baseline-findings.md) | Security / ZAP adapter | 3.1, 1.4 | 3.3 |
| [3.3 · Detect secrets in bounded visible assets](../implementation-artifacts/3-3-detect-secrets-in-bounded-visible-assets.md) | Security / asset analysis | 3.2 | 3.4 |
| [3.4 · Investigate website findings in the shared workspace](../implementation-artifacts/3-4-investigate-website-findings-in-the-shared-workspace.md) | Frontend / website workflow | 3.3, 1.5 | 4.2 |
| [4.1 · Add opt-in bounded AI explanations with fallback](../implementation-artifacts/4-1-add-opt-in-bounded-ai-explanations-with-fallback.md) | Backend / AI integration | 1.5 | — |
| [4.2 · Execute real rescans and classify comparable findings](../implementation-artifacts/4-2-execute-real-rescans-and-classify-comparable-findings.md) | Backend / comparison | 2.2, 3.4 | 4.3 |
| [4.3 · Inspect paired rescan evidence and recovery](../implementation-artifacts/4-3-inspect-paired-rescan-evidence-and-recovery.md) | Frontend / comparison workflow | 4.2 | 5.1 |
| [5.1 · Run the labeled acceptance and adversarial corpus](../implementation-artifacts/5-1-run-the-labeled-acceptance-and-adversarial-corpus.md) | QA / security validation | 4.3 | 5.2 |
| [5.2 · Verify accessible recovery and rehearse the honest demo](../implementation-artifacts/5-2-verify-accessible-recovery-and-rehearse-the-honest-demo.md) | Frontend / QA / demo operations | 5.1 | — |

## Epics

- [Epic 1 · Review a codebase safely and act on real findings](epics/epic-01-review-a-codebase-safely-and-act-on-real-findings.md)
- [Epic 2 · Review a repository revision without manual upload](epics/epic-02-review-a-repository-revision-without-manual-upload.md)
- [Epic 3 · Review a deployed website with ZAP and visible-asset evidence](epics/epic-03-review-a-deployed-website-with-zap-and-visible-asset-evidence.md)
- [Epic 4 · Receive grounded AI guidance and verify changes through rescans](epics/epic-04-receive-grounded-ai-guidance-and-verify-changes-through-rescans.md)
- [Epic 5 · Demonstrate the complete workflow with repeatable evidence](epics/epic-05-demonstrate-the-complete-workflow-with-repeatable-evidence.md)

## Parallel work

After source intake/lifecycle prerequisites, repository retrieval and the high-risk ZAP network gate can proceed separately. AI integration can begin after the source report. Respect the exact dependency lists; coordinate changes to shared schema/state modules with one owner.

## How to use this board

1. Claim an unblocked story; proposed owner roles are guidance, not assigned people.
2. Read its scope and governing contracts; create a focused branch.
3. Complete its acceptance and verification; record real results in a reviewed PR.
4. Update the [sprint tracker](../implementation-artifacts/sprint-status.yaml) and, once published, the actual GitHub issue. Do not maintain a competing JSON progress board.

## Publication status

**Not published.** [manifest.json](manifest.json) is a derived draft import package, not remote issue state. No repository, commit, issue number or assignee is invented. Before later publication, resolve local file links to verified repository blob URLs, replace dependency IDs with returned real issue URLs and establish supported parent/dependency relationships. See [repository setup](../../docs/REPOSITORY_SETUP.md).
