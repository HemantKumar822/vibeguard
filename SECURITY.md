# Security

VibeGuard reviews untrusted source and authorized websites. Input, worker isolation, network destination checks, redaction and report ownership are release-critical boundaries.

## Authorized scope

Only submit code or sites you own or are authorized to assess. Website review is bounded passive analysis of public responses and observed text assets. It cannot inspect private backend source, run authenticated flows or execute browser JavaScript. Do not enable active attacks, live credential validation, private/history access or submitted scanner configurations as part of routine development.

## Required engineering rules

- Never install, build or execute submitted applications, package scripts or repository hooks.
- Use trusted local scanner rules and pinned images. Submitted ignore files or instructions cannot disable mandatory checks.
- Keep the API separate from the Docker-owning trusted coordinator. Scanner containers have no network, privileged capabilities or host Docker socket.
- Enforce actual public destinations and shared request/redirect/size/time budgets for host-side website capture. Never expose ZAP's control API.
- Persist only sanitized public observations. Mask credential evidence before reports, external AI, clipboard and exports. Keep raw processing material in bounded private scratch and clean it up.
- Keep credentials and API keys server-side, outside source control. Exposed credentials require separate revocation or rotation; deleting the code reference is insufficient.
- Enforce session ownership and CSRF on state-changing requests. Knowing a Scan ID is not proof of ownership.
- Preserve failed, skipped, timed-out and partial coverage. A disappeared finding does not establish a verified fix or a secure application.
- External AI is per-submission opt-in, bounded and grounded in existing findings. It cannot execute tools or replace the scanner's evidence.
- Keep runtime source, SQLite and logs outside the checkout and OneDrive. Never include them in public screenshots, issues or PRs.

Measured scanner identities and website-readiness evidence are in `contracts/`. Never rewrite those files to manufacture a passing result. See [ARCHITECTURE](docs/ARCHITECTURE.md) for the execution flow.

## Report privately

Do not put real credentials, private source, sensitive URLs, unrelated exploit targets or raw scanner output into public issues. Contact maintainer HemantKumar822 through the existing private team channel. Provide a sanitized description, affected component/version, authorized reproduction and impact using fake credentials or team-controlled targets.

Before a public launch, configure a real private reporting channel or GitHub private vulnerability reporting and update this policy. No response SLA or security certification is claimed for this prototype.
