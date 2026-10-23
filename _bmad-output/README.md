# Shared project documents

Start with the [team story board](github-issues/README.md). It links all five epics and 16 detailed stories, with dependencies and proposed owner roles. Story 1.1 is the recommended foundation; all GitHub issues remain open for coordinated parallel work.

## Planning and delivery

- [Canonical epics/acceptance](planning-artifacts/epics.md)
- [Individual implementation handoffs](implementation-artifacts/README.md)
- [Sprint tracker](implementation-artifacts/sprint-status.yaml)
- [Planning readiness](planning-artifacts/implementation-readiness.md)
- [Workflow progress](workflow-status.md)
- [Repository preparation checks](repository-preparation/README.md)

The repository [README](../README.md) links the brief, PRD, UX, architecture, API and safety contracts. Original research packs are preserved under the brief's sources folder for provenance; user corrections and finalized planning govern their older conflicting scope proposals.

## What this folder means

This folder is deliberately shared with teammates. Local BMAD source, installed agents and skills are excluded separately; teammates can read and implement the stories without those installations. Runtime/private scan data and temporary authoring caches do not belong in this folder's published content.

All stories are currently prepared, not implemented. `ready-for-dev` means the handoff exists; actual start eligibility also requires its dependencies to be done. Published GitHub issue identities are in [the publication record](github-issues/publication.json). Local issue-body files remain authoring sources; GitHub issues track team work.
