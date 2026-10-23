"""Check shareable project preparation using Python stdlib and Git only.

Checks local documents, canonical story acceptance, dependencies, draft issue
manifest, tracker keys and ignore behavior. Never initializes the project Git
repository, contacts a remote or claims application tests passed.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'_bmad-output'


def run(args: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args,cwd=ROOT,text=True,capture_output=True,**kwargs)


def ensure(condition: object, message: str) -> None:
    if not condition:
        raise ValueError(message)


def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',help='Optional JSON report path inside this workspace')
    args=parser.parse_args()
    git=shutil.which('git')
    ensure(git,'Git is required to verify actual ignore behavior')
    backlog=json.loads((OUT/'planning-artifacts/backlog.json').read_text(encoding='utf-8-sig'))
    manifest=json.loads((OUT/'github-issues/manifest.json').read_text(encoding='utf-8-sig'))
    ensure(manifest['publication_status'] in ('not-published','published'),'Unknown publication state')
    if manifest['publication_status']=='published':
        publication=json.loads((OUT/'github-issues/publication.json').read_text(encoding='utf-8'))
        expected_remote=16 if publication.get('tracking_model')=='milestones-and-stories-only' else 21
        ensure(publication['status']=='published' and len(publication['issues'])==expected_remote,'Incomplete publication record')
        ensure(all(v.get('url') and v.get('number') for v in publication['issues'].values()),'Missing published issue identities')
        if 'milestones' in publication:
            ensure(len(publication['milestones'])==5,'Expected five delivery milestones')
            milestone_numbers={m['number'] for m in publication['milestones'].values()}
            ensure(all(v.get('milestone') in milestone_numbers for v in publication['issues'].values()),'An issue has no recorded delivery milestone')
    items={item['key']:item for item in manifest['items']}
    ensure(len(items)==21 and len(manifest['items'])==21,'Expected 5 unique epics and 16 unique story drafts')
    stories=backlog['stories']; ids=[s['id'] for s in stories]; incoming={s['id']:s['depends_on'] for s in stories}
    ensure(len(stories)==16 and len(set(ids))==16,'Canonical stories missing or duplicated')
    done=set()
    tracker=(OUT/'implementation-artifacts/sprint-status.yaml').read_text(encoding='utf-8-sig')
    paths=[]; story_paths=[]; total_acceptance=0; eligible=[]
    required_sections=['Summary','User story','Requirements and source of truth','Dependencies',
                       'In scope / implementation checklist','Out of scope','Acceptance criteria',
                       'Verification plan','Definition of done','Implementation record']
    keys={}
    for index,story in enumerate(stories):
        sid=story['id']; item=items[sid]
        ensure(item['depends_on']==incoming[sid],f'{sid}: manifest dependency drift')
        ensure(all(d in ids[:index] for d in incoming[sid]),f'{sid}: missing/forward dependency')
        expected_blocks=[s['id'] for s in stories if sid in s['depends_on']]
        ensure(item['blocks']==expected_blocks,f'{sid}: reverse dependency drift')
        ensure(item['parent']==f"epic-{story['epic']}",f'{sid}: wrong epic parent')
        source=ROOT/item['source_file']; body=source.read_text(encoding='utf-8-sig')
        story_paths.append(source); paths.extend([source,ROOT/item['body_file']])
        ensure(all('## '+section in body for section in required_sections),f'{sid}: missing handoff section')
        dep_match=re.search(r'^depends_on: (.+)$',body,re.M)
        ensure(dep_match and json.loads(dep_match[1])==incoming[sid],f'{sid}: handoff dependency drift')
        ensure(story['requirements'] in body,f'{sid}: requirement references changed')
        ensure(len(re.findall(r'^- \[ \] \*\*AC-\d+\*\*',body,re.M))==len(story['acceptance_criteria']),f'{sid}: acceptance count drift')
        for ac in story['acceptance_criteria']:
            ensure(ac[2:] in body,f'{sid}: canonical acceptance altered')
        total_acceptance+=len(story['acceptance_criteria'])
        key=source.stem; keys[sid]=key
        statuses=re.findall(r'^  '+re.escape(key)+r': (backlog|ready-for-dev|in-progress|review|done)$',tracker,re.M)
        ensure(len(statuses)==1,f'{sid}: tracker missing/duplicate key')
        if statuses[0]=='done':done.add(sid)
        ensure('[Story '+sid in (ROOT/item['body_file']).read_text(encoding='utf-8-sig') or '# Story '+sid in (ROOT/item['body_file']).read_text(encoding='utf-8-sig'),f'{sid}: incorrect draft body')
    for story in stories:
        if all(d in done for d in incoming[story['id']]) and story['id'] not in done:
            eligible.append(story['id'])
    actual=sorted(p.name for p in (OUT/'implementation-artifacts').glob('*.md') if re.match(r'^\d+-\d+-',p.name))
    ensure(actual==sorted(p.name for p in story_paths),'Unexpected or missing story handoff files')
    for eid in range(1,6):
        item=items[f'epic-{eid}']; paths.append(ROOT/item['body_file'])
        ensure(item['children']==[s['id'] for s in stories if s['epic']==eid],f'Epic {eid}: wrong children')
    paths += [ROOT/'README.md',ROOT/'CONTRIBUTING.md',ROOT/'SECURITY.md',
              ROOT/'docs/PROJECT_RULES.md',ROOT/'docs/REPOSITORY_SETUP.md',ROOT/'docs/TEAM_DELIVERY.md',
              OUT/'README.md',OUT/'repository-preparation/README.md',
              OUT/'github-issues/README.md',OUT/'implementation-artifacts/README.md',ROOT/'.github/pull_request_template.md']
    paths += list((ROOT/'.github/ISSUE_TEMPLATE').glob('*.md'))
    local_links=0
    for path in paths:
        text=path.read_text(encoding='utf-8-sig')
        for target in re.findall(r'\]\(([^)]+)\)',text):
            if target.startswith(('https://','http://','mailto:','#')):continue
            target=target.split('#',1)[0].strip('<>')
            ensure((path.parent/target).exists(),f'Broken local link in {path.relative_to(ROOT)}: {target}')
            local_links+=1

    ignored=['.agents/skills/example/SKILL.md','.agent/local.md','agents/local.md','skills/local.md',
             '_bmad/config.toml','.claude/config.json','.codex/config.toml','.cursor/rules/local.mdc',
             '.opencode/config.json','.github/agents/example.agent.md','.github/instructions/local.md',
             'AGENTS.md','backend/AGENTS.md','CLAUDE.md','.env','.env.production','backend/.env',
             'credentials.json','private.key','node_modules/example/index.js','.venv/pyvenv.cfg',
             'runtime/job/raw.json','scan-data/input.js','scanner-output/raw.json','uploads/source.ts',
             'reports/raw.json','scan.sqlite3','example.log','frontend/dist/index.html',
             '_bmad-output/example/.working/mock.html','_bmad-output/example/.runtime-cache/cache.json']
    shared=['README.md','CONTRIBUTING.md','SECURITY.md','.gitignore','.gitattributes','.env.example',
            'docs/PROJECT_RULES.md','.github/pull_request_template.md','.github/ISSUE_TEMPLATE/user_story.md',
            'frontend/package-lock.json','backend/uv.lock','scripts/validate_repo_preparation.py',
            '_bmad-output/planning-artifacts/epics.md','_bmad-output/planning-artifacts/backlog.json',
            '_bmad-output/implementation-artifacts/sprint-status.yaml',
            '_bmad-output/planning-artifacts/briefs/brief-TechFest-2026-10-23/.memlog.md',
            '_bmad-output/planning-artifacts/briefs/brief-TechFest-2026-10-23/sources/CY-02.png']
    shared += [p.relative_to(ROOT).as_posix() for p in paths]
    # A workspace-local ignored cache also works in managed shells whose TEMP
    # points to an inaccessible sandbox package directory.
    scratch_parent=(OUT/'.runtime-cache').resolve()
    scratch_parent.mkdir(parents=True,exist_ok=True)
    scratch=Path(tempfile.mkdtemp(prefix='techfest-ignore-',dir=scratch_parent)).resolve()
    ensure(scratch.is_relative_to(scratch_parent) and scratch!=scratch_parent,'Unsafe temporary Git target')
    try:
        init=run([git,'-c','init.templateDir=','init','--bare','--quiet',str(scratch)])
        ensure(init.returncode==0,'Cannot initialize disposable ignore-policy test directory: '+init.stderr)
        command=[git,'--git-dir='+str(scratch),'--work-tree='+str(ROOT),'-c','core.bare=false','-c','core.excludesFile=','check-ignore','--no-index','--quiet','--']
        for path in dict.fromkeys(ignored+shared):
            outcome=run(command+[path])
            ensure(outcome.returncode in (0,1),'Git ignore check failed: '+outcome.stderr)
            ensure((outcome.returncode==0)==(path in ignored),'Unexpected ignore policy for '+path)
        preview=run([git,'--git-dir='+str(scratch),'--work-tree='+str(ROOT),'-c','core.bare=false',
                     '-c','core.excludesFile=','ls-files','--others','--exclude-standard','-z'])
        ensure(preview.returncode==0,'Cannot inspect actual shareable-file preview')
        shareable=sorted(filter(None,preview.stdout.split('\0')))
        forbidden_prefixes=('.agents/','.agent/','agents/','skills/','_bmad/','.claude/','.codex/',
                            '.cursor/','.opencode/','.github/agents/','.github/instructions/')
        ensure(not any(p.startswith(forbidden_prefixes) for p in shareable),'Actual preview contains local agent/tool files')
        ensure('_bmad-output/planning-artifacts/epics.md' in shareable,'Generated planning output missing from preview')
        ensure(all(p.relative_to(ROOT).as_posix() in shareable for p in paths),'A prepared team document is excluded from preview')
    finally:
        ensure(scratch.resolve().is_relative_to(scratch_parent) and scratch!=scratch_parent,'Unsafe cleanup target')
        shutil.rmtree(scratch)

    # Ignore rules do not untrack already-indexed files. Inspect the actual index if present.
    repo=run([git,'rev-parse','--show-toplevel'])
    tracked_audit='not applicable: project Git is not initialized'
    if repo.returncode==0 and Path(repo.stdout.strip()).resolve()==ROOT:
        tracked=run([git,'ls-files','-z'])
        ensure(tracked.returncode==0,'Cannot inspect project tracked paths')
        for path in filter(None,tracked.stdout.split('\0')):
            check=run([git,'-c','core.excludesFile=','check-ignore','--no-index','--quiet','--',path])
            ensure(check.returncode==1,'Ignored/private artifact is already tracked: '+path)
        tracked_audit='PASS: no ignored artifacts already tracked'
    report={'result':'PASS','stories':len(stories),'epic_issue_drafts':5,'story_issue_drafts':16,
            'canonical_acceptance_criteria':total_acceptance,'dependency_and_reverse_links':'PASS',
            'local_markdown_links':local_links,'ignore_policy_cases':len(set(ignored+shared)),
            'shareable_file_count':len(shareable),'shareable_files':shareable,
            'dependency_clear_foundation_stories':eligible,'tracked_file_audit':tracked_audit,
            'dependency_policy':'Informational guidance; coordinated parallel work is permitted and no native GitHub blockers are used',
            'project_git_created':False,'remote_actions':False,
            'limitations':'Preparation checks only; no application/security acceptance tests or remote publication.'}
    if args.output:
        destination=(ROOT/args.output).resolve()
        ensure(destination.is_relative_to(ROOT),'Report must stay inside workspace')
        destination.parent.mkdir(parents=True,exist_ok=True)
        destination.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k!='shareable_files'},indent=2))
    return 0


if __name__=='__main__':
    try:
        raise SystemExit(main())
    except (ValueError,OSError,KeyError,json.JSONDecodeError) as error:
        print('Preparation check failed: '+str(error))
        raise SystemExit(1)
