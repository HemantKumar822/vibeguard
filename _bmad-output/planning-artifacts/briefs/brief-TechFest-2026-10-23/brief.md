---
title: 'CY-02 AI Security Reviewer — Product Brief'
status: final
created: 2026-10-23
updated: 2026-10-23
workflow: bmad-product-brief
agent: Mary
mode: headless-create
approval: pending-user-review
---

# Product brief: AI Security Reviewer

**Ready for John's PRD as a planning input; technical feasibility remains unproven.**

## Purpose and users

Build a graphical security reviewer for developers shipping AI-built websites in the CY-02 hackathon. It accepts a **full codebase, repository, or deployed website URL**, returns evidence-backed candidate findings, explains their impact, generates one repair prompt for the developer's coding tool, and compares findings before and after changes. **Deployed URL checks use OWASP ZAP.** All three intake paths are required by the user; ZIP is an optional transport choice, not the product boundary.

The primary user is a developer who can build and deploy a website but needs help finding exposed credentials, unsafe input handling, insecure configuration, and possible missing access checks. The immediate audience is the hackathon team and evaluators. [ASSUMPTION A1] Start with JavaScript/TypeScript source and common React, Vite, Next.js and Node patterns; this is a coverage choice, not a market-share claim.

## Problem and proposed value

A working interface can conceal security mistakes. Raw scanner warnings leave the developer to judge relevance, locate evidence, translate advice into changes, and establish whether the same checks still detect the issue. The proposed value is a complete evidence → explanation → repair instruction → repeat-check workflow, presented in one usable workspace.

Existing products already provide scanning and AI-assisted remediation. Our proposed distinction is the focused combination of three intake paths, masked evidence, a portable repair prompt, and transparent comparison. This is an execution hypothesis, not a demonstrated competitive advantage. [Official product context](https://snyk.io/product/snyk-code/).

## Required experience

1. **Submit and scan:** select Codebase, Repository, or Website URL; see accepted scope and actual per-tool progress. [ASSUMPTION A2] Codebase intake supports a bounded folder/file-tree upload; repository intake starts with a public GitHub HTTPS snapshot at a recorded commit. Private repositories and history scanning are deferred, pending user correction.
2. **Investigate and repair:** filter findings by severity, category and tool; inspect masked evidence, confidence and limits; copy one consolidated repair prompt. Source evidence identifies a file and line. ZAP observations identify a URL and response/header or other available evidence location; source locations are never invented.
3. **Rescan and compare:** submit an updated codebase or repository revision, or rescan the authorized website. Show still detected, not detected, newly detected, and unverified findings with comparable coverage. Removal of a warning does not establish a verified repair or credential rotation.

Source and repository submissions use Gitleaks and Semgrep. Under A3, website submissions use ZAP baseline/passive checks with a bounded crawl. A URL alone cannot reveal private server source or establish complete authorization coverage. ZAP's baseline spiders the site and passively analyzes responses; it still generates live requests. [ZAP baseline](https://www.zaproxy.org/docs/docker/baseline-scan/).

## Scope and boundaries

**Required:** assess only code, repositories and sites the team is authorized to assess; all three submission paths; real scanner output; severity and confidence; masked evidence; plain-language impact and fixes; one copyable repair prompt with verification steps; deterministic guidance when AI is unavailable; genuine rescans; visible incomplete coverage; responsive, keyboard-usable graphical UI. Preserve an explicit revoke/rotate reminder for potentially exposed private credentials.

**[ASSUMPTION A3] Bounded URL MVP:** public HTTP(S) targets the team is authorized to assess, ZAP baseline/passive only, no authenticated sessions or active exploitation. Destination restrictions and isolated execution are release conditions for URL scanning. If these conditions fail, report URL capability as incomplete; do not silently remove it from required scope.

**Optional:** dependency scanning with Trivy, additional languages/rules, archive upload as an additional codebase transport, private repository authentication, source history analysis, and linked source-plus-URL scans. Trivy is provisional stretch scope because the packs disagree; the user has not required it.

**Excluded:** executing submitted apps, builds or install scripts; autonomous code changes; unrestricted shell agents; active penetration testing under A3; fake security scores; claims of exhaustive detection or security certification. The product remains a graphical workspace with three phases, not a chat-first application. Visual tokens remain for Sally's UX stage; no supplied `DESIGN.md` exists.

## Demonstration and evaluation

Plan a controlled vulnerable → corrected → clean fixture set covering source upload, public repository import, and a team-controlled deployed ZAP target. Record expected rule/alert IDs and locations for credential, input-handling, configuration, and selected access-check cases; document unsupported cases. Use fake secrets and a deliberately public key control.

The acceptance target is: **all three required intake paths complete controlled fixture scans with real, attributed results**; repaired fixtures are rescanned; failed or changed coverage never yields a fixed claim; repair prompts contain the reported locations and useful checks; secret-like values are absent from persisted reports, logs, model payloads, UI and clipboard outputs under the test corpus. Separately test timeout, invalid output, offline AI and redirection/internal-destination rejection: failures must be visible, and an incomplete path does not satisfy delivery.

Measure expected detections, false positives/negatives, correction outcomes, completed coverage and elapsed runtime on the demo machine. Have a teammate assess guidance clarity, prompt usefulness and fix verification against the fixture expectations. Do not publish an accuracy percentage or speed guarantee before measurement. Detailed gates and deferred decisions are in [addendum.md](addendum.md).

## Handoff

The next stage turns these boundaries into numbered requirements and testable acceptance criteria, resolves assumptions, and retains all three intake paths. UX then specifies the interactions; architecture resolves contracts, runtime and execution policy before stories. No implementation, repository creation, or GitHub issue publication has occurred during this stage.
