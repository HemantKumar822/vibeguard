# safety-v1 — proposed finite prototype policy

These are architecture defaults for implementation/testing, not measured throughput or proven containment. Core, API, workers and capabilities must use one versioned profile. Changes require a new fingerprint and comparison review. No public service is enabled merely because this file exists.

| Boundary | Limit / rule |
| --- | --- |
| Source intake | 25 MiB aggregate uploaded bytes; 5,000 files; 2 MiB/file; path depth 20; 240 UTF-8 bytes/path; reject absolute, traversal, links, devices and normalized/case-colliding paths |
| Repository | Public GitHub HTTPS only; requested ref 256 bytes; resolve full commit; archive download 25 MiB, unpacked 100 MiB, expansion ratio 100:1, same file/path limits; 60s total retrieval/extraction |
| Source policy | Review source/config files including relevant dotfiles and lockfiles; exclude vendor/node_modules/build outputs with reasons. No project-provided rule/config/suppression overrides. Partial coverage disclosed |
| Admission | 1 running job and at most 3 queued jobs system-wide; 429 beyond cap; 600s maximum queue wait then failed |
| Job deadlines | 300s after start; source tool 90s each; ZAP 180s including spider/passive wait; asset stage 60s; model 15s; global deadline wins |
| Worker resources | 2 CPU, 2 GiB RAM, 128 processes, 256 MiB scratch, 5 MiB vendor output/tool; no source execution, network disabled except dedicated retrieval/web/model adapters |
| Website target | Exact origin: scheme/host/port; HTTP80 or HTTPS443 only. No userinfo or fragments; URL 4 KiB. Public globally routable destinations only; reject nonpublic/reserved/metadata IPv4/IPv6 and DNS changes to them |
| Crawl and redirects | 50 HTML pages; 200 total HTTP requests including asset requests and redirects; 3 redirects/request, same-origin only; 20 MiB aggregate response bytes and 2 MiB/body; no authenticated sessions or active scan |
| Asset scope | Up to 50 unique same-origin linked text assets within shared request/byte caps; no JavaScript execution or recursive unbounded imports; map inspected assets to coverage and disclose omitted/runtime-loaded assets |
| Website enforcement | All ZAP/fetch traffic through controlled egress; validate DNS and connected peer per connection, block direct sockets. A trusted pre-send request-budget gate and response-byte enforcement must terminate on bounds; URL startup checks alone are insufficient |
| Model input | Explicit opt-in; at most 30 Findings, 24 KiB sanitized structured request, 8 KiB accepted response, one call, no automatic retries. Remaining Findings use deterministic guidance; master prompt includes all Findings within report limits |
| Report bounds | 1,000 Findings, 2 KiB evidence/Finding, 128 KiB master prompt, 5 MiB sanitized report; cap overflow yields partial coverage and actionable warning, never silent complete |
| Raw retention | Per-job private scratch only; remove on tool/job termination, deletion or crash recovery. Startup + 60s sweeper removes expired/abandoned scratch; cleanup failure is visible and blocks unrestricted intake |
| Report/session retention | Sanitized report 24h from terminal time; session expires after 24h inactivity; inaccessible expired data is purged by 60s sweep. No browser persistent storage; lost cookie means no access recovery in MVP |
| Delete | Tombstone immediately; stop running job, forbid late results, remove raw/report artifacts; 60s cleanup deadline, then deletion status failed with safe reason and retry. Cleanups retain no finding/source content in logs |

## Retrieval and worker enforcement

Repository retrieval uses fixed GitHub endpoints and an explicit codeload host allowlist, public-destination checks and bounded streaming. Strip the single archive root safely; never resolve a user path by concatenation alone. Optional archive upload must reuse this validator, not introduce a separate permissive extractor. Ingested paths/URLs may themselves contain sensitive material; sanitize display/log fields and retain raw values only in temporary processing.

Container jobs run non-root, read-only root filesystem with separate bounded scratch, no host environment secrets, dropped capabilities, no-new-privileges, resource quotas and no host socket. The trusted host coordinator owns launcher privileges; the API and scanner jobs do not. Runtime-engine and image digests are pinned and recorded during bootstrap; moving tags are not executable policy.

Public-origin egress requires connection-time checks, including IPv4-mapped IPv6 and redirect/rebinding tests. ZAP and asset fetcher must not bypass the enforcement route. A trusted HTTP-request counter/hook plus bounded connection/response handling may implement the policy; its actual compatibility with the selected ZAP build is an early feasibility story. The chosen mechanism must prove enforcement rather than merely rely on the crawler's advertised settings. Do not mount TLS/session data from the host into workers.

## Release gates

Before required-mode delivery: demonstrate source safety; public repository snapshot equivalence; ZAP alert and browser-visible fake-secret detection; same-policy corrected repeats; public-key/clean controls; category coverage; hostile path/config/redirect/DNS tests; masked output across every channel; idempotency/session/CSRF/deletion/crash cases; and real demo-machine timings. Use fake credentials and team-authorized targets only.

If runtime/network enforcement fails, keep arbitrary submissions disabled and state the missing capability. A team-fixture demonstration is a labeled limitation, not completion of required public-target functionality. Optional dependency scanning cannot displace any required mode or safety gate.
