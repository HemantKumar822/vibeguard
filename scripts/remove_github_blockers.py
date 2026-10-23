"""Remove native issue blockers while preserving epic trees and written guidance."""
import json
from concurrent.futures import ThreadPoolExecutor
from publish_github_issues import api, REPO, PACKAGE


def main():
    assert api('user')['login'] == 'HemantKumar822'
    assert api(f'repos/{REPO}')['private']
    path = PACKAGE / 'publication.json'
    record = json.loads(path.read_text(encoding='utf-8'))
    manifest = json.loads((PACKAGE / 'manifest.json').read_text(encoding='utf-8'))

    def remove(item):
        identity = record['issues'][item['key']]
        endpoint = f"repos/{REPO}/issues/{identity['number']}/dependencies/blocked_by"
        blockers = api(endpoint)
        for blocker in blockers:
            api(endpoint + '/' + str(blocker['id']), 'DELETE')
        assert api(endpoint) == [], 'A native blocker remains'
        issue = api(f"repos/{REPO}/issues/{identity['number']}")
        assert issue['state'] == 'open' and issue['milestone'], 'Issue must remain open and grouped'
        if item['kind'] == 'story':
            parent = record['issues'][item['parent']]['url']
            assert parent in issue['body'], 'Epic link missing'
        return len(blockers)

    with ThreadPoolExecutor(max_workers=4) as pool:
        removed = sum(pool.map(remove, manifest['items']))
    for key in list(record['relationships']):
        if '<' in key:
            record['relationships'][key] = 'description only; team parallel-work preference'
    for eid in range(1, 6):
        children = api(f"repos/{REPO}/issues/{record['issues'][f'epic-{eid}']['number']}/sub_issues")
        expected = [record['issues'][i['key']]['number'] for i in manifest['items'] if i.get('parent') == f'epic-{eid}']
        assert sorted(i['number'] for i in children) == sorted(expected)
    record['dependency_policy'] = 'Informational descriptions only. No native blocking relationships; all issues remain open for team coordination.'
    path.write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
    print(f'PASS: removed {removed} native blockers; all 21 issues open, milestone-assigned and unblocked; 5 epic trees preserved.', flush=True)


if __name__ == '__main__':
    main()
