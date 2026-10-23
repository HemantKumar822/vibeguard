# Review workspace UI polish — 2026-10-24

User requested a polished professional interface and push. This is a presentation pass on the existing source/repository workflows, with no backend changes.

## Design direction

Use a compact security workbench rather than a large marketing introduction. Fixed desktop navigation, quiet API connection status, an actual three-stage review rail, source selection and scope context, then a dedicated evidence/repair panel. The rail follows accepted Scan/repair state and never invents progress or security scores.

Core palette: background `#0b0b0f`, panel `#131318`, raised surface `#1b1b23`, border `#32323e`, secondary text `#aaaab9`, blue accent `#b6d9ff`. Arial display headings, Segoe UI/system body and monospace evidence/utility labels. Existing 48px/32px heading scale and reduced-motion policy retained.

Layout: desktop sidebar → header and compact introduction → source/review rail → two-column source and scope panel → findings/detail and repair output. Mobile condenses navigation, stacks forms and findings, preserves limits and keyboard focus, and keeps code/evidence locally scrollable. No external font/image/CDN dependencies.

## Improvements

- Persistent workspace navigation and skip link; links target real sections.
- Folder selection, mapped-file fallback, repository attribution and consent visually separated.
- Collapsible selected-file inventory; accepted report preserved during new input selection.
- Primary action hierarchy, clearer empty/error/reconnect states and explicit unavailable capabilities.
- Text-labeled tool states, severity badges, selected finding emphasis and a dedicated repair panel.
- Coverage notes expand by default for partial/failed reports.
- Mobile scope limits remain visible even when the desktop context panel is hidden.

## Verification

23 existing frontend behavioral tests passed after the layout/report changes. Strict TypeScript production build, fixture-exclusion gate and lint passed. Backend tests were not restarted for presentation-only changes. Rendered browser/keyboard/zoom verification remains the explicitly deferred Story 5.2 follow-up; it is not claimed from DOM tests or CSS inspection.
