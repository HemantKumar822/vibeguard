"""Create/resume the authorized five delivery milestones and epic labels."""
import json
from pathlib import Path
from publish_github_issues import api, REPO, PACKAGE

MILESTONES = [
    ('M1 — Safe source review', 'Deliver a real source-tree scan, private bounded jobs, masked findings and a deterministic repair prompt. Complete Epic 1 stories 1.1–1.5. Start with Story 1.1; later work follows recorded dependencies.'),
    ('M2 — Repository review', 'Deliver public GitHub snapshot retrieval, resolved commit attribution and the shared evidence workspace. Complete Epic 2 stories 2.1–2.2 after their source prerequisites. Can proceed alongside the website milestone once prerequisites are met.'),
    ('M3 — Website review with OWASP ZAP', 'Deliver enforced website networking, actual ZAP passive observations, visible-asset secret checks and the shared report. Complete Epic 3 stories 3.1–3.4. Begin egress feasibility after 1.3; do not wait for M2 to finish.'),
    ('M4 — Repair guidance and real rescans', 'Deliver opt-in grounded AI with deterministic fallback, genuine repeat scans and paired evidence. Complete Epic 4 stories 4.1–4.3. AI is not a prerequisite for comparison; all three scan modes remain required for final completion.'),
    ('M5 — Validated hackathon demo', 'Complete Epic 5 stories 5.1–5.2: labeled per-mode acceptance, adversarial and leakage checks, observed metrics, accessible recovery and a rehearsed operator guide. No invented due date or unmeasured delivery commitment.'),
]


def main():
    assert api('user')['login'] == 'HemantKumar822'
    assert api('repos/' + REPO)['private']
    record_path = PACKAGE / 'publication.json'
    record = json.loads(record_path.read_text(encoding='utf-8'))
    manifest = json.loads((PACKAGE / 'manifest.json').read_text(encoding='utf-8'))
    existing = api(f'repos/{REPO}/milestones?state=all&per_page=100')
    labels = api(f'repos/{REPO}/labels?per_page=100')
    milestones = {}
    for eid, (title, description) in enumerate(MILESTONES, 1):
        matches = [m for m in existing if m['title'] == title]
        assert len(matches) <= 1
        milestone = matches[0] if matches else api(f'repos/{REPO}/milestones', 'POST', {
            'title': title, 'description': description, 'state': 'open'})
        milestones[str(eid)] = {'number': milestone['number'], 'title': title, 'url': milestone['html_url']}
        label = f'epic:{eid}'
        if not any(x['name'] == label for x in labels):
            api(f'repos/{REPO}/labels', 'POST', {'name': label, 'color': ['0052CC','0E8A16','D93F0B','5319E7','006B75'][eid-1],
                'description': title.split(' — ', 1)[1]})
    for item in manifest['items']:
        eid = item['key'].split('-')[1] if item['kind'] == 'epic' else item['parent'].split('-')[1]
        number = record['issues'][item['key']]['number']
        issue = api(f'repos/{REPO}/issues/{number}')
        names = [label['name'] for label in issue['labels']]
        names = list(dict.fromkeys(names + [f'epic:{eid}']))
        api(f'repos/{REPO}/issues/{number}', 'PATCH', {'milestone': milestones[eid]['number'], 'labels': names})
        record['issues'][item['key']]['milestone'] = milestones[eid]['number']
    issues = api(f'repos/{REPO}/issues?state=all&per_page=100')
    assert len([i for i in issues if 'pull_request' not in i]) == 21
    for item in manifest['items']:
        identity = record['issues'][item['key']]
        issue = next(i for i in issues if i['number'] == identity['number'])
        assert issue['milestone']['number'] == identity['milestone']
    assert api(f"repos/{REPO}/issues/{record['issues']['1.1']['number']}/dependencies/blocked_by") == []
    for eid in range(1, 6):
        parent = record['issues'][f'epic-{eid}']['number']
        children = api(f'repos/{REPO}/issues/{parent}/sub_issues')
        expected = [record['issues'][item['key']]['number'] for item in manifest['items'] if item.get('parent') == f'epic-{eid}']
        assert sorted(i['number'] for i in children) == sorted(expected)
    record['milestones'] = milestones
    record_path.write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
    print('PASS: five milestones, all 21 issues assigned, five epic trees verified, Story 1.1 unblocked.', flush=True)


if __name__ == '__main__':
    main()
