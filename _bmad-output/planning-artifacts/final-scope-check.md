# CY-02 final planning check

Date: 2026-10-23. Verdict: aligned with the challenge, with targeted backlog refinements now applied before publication. Document assessment only; no implementation, scanner execution or delivery-time validation.

## Coverage

The PRD, architecture/API/safety profile, UX experience and all 16 canonical stories cover source/repository intake, website input using ZAP, secrets and the three other issue categories, masked evidence, severity/confidence, plain-language fixes, consolidated repair instructions, genuine rescans, rotation reminders and authorized assessment. The additional repository and standalone website modes preserve the user's requirements. Evaluation includes observed TP/FP/FN, clean controls, prompt utility and repeat evidence. No challenge capability was found missing from the requirements.

## Refinements applied before publishing issues

1. **Remove unnecessary sequencing around the central demo.** Story 4.3 depends on optional AI Story 4.1, although deterministic guidance and comparison do not require AI. That dependency has been removed from the canonical backlog and derivatives. Story 4.2 can implement and exercise source comparison early, while retaining all three modes as its final acceptance; final integration need not prevent early testing.
2. **Clarify the test matrix.** Story 5.1 says fixtures for all four categories and each input mode. Explicitly distinguish category coverage across the product from per-mode coverage: source/repository fixtures cover selected access-check and unsafe-input rules; website fixtures validate actual passive observations and visible-asset secrets. Do not turn that sentence into a promise that every category is detectable through passive URL scanning. Record unsupported cells and the reason, and preserve product-wide coverage of all four categories.
3. **Bring feasibility and evidence forward.** Keep the final full-corpus gate in Epic 5, but build vulnerable/corrected/clean fixtures alongside each adapter, as Story 1.4 already requires. Prove container availability and the ZAP egress mechanism early (1.1 and 3.1); choose an authorized demo deployment compatible with the public-origin policy. Schedule a working source scan â†’ repair prompt â†’ corrected rescan as the first end-to-end rehearsal. Team capacity and remaining hours are unknown, so 24-hour delivery is not established by this plan.

## Scope to retain

Keep masking, actual tool states, authorization, enforced URL boundaries and honest rescan classifications. Keep dependency scanning, private repositories, active/authenticated scans and decorative additions deferred. Initial JS/TS, public GitHub and passive public-target support remain documented assumptions, not universal support claims.

## Next

The dependency, acceptance-clarity and early-feasibility refinements are synchronized across epics, backlog, handoffs and issue drafts. Complete the single remaining repository/GitHub setup stage and start Story 1.1. No Git initialization or remote publication was performed by this check.
