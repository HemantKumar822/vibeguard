# VibeGuard repository setup

The user authorized publication after local preparation. Destination: **HemantKumar822/vibeguard**, private. GitHub CLI account verified; the three named teammates were invited with Write access. This checklist records the publication process. Temporary Git directories used by the validator are disposable tests.

## Prepared locally

- Root README, contributor guide, project rules, security notes, environment example and Git attributes/ignore policy.
- Five epic issue drafts, 16 detailed story handoffs and a derived publication manifest in `_bmad-output/github-issues/`.
- Story requirements, acceptance criteria, dependency/blocking links and verification expectations.
- Issue/PR templates and a local preparation validator. No CI badge, branch rule, team assignment or issue number is claimed.

## Publication decisions

- Owner/name: HemantKumar822/vibeguard; visibility: private. No license has been selected; no license grant is implied.
- Maintainer: HemantKumar822. Write invitations: vatsanusha7-rgb, devanshisharma1208-droid, asadityasharma190907-afk. Story assignments remain unassigned until teammates choose owners.
- `gh api user` verified HemantKumar822 with network access. No credentials were replaced.
- Confirm the final planned publish list with `python scripts/validate_repo_preparation.py`. Installed agents/skills and BMAD runtime source must be absent; `_bmad-output/` documents must be included; credentials/runtime data must be absent.

## Execution order

1. Initialize local Git only when publication/setup is requested; run the validator again so tracked-file checks can run. Stage the intentional shareable files, inspect staged names and review a first commit.
2. Create the confirmed remote with the authenticated CLI, connect the remote and push the reviewed initial commit. Never use force push to repair setup automatically.
3. Create the manifest's labels and five epic issues, then 16 story issues. Preserve stable IDs in titles. Resolve generated local file links to real repository blob URLs before sending bodies; never publish local Windows paths or guessed issue numbers.
4. Store returned issue URLs/numbers, replace draft dependency references with real issue links and establish parent/dependency relationships supported by the account. Verify every native or linked dependency points to the intended story.
5. Add agreed collaborators/reviewers and configure the agreed merge/branch protections. Before claiming a required CI check, implement and run the actual check.
6. Audit problem statement → PRD → UX/architecture → stories → published issues. Check statuses, links, owners, blockers, ignore policy and README reality. Track any unresolved publishing task rather than declaring setup done.

See the [publication record](../_bmad-output/github-issues/publication.json) for actual issue identities and relationship results. [The draft package](../_bmad-output/github-issues/README.md) is reviewable without access to GitHub. Implementation begins with Story 1.1 after the team is ready; functional correctness is established during the build, not by repository creation.

## Team workflow settings

Squash merging and automatic deletion of merged branches are enabled; merge commits and rebase merging are disabled. Use feature branches and reviewed pull requests. CI and enforced branch protection are not installed or claimed; working build/test commands belong to Story 1.1. Collaborator invitations require each teammate to accept. No story owner is invented and no license is selected.
