# Contributing

Start from the [story board](_bmad-output/github-issues/README.md). Every story has a readable handoff with scope, requirements, dependencies, acceptance criteria and verification. The [development guide](docs/DEVELOPMENT.md) contains the bootstrap's actual setup/build/test commands; scanning is not implemented yet.

## Pick and claim work

1. Check the [sprint tracker](_bmad-output/implementation-artifacts/sprint-status.yaml) and the story's **Dependencies** section.
2. Claim one story with the team. Once GitHub issues exist, assign its issue to one accountable owner; additional collaborators are welcome.
3. Dependencies guide integration order. Coordinate contracts and ownership when working in parallel; finish required integration and acceptance checks before closing a story.
4. Use a focused branch such as `feat/1-2-source-intake`, `fix/3-1-redirect-check` or `docs/5-2-demo-guide`. Prefer small PRs; avoid mixing unrelated stories.

## Build within the contract

Read the linked PRD, architecture decisions and UX sections before implementation. Backend owns one generated OpenAPI contract; frontend consumes its generated types. Do not introduce a UI-only or scanner-specific public schema. Change a shared contract explicitly, update its fixtures/types, and tell affected owners before merging.

Create only the tables/modules needed for the current story. Do not run uploaded code, installs, builds or hooks. Do not give an API/scanner container the Docker socket. External AI is opt-in and receives bounded sanitized evidence only. See the [project rules](docs/PROJECT_RULES.md) for the complete guardrails.

## Verify and open a pull request

Run `python scripts/validate_repo_preparation.py` for documentation/backlog changes. After Story 1.1, README and contributor instructions must list the real build/type/test commands introduced by the scaffold. Do not record a command as passing unless it was run.

For code changes, run checks appropriate to the story, including its positive and failure cases. Add a concise test record: command, outcome and relevant evidence. Raw credentials/source/vendor output never belong in screenshots, logs, comments or fixtures.

Use the [PR template](.github/pull_request_template.md). Include the story ID and, after publication, a real issue link. Use `Closes #...` only when the entire issue's acceptance criteria are met; use a nonclosing reference for partial work. Do not invent issue numbers.

Commit subjects use `feat:`, `fix:`, `docs:`, `test:`, `refactor:` or `chore:` followed by the concrete change. This is a team convention, not an installed commit hook.

## Review and completion

- Obtain one teammate review before merge; use the review to check behavior, failure cases and shared boundaries. Remote branch protection will be configured later; it is not currently enforced.
- Resolve failing checks and blocking feedback. State unrun checks and limitations plainly.
- Complete all story acceptance criteria, record verification, update affected docs/contracts, and update the sprint tracker. Review-ready is distinct from done.
- If scope changes or a story is too large, split it before coding, retain requirement coverage and update dependencies/backlog/story handoffs together. Never quietly drop a required input mode or safety condition.

## Shared versus local files

Track `_bmad-output/`, application source, tests, fixtures with fake credentials, lockfiles and team documentation. Keep local agents/skills/BMAD installation, environment secrets, caches and runtime scan data out of Git. `.gitignore` does not remove files already tracked; the preparation validator checks for that separately once Git is initialized.

BMAD itself is optional local tooling, not a prerequisite for reading stories. Shared rules live here and in `docs/PROJECT_RULES.md`, not in a required agent installation. Preserve constructive, respectful review; focus feedback on behavior and evidence.
