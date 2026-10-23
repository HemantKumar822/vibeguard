# Repository preparation and publication

Local content preparation passed before the authorized publication to [HemantKumar822/vibeguard](https://github.com/HemantKumar822/vibeguard), a private team repository.

## Shared package

- Five epics and 16 detailed story handoffs: outcome, requirements, tasks, exclusions, dependencies, 54 canonical acceptance criteria, verification and definition of done.
- README, contributor/security guidance, project rules, environment example, Git attributes, issue and pull request templates.
- `.gitignore` keeps installed agents, skills, BMAD runtime source, credentials and runtime data local. Generated `_bmad-output/` plans remain shared.
- [Publication identities and relationship results](../github-issues/publication.json); local issue-body files are retained as authoring sources, not a separate live tracker.

## Validation and operating state

Run `python scripts/validate_repo_preparation.py --output _bmad-output/repository-preparation/checks.json`. The [latest report](checks.json) records actual counts, local links, dependency checks, ignore-policy cases and an audit of already-tracked files. The disposable ignore test does not initialize the project or contact GitHub.

All 16 stories are prepared; only Story 1.1 is initially unblocked. No application implementation, scanner acceptance, isolation, accessibility or detection result is claimed. No CI check or enforced branch protection is claimed. Those checks require working code and actual execution evidence. No license has been selected.

The regeneration script refuses to overwrite active stories or a published issue manifest. Update canonical planning, local handoffs and published issues deliberately when requirements change.

[Team board](../github-issues/README.md) · [Setup record](../../docs/REPOSITORY_SETUP.md)
