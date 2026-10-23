# 04 — Frontend & UX Specification (MVP)

**Status:** Final functional UX requirements for the 24-hour prototype; visual styles come from the team's `DESIGN.md`. **No second design framework.**  
**Design inspiration:** Bugatti preset from [getdesign.md](https://getdesign.md/bugatti/design-md), installed by the team if desired with `npx getdesign@latest add bugatti`. The preset is an independent interpretation of publicly visible brand design, not an official Bugatti design system. This document does **not** install it or copy trademarks, photography, logos, or proprietary fonts.

## 1. UX goal and governing rule

The app is a **visual security review workspace**, not a chat assistant. In one short journey a developer must be able to answer:

1. What project did I scan, and which checks ran?
2. What did the tools actually find, and **where**?
3. What should I ask my coding AI to change?
4. What changed after I uploaded the corrected project?

The presentation can be premium and cinematic, but **evidence is always more important than visual drama**. Do not use fake security scores, fake terminal output, fake graphs, or simulated tool success labeled as real.

## 2. Visual direction: Bugatti-inspired, not a Bugatti clone

The preset emphasizes **cinema-black surfaces, monochrome restraint, striking display typography, and controlled motion**. Apply those principles selectively:

- **Entry / project submission:** Bold typography, intentional whitespace, confident page composition, one clear primary action.
- **Scan in progress:** Precise scanning animation and restrained tool-status visuals; motion follows actual events, not fake activity.
- **Findings / code view:** Prioritize dense information clarity, legible monospace, consistent panels, and crisp separators. **No giant hero lettering** inside detailed tables.
- **Comparison:** Side-by-side evidence and clearly labeled differences; do not rely on color alone.
- **Branding:** Make an original identity for our reviewer; avoid Bugatti marks, automotive images and borrowed logos.

Once the team provides `DESIGN.md`, its **actual tokens** (colors, typography, spacing, component design and motion) override these inspirational descriptions. Treat `DESIGN.md` as a starting point to adapt, not an instruction to sacrifice accessibility for visual resemblance. Maintain readable contrast, sensible density, reduced-motion support and predictable focus states.

## 3. Exactly three product experiences

Implement as one route/workspace with three visible phases if that is faster. No separate marketing site, account system, chat page, admin console, project gallery, or analytics dashboard.

| Phase | Primary user action | Visible outcome | Mandatory empty/error states |
| --- | --- | --- | --- |
| **A. Submit & scan** | Drop/select project ZIP, click Scan | Validated file, project info, Gitleaks/Semgrep status sequence | Invalid ZIP, upload too large, unsupported/unknown project, scan failure, no findings |
| **B. Investigate & repair** | Pick/filter a finding, read evidence, copy repair prompt | Severity + confidence, exact file/line, redacted snippet, plain explanation, next step | Partial scan, unavailable source snippet, AI unavailable / fallback prompt |
| **C. Rescan & compare** | Upload corrected ZIP; compare runs | Named findings classified as still detected / not detected / new / unverified, with tool coverage | Failed rescan, unmatched finding, mismatched scanner version/rules |

### Suggested desktop layout

```text
┌──────────────────────────────────────────────────────────────────────────┐
│ Original wordmark      Project / Scan name            Scan status       │
├──────────────────────────────────────────────────────────────────────────┤
│ PHASE A: Upload  →  Scanning  →  Findings  →  Compare                     │
├──────────────────────────────────────────────────────────────────────────┤
│ [Tools: Gitleaks ✓ | Semgrep ✓]  [Coverage: 2 / 2 checks completed]    │
├───────────────────────┬──────────────────────────────────────────────────┤
│ FINDINGS              │ SELECTED FINDING                                 │
│ Severity + tool       │ File and line • rule • confidence                │
│ filters               │ Safe highlighted snippet (secret redacted)       │
│                       │ Why this matters / limits / suggested repair     │
│ [Finding item]        │                                                  │
│ [Finding item]        │ [Copy consolidated AI repair prompt]             │
├───────────────────────┴──────────────────────────────────────────────────┤
│ [Upload corrected ZIP]     [Compare scans]                              │
└──────────────────────────────────────────────────────────────────────────┘
```

On mobile/narrow view: stack findings list → selected issue detail → repair action; make long paths and code snippets scroll without breaking layout. Avoid horizontal scrolling across the whole page.

## 4. Required interface components (nothing extra)

1. **Upload zone:** Click or drag/drop, selected ZIP details, limit guidance, validation errors and Scan CTA.
2. **Scanner timeline:** Two named stages with `queued`, `running`, `complete`, `failed`, `skipped`, `timed_out`; update from backend polling, not arbitrary timers.
3. **Finding summary:** Grounded totals by severity and completed-tool count (not a made-up security score).
4. **Finding list + filters:** Severity, scanner, search by filename/title; keyboard selection and clear selected state.
5. **Finding detail:** File path, line, scanner rule, confidence, redacted supporting evidence, plain explanation, and actionable fix guidance.
6. **Repair prompt panel:** One complete prompt with Copy button and copy feedback; a deterministic non-AI fallback when the model fails.
7. **Rescan comparison:** Two version labels, per-tool coverage, summary count changes, per-finding status labels, and drill-down evidence. For exposed real credentials, separate **human action: revoke/rotate key** reminder.

Optional UI libraries are implementation choices, not additional workflows: use React + TypeScript with existing accessible component primitives; icons/charts/animations only when genuinely helpful. A chart is **not** required to satisfy the graphical-UI goal.

## 5. Interactive behavior and truthful copy

- Scan only after the file passes client-side prechecks; backend validation is authoritative. Show the actual reason if it rejects input.
- Poll `GET /scans/{id}` for authoritative run/tool states; stop on terminal status, and clearly handle network disconnect/retry.
- A scanner returning 0 findings displays **“No findings detected by completed checks”**, never **“Your website is secure.”**
- A failed or skipped scanner displays **“This check did not complete”**, not a green check.
- Findings are **potential issues** unless there is sufficient proof; show `confidence` with an explanation.
- Never render complete secrets in snippets, prompts, logs, clipboard, download data, tooltips or hidden attributes.
- When the corrected ZIP is scanned, distinguish **“Not detected on rescan”** from **“Verified fixed.”** The former is the expected MVP label; the latter needs a stronger reproducible check.
- Generate a fix prompt containing exact reported locations and constraints, but no fabricated code changes or live credentials.
- Provide proper loading skeletons, empty screens, error messages, button disabled states and understandable copy feedback.

## 6. Shared frontend data contract

Use the example in [`02_PRODUCT_AND_ARCHITECTURE.md`](02_PRODUCT_AND_ARCHITECTURE.md) as the common API source. Frontend development can begin with three *explicitly marked* fixture payloads:

- **Running:** one complete scanner, one currently running.
- **Found:** several findings with redacted evidence and a repair prompt, including a warning labeled for review.
- **Compare:** one still detected, one not detected, one newly detected, one unverified due to scanner failure.

Fixtures are development tools only; the submitted demo must connect to real scanner output and visibly distinguish any demo fixture mode from a real scan. Do not define a separate incompatible UI-only JSON schema.

## 7. Scope, acceptance tests and owner handoff

**Frontend acceptance (P0):**

- [ ] ZIP upload, invalid-file behavior and real scan progress work against the shared API.
- [ ] Findings can be searched/filtered; selecting one displays actual file/line + sanitized evidence.
- [ ] AI prompt is copyable; fallback repair guidance appears if model call fails.
- [ ] Corrected ZIP goes through a real second scan and a truthful before/after comparison.
- [ ] The UI looks like one cohesive product with clear hierarchy and precise interaction—not a stock chatbot or generic admin template.
- [ ] Responsive narrow layout, visible focus, keyboard accessibility, readable code view, contrast and reduced-motion behavior are checked.
- [ ] Broken scanners and incomplete coverage are obvious; no fake safe-state or synthetic metric is presented as real.

**Parallel collaboration:** Agree on the API response fixture and `DESIGN.md` first. Frontend can build from mocked contracts immediately; backend can build scanners concurrently. Integrate incrementally instead of waiting until the end.

**Time constraint:** Prioritize a polished **single workspace** and its three phases. If behind, cut decorative animations, charts, extensive onboarding and new pages **before** cutting evidence clarity, responsiveness, loading/error states or rescan UX.

## 8. Design handoff when your team runs BMAD

In the repository root, from your own environment:

```bash
npx getdesign@latest add bugatti
```

Verify the resulting `DESIGN.md` and commit the agreed version. The CLI saves the preset to `./DESIGN.md` when none exists; if one already exists, it normally writes into a nested preset directory instead of overwriting unless forced. **No need to run this command again on every teammate's machine** once the agreed file is committed. Source: [getdesign npm documentation](https://www.npmjs.com/package/getdesign).

Supply **both** `DESIGN.md` and this UX spec to BMAD. `DESIGN.md` defines how it looks; **this document defines what it must do**. Have BMAD plan frontend implementation, integration and acceptance checks—do not invent a second design toolchain.
