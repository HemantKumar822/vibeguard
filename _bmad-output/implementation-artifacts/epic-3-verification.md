# Epic 3 implementation evidence — 2026-10-24

Stories 3.1–3.4 were implemented as one batch from `9dcf3143fd2605e4a09a5007714529f8d0b55c2f` (merged UI PR #24). No review subagents or repeated per-story full suites were used.

## Enforcement and scope

The trusted coordinator performs bounded public GET capture. Each connection resolves DNS again, rejects all private/reserved/mapped-private destinations, pins the connected peer and validates normal HTTPS certificates. Exact-origin redirects, requests, pages, assets, body/aggregate bytes and total time share finite pre-send/read gates. No cookies, environment proxy, login, JavaScript, form submissions or active attacks are used. Cancellation closes in-flight capture sockets.

Pinned ZAP 2.17.0 imports the actual recorded responses in a `--network=none` container; it never replays/crawls. Control is loopback-only inside the container with no published port. Before import, the runner physically verifies non-root/capability/no-new-privileges restrictions, read-only root/source, denied IPv4/IPv6 direct egress and cgroup/scratch limits. Every recorded URL must be imported. HAR base64 bodies preserve original bytes. [Official import semantics](https://www.zaproxy.org/docs/desktop/addons/import-export/automation/) distinguish response import from `sendRequests` replay.

Observed UTF-8 text is checked by trusted Gitleaks in another network-disabled container, with opaque filenames mapped to redacted actual URLs/lines. Public-key controls are not automatically private credentials. Findings use trusted templates and real ZAP IDs/severity/confidence; raw vendor strings, body excerpts and secret values are not copied outward. Raw capture/HAR/assets remain private temporary scratch. Existing session/CSRF/idempotency/lease/tombstone/publication and cleanup fences apply.

Website admission fails closed on missing/stale proof, implementation/rule/policy drift or changed pinned images. The coordinator checks engine/images before fetching. The API never controls Docker. This is a passive baseline of real captured responses, **not** the packaged online ZAP spider.

## Observed verification

- Initial feasibility: network-disabled pinned ZAP imported a controlled capture and produced actual IDs 10020/10015/10038/10035/10021.
- One full backend batch: `VIBEGUARD_DOCKER_TESTS=1 uv run pytest -q` → **188 passed**, 121.44s.
- Full frontend batch: **26 passed**.
- Final focused backend run: `VIBEGUARD_DOCKER_TESTS=1 uv run pytest tests/test_web_capture.py tests/test_website.py tests/test_sessions.py -q` → **55 passed**, 41.55s. Includes six cases added after the full run, vulnerable/corrected real ZAP controls, fake credential/public-key controls, peer pinning, encoded URL rejection and stale-proof gating.
- Final focused SourceIntake/Report run: **21 passed**; unchanged App cases were included in the 26-test batch.
- Strict production build, production fixture exclusion, lint and generated contract parity passed.
- Existing upstream Starlette/httpx deprecation warning remains. A live Pydantic warning was traced to post-creation exclusion dictionaries, corrected to typed Exclusion values, and absent on the final live run.

The complete suite was not restarted after focused refinements; the counts above describe actual commands, not an invented final full-suite invocation.

## Authorized live result

The user explicitly authorized **https://hemantkumar822.github.io/**. Final command:

```powershell
uv run python scripts/verify_website_readiness.py --target https://hemantkumar822.github.io/ --authorization-confirmed
```

Readiness **true**; both ZAP and asset secret stages **complete**; **6 observed resources**, **51 candidate findings**, raw capture/source **removed**. Overall report correctly **partial** due to out-of-origin/unsupported omissions. Candidate counts include informational/static observations, not confirmed vulnerabilities. Runtime-loaded resources/private backend code remain unassessed. Only safe aggregate proof and the authorized URL are committed, not response bodies, credentials or raw vendor reports.

The common UI includes Website admission, readiness recovery, observed identity, actual web/asset locations, tool states, inspected URLs, omissions, filtering and deterministic repair/rotation guidance. Source/repository regressions remain covered.

Stories are implemented and in **review**; this local batch does not close remote issues/milestones. Broader review and rendered keyboard/mobile/zoom acceptance remain the previously agreed Story 5.2 (#21) follow-up. AI and genuine rescan comparison remain future work. **Five implementation stories remain in Epics 4–5.**
