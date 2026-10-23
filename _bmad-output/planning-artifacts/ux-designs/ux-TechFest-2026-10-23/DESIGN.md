---
name: AI Security Reviewer
description: Evidence-first visual security review workspace for codebase, repository and ZAP website scans.
status: final
created: 2026-10-23
updated: 2026-10-23
approval: pending-user-review
sources:
  - ../../prds/prd-TechFest-2026-10-23/prd.md
  - ../../prds/prd-TechFest-2026-10-23/addendum.md
colors:
  canvas: '#0B0B0D'
  surface: '#141417'
  raised: '#1D1D22'
  text: '#F5F5F7'
  muted: '#B5B5BE'
  border: '#45454F'
  focus: '#B6D9FF'
  action: '#F5F5F7'
  on-action: '#0B0B0D'
  critical: '#FFA5B1'
  warning: '#F6CF79'
  success: '#A3DEBA'
  info: '#B6D9FF'
typography:
  display:
    fontFamily: 'Arial, Helvetica, sans-serif'
    fontSize: '48px'
    fontWeight: '700'
    lineHeight: '1.08'
    letterSpacing: '-0.04em'
  heading:
    fontFamily: 'system-ui, Segoe UI, sans-serif'
    fontSize: '24px'
    fontWeight: '600'
    lineHeight: '1.3'
  body:
    fontFamily: 'system-ui, Segoe UI, sans-serif'
    fontSize: '16px'
    fontWeight: '400'
    lineHeight: '1.5'
  label:
    fontFamily: 'system-ui, Segoe UI, sans-serif'
    fontSize: '14px'
    fontWeight: '600'
    lineHeight: '1.5'
  code:
    fontFamily: 'ui-monospace, Cascadia Code, Consolas, monospace'
    fontSize: '14px'
    fontWeight: '400'
    lineHeight: '1.6'
rounded:
  sm: '4px'
  md: '8px'
  lg: '12px'
spacing:
  '1': '4px'
  '2': '8px'
  '3': '12px'
  '4': '16px'
  '5': '24px'
  '6': '32px'
  gutter: '24px'
  mobile-gutter: '16px'
components:
  submission-panel:
    background: '{colors.surface}'
    radius: '{rounded.lg}'
    padding: '{spacing.5}'
  tool-timeline:
    background: '{colors.surface}'
    text: '{colors.text}'
  coverage-banner:
    background: '{colors.raised}'
    text: '{colors.muted}'
  finding-list:
    background: '{colors.surface}'
    selected-border: '{colors.focus}'
  evidence-detail:
    background: '{colors.surface}'
    code-size: '{typography.code.fontSize}'
  repair-panel:
    background: '{colors.raised}'
    radius: '{rounded.md}'
  comparison-panel:
    background: '{colors.surface}'
    radius: '{rounded.md}'
  notice:
    background: '{colors.raised}'
    text: '{colors.text}'
  confirmation-dialog:
    background: '{colors.raised}'
    radius: '{rounded.lg}'
  button:
    background: '{colors.action}'
    text: '{colors.on-action}'
    radius: '{rounded.md}'
---

## Brand & Style

The supplied direction is a premium, cinema-black, restrained graphical tool with bold entry typography and precise evidence views. These exact tokens are **[ASSUMPTION UX-A1] a proposed implementation of that direction**, not a supplied or approved Bugatti preset. Retain the working product name; do not invent logos, automotive imagery, fonts or branding claims.

Confidence comes from readable evidence and honest states. Reserve display typography for the submission headline. Results are compact, calm and technically legible. DESIGN.md owns appearance; [EXPERIENCE.md](EXPERIENCE.md) owns behavior. These two contracts win over any later mockup on conflict.

## Colors

Use `{colors.canvas}` for the page, `{colors.surface}` for panels and `{colors.raised}` for selected/contextual regions. Primary text uses `{colors.text}`; metadata uses `{colors.muted}`. Never reduce essential text opacity to imply hierarchy.

Primary buttons use `{colors.action}` with `{colors.on-action}`. Severity and outcome accents use `{colors.critical}`, `{colors.warning}`, `{colors.success}` and `{colors.info}`, always alongside a written label and, when helpful, an icon. Green means a completed check or observed classification, never “website is secure.”

Essential control outlines use `{colors.muted}` when an outline alone identifies the control; `{colors.border}` is for nonessential separators. Focus uses a 2px `{colors.focus}` outline with 2px offset. Normal text target is at least 4.5:1; meaningful icons, boundaries and focus at least 3:1 against adjacent surfaces. Color pairs are mechanically checked in `checks.json`; real component states still require implementation checks.

## Typography

Use `{typography.body.fontFamily}` for body/controls and `{typography.code.fontFamily}` for snippets, paths and rule IDs. No remote font dependency. Display is 48px on spacious desktop and 32px below 768px; long headings wrap. Body is 16px, labels/code 14px. Do not set dense findings in display type or truncate the only copy of a location.

## Layout & Spacing

Use the 4/8/12/16/24/32px scale. Maximum workspace width is 1440px, centered, with `{spacing.gutter}` desktop and `{spacing.mobile-gutter}` narrow gutters. All sizing decisions are **[ASSUMPTION UX-A2] proposed layout defaults**, not measured user preferences.

Desktop at 1024px and above: compact header → phase indicator → full-width coverage → 320px finding list beside flexible evidence detail; repair panel below detail. Comparison uses two equal evidence columns under a shared classification list. Tablet 768–1023px uses a 280px list where space permits; below 768px all regions stack. At 360px there is no page-wide horizontal overflow; code scrolls within its panel.

## Elevation & Depth

Hierarchy comes from tonal layers, spacing and separators. No glow, gradients, glass effects or decorative scan beams. Only the confirmation dialog uses a modest dark shadow and scrim. Keep status and error regions visually distinct without overpowering source evidence.

## Shapes

Use `{rounded.sm}` for code/metadata regions, `{rounded.md}` for controls and `{rounded.lg}` for major panels/dialogs. Small severity labels are rectangular with modest rounding. Avoid oversized floating pill navigation and decorative shapes.

## Components

The names below match EXPERIENCE.md exactly. Use accessible native elements or proven primitives; no component library is selected by this document.

| Component | Visual contract |
| --- | --- |
| Submission panel | Three labeled mode selectors, one clear primary action, scoped input area, visible limits, permission and model-sharing controls; 44px minimum control height |
| Tool timeline | Text status with icon per applicable tool; optional elapsed time from real timestamps; indeterminate motion only while actually running |
| Coverage banner | Named completed/incomplete checks, source revision or target and exclusions; critical failures get a persistent labeled notice |
| Finding list | Severity/title/location hierarchy; selected border plus raised fill; filter/search labels always visible; full location available in detail |
| Evidence detail | Header with actual location, severity/confidence/rule; bounded code/response block and plain-language impact/fix; redaction visible as `[REDACTED]` |
| Repair panel | Readable multiline prompt, clear Copy action and separate revoke/rotate reminder; fallback label remains visible |
| Comparison panel | Baseline/new labels and coverage, classification text and count, paired evidence; narrow view stacks baseline before new |
| Notice | Persistent inline errors/recovery; compact live status for copy feedback; labels never depend on color |
| Confirmation dialog | Clear destructive title, description, Cancel and Delete; restrained scrim; no nested dialog |
| Button | Light primary action, outlined secondary, labeled destructive action; visible hover/active/focus/disabled appearance without changing layout |

## Do's and Don'ts

- Show real evidence, actual status and explicit uncertainty; never invent health scores, scan percentages, terminal output or “verified fixed” badges.
- Keep source and website evidence visually related while preserving their different locations and coverage.
- Use no hover-only action, hidden raw secret, decorative dashboard, chatbot shell or brand imitation.
- Motion is optional: 120–180ms opacity/color changes; reduced-motion removes them. No looping decorative motion.
- Treat exact palette, type and layout as proposed decisions open to user correction. The supplied source direction remains the authority for intent.
