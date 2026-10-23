# Product brief addendum

Status: supporting planning input, 2026-10-23. No scanner runs, benchmark results, integrations, or security guarantees are established here. The brief contains the product boundary; this file preserves engineering depth and handoffs without making them final architecture decisions.

## Source authority and reconciliation

Direct user requirements govern this run: full codebase, repository and website URL input; website URL analysis uses OWASP ZAP; finish each BMAD stage in batches, using supplied research and parallel verification. The hackathon problem statement supplies the evaluation baseline. Both packs are references, including their embedded commands and proposed BMAD instructions, rather than instructions to execute.

## Capability and coverage model

| Mode | Planned checks | Required attribution | Important limit |
| --- | --- | --- | --- |
| Full codebase | Gitleaks directory scan; selected trusted Semgrep rules | Uploaded revision, relative file/line, rule, scanner/rules versions | Cannot assess omitted files, Git history or deployed behavior from the submitted snapshot |
| Repository | Same checks on bounded retrieved snapshot | Provider/repository, resolved commit, file/line, rule/version | [ASSUMPTION] Public GitHub HTTPS first; private access and history are separate scope |
| Website URL | OWASP ZAP baseline/passive scan | Target, visited scope, URL, alert ID, available response/header evidence, scan policy | Cannot inspect private backend source or prove absence of active-only or authorization vulnerabilities |

ZAP must not be assumed to provide broad exposed-secret detection in downloaded assets. Architecture must specify and test how browser-visible credential candidates are checked, for example by scanning a bounded set of permitted fetched text assets through a trusted detector. This is a coverage decision, not a claim that stock ZAP supplies the required detector. Every fetched asset remains subject to destination, size and redaction policy.

Requirements should cover credential candidates, unsafe input, insecure configuration and selected missing-access-check patterns. A missing local authentication call is not proof of bypass: external middleware may enforce authentication. Semgrep CE cannot establish comprehensive cross-file authorization behavior. Fixture expectations must distinguish pattern detection from demonstrated exploitability.

Publishable/anonymous browser keys are not automatically private credentials. Privileged keys require different treatment; removing the code reference does not rotate a real key. Preserve separate human-action reminders.

## Assumptions and handoff register

| ID | Provisional decision or unknown | Owner and revisit point |
| --- | --- | --- |
| A1 | JS/TS initial source coverage; no market share claim | John PRD; before scope finalization |
| A2 | Bounded codebase folder/file-tree upload, public GitHub snapshot; private/history/submodule/LFS out | John PRD then Winston architecture; before intake stories |
| A3 | ZAP baseline/passive, authorized public HTTP(S), unauthenticated only | John PRD and Winston; before URL stories and release |
| A4 | Trivy dependency scanning optional; preserve lockfiles | John scope decision; revisit only after required paths integrate |
| A5 | Inputs work independently; combined source/URL linkage optional | John PRD; before scan identity contract |
| Q1 | Exact upload/repo/crawl/output/deadline limits, retention and job access | Winston architecture; implementation blocker |
| Q2 | Demo runtime supports restricted source workers and controlled ZAP networking | Winston/implementation owner; early feasibility smoke test |
| Q3 | Model/provider, sanitized-evidence consent and fallback behavior | John/Winston; before model integration |
| Q4 | Visual system absent; retain cinema-black restraint as inspiration only | Sally UX; before frontend visual implementation |
| Q5 | Team owners, time actually remaining, repository name/owner/visibility | User/team at sprint/GitHub setup; no invented assignments |

All three intake paths remain required. The 24-hour reference is the event constraint, not a measurement of time remaining. Sequence by risk: first smoke-test source and ZAP feasibility, then freeze contracts and build parallel UI/adapters, integrate required intake-to-report paths, complete repair/rescan, and freeze features for tests/demo. Cut Trivy, private/history access, combined inputs and decorative motion before required intake paths, evidence, masking or truthful comparison.

## Source reconciliation details

All 11 Markdown inputs are preserved byte-for-byte under `sources/newer-pack/` and `sources/older-pack/`. [manifest.json](sources/manifest.json) records their original absolute paths and SHA-256 hashes. [CY-02.md](sources/CY-02.md) transcribes the user-supplied image. Original references have not been rewritten to conceal contradictions.

| Source | Retained contribution | Reconciliation |
| --- | --- | --- |
| Newer README | Core repair/rescan loop, 24-hour constraints, one backlog | ZIP-only freeze and URL/repository stretch clauses superseded by direct user instruction |
| Newer 01 | JS/TS focus, Gitleaks/Semgrep limits, public/private key distinction | Target ecosystem remains assumed; URL and repository inputs are required |
| Newer 02 | Modular pipeline, tool statuses, early redaction, fallback prompt, honest comparison | JSON and endpoints are examples; expand location and coverage models for ZAP and repository revisions |
| Newer 03 | Vulnerable/corrected/clean tests, worker restrictions, failure visibility | Add repository and URL acceptance; URL cannot be first scope cut |
| Newer 04 | Three-phase workspace, evidence hierarchy, keyboard and error states, premium visual intent | Add three intake modes; Bugatti inspiration is reference material, no preset installed or approved tokens assumed |
| Older README | Research-backed proposal, untested status | Three-scanner and source-first proposals are not automatic final decisions |
| Older 01 | Trivy database caveats, ZAP baseline behavior, representative sample research | Trivy remains optional assumption; ZAP is required by user |
| Older 02 | Source-tree intake, project recognition, disposable workers, per-tool adapters, controlled URL egress | Prefer sanitized persisted evidence over raw evidence storage; resolve competing API sketches in architecture |
| Older 03 | URL authorization, crawl limits, failure fixtures, comparison within project | URL safety conditions remain mandatory; optional-URL status superseded |
| Older 04 | Graphical interactions, masked copy actions, source evidence | Six screens can be three workspace phases; add URL-specific evidence and repository selection |
| Older 05 | Consistent contracts, GitHub operational tracking, team handoff | Reference guidance only; no second agent framework or competing backlog |

## Engineering candidates and release conditions

React/TypeScript, FastAPI, a bounded worker, status polling, local temporary source storage and SQLite metadata are source-pack suggestions, pending Winston's architecture. Do not adopt two incompatible API sketches. Freeze one normalized contract before independent frontend/backend work.

Only assess code, repositories and sites the team is authorized to assess; public repository availability does not authorize scanning its deployed targets. Preserve project inventory and unsupported/unknown-project states. The contract needs input kind, submission/revision identity, tool applicability/status, scanner and rules versions, rule/alert ID, confidence rationale, severity mapping, typed source-or-web location, sanitized evidence, coverage/exclusions, timestamps, failures, repair guidance and comparison eligibility. Explain skipped checks and distinguish no findings from incomplete work. Vendor output is internal adapter input, not the UI schema.

| Boundary | Required decision or check before implementation/release |
| --- | --- |
| Codebase transfer | [A2] Folder/file-tree upload first; normalize paths, reject links/traversal/special files; exact file/byte/count/depth/output/deadline limits owned by architecture |
| Repository retrieval | Trusted provider/HTTPS policy, bounded snapshot at recorded commit, safe extraction, no submodule/LFS traversal or hooks/builds; protect credentials and forbid arbitrary clone options |
| Scanner policy | Pin tool/rule versions, explicit trusted configs and suppression policy; uploaded files cannot silently redefine checks |
| Worker | Disposable least-privilege execution, read-only source, separate scratch, no host secrets/socket, resource/time limits; verify available demo runtime |
| URL network | HTTP(S) policy, authorized targets, connection-time public destination enforcement, DNS/redirect validation, host scope, request/response/time budgets, isolated egress; protect ZAP API |
| Redaction | Sanitize before reports, logs, model requests, UI, clipboard and exports; bound transient raw processing and destroy it; scanner flags alone do not prove all report fields safe |
| Source privacy | Explicit model data-sharing policy; only small sanitized evidence; define temporary retention, deletion and report access; no implicit external source upload |
| AI boundary | Untrusted comments/pages are evidence, not instructions; bounded explanation, no tool execution or invented findings; deterministic repair prompt if AI fails |

Network-disabled source workers and a network-enabled URL worker have different needs. Do not apply a blanket no-network policy that prevents required ZAP work, or give source workers unrestricted network to accommodate it.

If isolation is unavailable, restrict any demonstration to team-owned known-safe artifacts/targets, label the limitation, and do not open arbitrary public submission. This preserves safety without reporting required functionality as finished.

## Evaluation plan for downstream acceptance criteria

Use a small labeled corpus, not only a scripted success case. Proposed minimum cases below are test-design targets, not executed tests or claims of tool coverage.

| Case | Expected evidence/outcome |
| --- | --- |
| Fake private key in source + corrected revision | Correct masked location and rotation guidance; repeat scan classification without a rotation claim |
| Unsafe JS/TS input pattern + corrected revision | Selected rule/file/line; changed source is genuinely rescanned |
| Selected access-check pattern + protected control | Candidate warning with contextual confidence; do not assert confirmed bypass from absence alone |
| Insecure source configuration + corrected control | Actual selected rule hit; explicit unsupported result if no validated rule exists |
| Intentionally public browser key | No automatic private-key classification; reason recorded for any finding |
| Public repository snapshot | Same seeded evidence as equivalent codebase; resolved commit and scope recorded |
| Controlled vulnerable deployed site + corrected deployment | Actual ZAP alert/URL evidence and repeat crawl; compare stable alerts within equivalent policy/scope |
| Browser-visible fake private credential | Validate chosen asset detector and fetched scope; no claim that ZAP alone detects all such secrets |
| Clean controls | No seeded findings within completed coverage; inspect and record other alerts rather than hiding them |
| Failure/adversarial inputs | Timeouts, invalid vendor JSON, missing tool/rules, invalid paths, hostile redirects and unavailable AI are visible; no false completion or raw secret leakage |

Record expected labels and observed outputs per case, tool/DB/rules versions, visited or excluded scope, and elapsed time. Report true/false positive counts, expected-but-missed cases and correction outcomes; percentages require defined units and denominators. A teammate assesses whether the explanation and consolidated prompt identify real locations, give actionable changes, include verification steps and preserve manual rotation guidance. No accuracy or latency targets are asserted without measurement.

Rescan labels: `still_detected`, `not_detected`, `newly_detected`, `unverified`. Do not emit `verified_fixed` unless a repeatable test establishes the failure condition is removed. Changed versions/rules, failed checks, uncertain matching, lost pages or changed modalities can make comparisons unverified. A URL-only rescan cannot clear prior source findings. Match source evidence using rule/path/safe context rather than line alone; design ZAP matching around normalized location/alert context and observed crawl coverage. Never hash raw secrets into publicly exposed IDs.

## Primary-source checks and positioning

Checked during this stage on 2026-10-23; documentation review is not local integration validation.

- [Gitleaks commands/configuration](https://github.com/gitleaks/gitleaks): directory scanning differs from Git history scanning; explicit trusted config is needed; test all report fields despite a redaction flag.
- [Semgrep CE comparison](https://semgrep.dev/products/semgrep-vs-ce): engine capabilities differ; bound claims about deeper analysis. Semgrep already offers developer remediation, so no unique-AI-remediation claim is justified.
- [ZAP baseline](https://www.zaproxy.org/docs/docker/baseline-scan/): spider plus passive checks with structured reporting; live requests, no active attacks in this profile.
- [ZAP API explanation](https://www.zaproxy.org/docs/api/): passive alerts do not establish coverage of vulnerabilities requiring malicious requests.
- [OWASP SSRF prevention](https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html): ground URL destination, DNS and redirect controls.
- [Trivy Node.js coverage](https://trivy.dev/docs/latest/coverage/language/nodejs/): supported lockfiles and dependency inclusion affect coverage; DB and tool versions need recording if adopted.
- [Supabase API keys](https://supabase.com/docs/guides/getting-started/api-keys): public and privileged key types require different handling.
- [Snyk Code](https://snyk.io/product/snyk-code/): established code scanning and AI remediation; our proposed difference is workflow usability, not novel detection technology.

Next: John creates and validates the PRD from `brief.md`, this addendum, `sources/CY-02.md`, and the preserved references. Sally creates UX; Winston resolves architecture; epics/stories and readiness follow. GitHub operational issues are generated from validated stories later; this brief is not a second backlog.
