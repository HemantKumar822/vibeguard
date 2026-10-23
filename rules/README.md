# Mandatory source rules v1

These rules are authored for VibeGuard and distributed under the MIT license in LICENSE. No downloaded Semgrep registry pack or submitted configuration is loaded. Gitleaks is explicitly configured with this file rather than its default rules. Rule fingerprints include both configurations and the suppression policy; immutable scanner images are recorded in contracts/scanner-readiness.json.

Coverage is deliberately narrow: selected credential patterns, dynamic eval, disabled TLS verification and simple Express-style routes lacking a local middleware argument. Route findings require review: global middleware, handler internals or framework authorization can make them false positives. A public browser API key alone is not a private credential. No live key validation occurs.

Inline `nosem` / `gitleaks:allow`, project ignore files, Git metadata and submitted rule configurations cannot turn off these checks. Vendor JSON is processed only in bounded coordinator memory. Evidence includes the trusted rule and validated file/line; source literals and unknown vendor fields are not included in reports.
