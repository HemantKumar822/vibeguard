"""Apply the user's milestone-only tracking choice; remove duplicate epic issues."""
import json
import re
import subprocess
from concurrent.futures import ThreadPoolExecutor
from publish_github_issues import api, REPO, PACKAGE


def main():
    assert api('user')['login'] == 'HemantKumar822'
    assert api(f'repos/{REPO}')['private']
    path = PACKAGE / 'publication.json'
    record = json.loads(path.read_text(encoding='utf-8'))
    if record.get('tracking_model') == 'milestones-and-stories-only':
        print('Milestone-only migration already complete; no changes made.')
        return
    record.setdefault('removed_epic_issues', {})
    epics = {k: v for k, v in record['issues'].items() if k.startswith('epic-')}
    stories = {k: v for k, v in record['issues'].items() if not k.startswith('epic-')}

    def update(pair):
        key, identity = pair
        issue = api(f"repos/{REPO}/issues/{identity['number']}")
        assert issue['title'].startswith('[Story ' + key + ']') and issue['state'] == 'open'
        milestone = record['milestones'][key.split('.')[0]]
        body = issue['body']
        for ekey, epic in epics.items():
            m = record['milestones'][ekey.split('-')[1]]
            body = re.sub(re.escape(epic['url']) + r'(?=[)#\s]|$)', m['url'], body)
        body = body.replace('Parent epic:', 'Delivery milestone:')
        labels = [x['name'] for x in issue['labels'] if not x['name'].startswith('epic:')]
        api(f"repos/{REPO}/issues/{identity['number']}", 'PATCH',
            {'body': body, 'labels': labels, 'milestone': milestone['number']})
        assert api(f"repos/{REPO}/issues/{identity['number']}/dependencies/blocked_by") == []

    with ThreadPoolExecutor(max_workers=4) as pool:
        list(pool.map(update, stories.items()))
    for key, identity in epics.items():
        issue = api(f"repos/{REPO}/issues/{identity['number']}")
        assert issue['title'].startswith('[Epic ' + key.split('-')[1] + ']'), 'Wrong deletion target'
        subprocess.run(['gh', 'issue', 'delete', str(identity['number']), '--repo', REPO, '--yes'], check=True)
        record['removed_epic_issues'][key] = {**identity, 'status': 'deleted at user request; replaced by milestone'}
        del record['issues'][key]
        path.write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
    actual = [x for x in api(f'repos/{REPO}/issues?state=all&per_page=100') if 'pull_request' not in x]
    assert len(actual) == 16 and all(x['state'] == 'open' and x['milestone'] for x in actual)
    assert all(not x['title'].startswith('[Epic ') for x in actual)
    milestones = api(f'repos/{REPO}/milestones?state=all&per_page=100')
    assert len(milestones) == 5
    assert sorted(x['open_issues'] for x in milestones) == [2, 2, 3, 4, 5]
    record['tracking_model'] = 'milestones-and-stories-only'
    record['relationships'] = {k: v for k, v in record['relationships'].items() if '<' in k}
    path.write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
    print('PASS: only 16 open story issues remain, grouped in 5 milestones; duplicate epic issues deleted; no blockers.', flush=True)


if __name__ == '__main__':
    main()
