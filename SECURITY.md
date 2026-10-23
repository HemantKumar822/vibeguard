# Security reporting and safe development

This prototype reviews untrusted code and authorized websites. Its own input, worker, network, secret-handling and report-access boundaries are release-critical. Planning documents are not evidence those boundaries work.

## Report privately

Do not put live credentials, private source, sensitive URLs, exploit details against unrelated sites or raw scanner output into public issues/PRs. For the pre-publication team workspace, contact the team lead through the existing private team channel. Before a public launch, configure a real private reporting channel or GitHub private vulnerability reporting and update this file; no email address or response SLA is invented here.

Share a sanitized description, affected component/version, authorized reproduction steps and impact. Use fake credentials and team-controlled targets. The generic bug template is for nonsensitive defects only.

## Required boundaries

- Do not execute submitted applications, install scripts, builds or repository hooks.
- Apply trusted scanner rules, finite limits and worker isolation; permission confirmation is not containment.
- Route website/asset traffic through tested actual-destination and budget controls. Never expose ZAP's control API publicly.
- Sanitize evidence before persistence, logging, model calls, clipboard, screenshots and user output.
- Keep private credentials server-side. If a real credential was exposed, revoke/rotate it separately from removing the code reference.
- Do not label incomplete checks as clean or a disappeared finding as verified fixed.

The [architecture safety profile](_bmad-output/planning-artifacts/architecture/architecture-TechFest-2026-10-23/SAFETY-PROFILE.md) and each story's acceptance criteria define the implementation gates. Only scan targets the team is authorized to assess.
