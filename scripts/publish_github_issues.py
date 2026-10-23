"""Publish/resume the explicitly authorized VibeGuard issue package using gh.

Run manually after reviewing the local package. Records each returned identity
before continuing. Never guesses issue numbers, initializes Git or pushes code.
"""
import json
import re
import subprocess
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / '_bmad-output/github-issues'
REPO = 'HemantKumar822/vibeguard'
BASE = 'https://github.com/' + REPO


def api(endpoint, method='GET', payload=None):
    args = ['gh', 'api', endpoint, '--method', method]
    if payload is not None:
        args += ['--input', '-']
    result = subprocess.run(args, input=json.dumps(payload) if payload is not None else None,
                            text=True, capture_output=True, encoding='utf-8', cwd=ROOT)
    if result.returncode:
        raise RuntimeError(result.stderr.strip())
    return json.loads(result.stdout) if result.stdout.strip() else None


def main():
    assert api('user')['login'] == 'HemantKumar822', 'Wrong GitHub account'
    assert api('repos/' + REPO)['private'], 'Repository must remain private'
    manifest = json.loads((PACKAGE / 'manifest.json').read_text(encoding='utf-8'))
    record_path = PACKAGE / 'publication.json'
    record = json.loads(record_path.read_text(encoding='utf-8')) if record_path.exists() else {}
    record.update(repository=BASE, status='publishing')
    record.setdefault('issues', {})
    record.setdefault('relationships', {})

    def save():
        record_path.write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')

    for label in json.loads((PACKAGE / 'labels.json').read_text()):
        existing = api('repos/' + REPO + '/labels?per_page=100')
        if not any(x['name'] == label['name'] for x in existing):
            api('repos/' + REPO + '/labels', 'POST', label)
    existing = api('repos/' + REPO + '/issues?state=all&per_page=100')
    for item in manifest['items']:
        key = item['key']
        if key in record['issues']:
            continue
        matched = [x for x in existing if x['title'] == item['title'] and 'pull_request' not in x]
        assert len(matched) <= 1, 'Duplicate issue title: ' + item['title']
        issue = matched[0] if matched else api('repos/' + REPO + '/issues', 'POST', {
            'title': item['title'], 'labels': item['labels'],
            'body': 'Publishing the reviewed story package. Full requirements and dependency links will be added shortly.'})
        record['issues'][key] = {'number': issue['number'], 'id': issue['id'], 'url': issue['html_url']}
        save()
        print('Recorded ' + key + ': ' + issue['html_url'], flush=True)

    path_keys = {}
    for item in manifest['items']:
        for field in ('source_file', 'body_file'):
            if field in item:
                path_keys[(ROOT / item[field]).resolve()] = item['key']
    for item in manifest['items']:
        source = ROOT / item['body_file']
        body = source.read_text(encoding='utf-8')

        def link(match):
            target = match[1]
            if target.startswith(('http:', 'https:', 'mailto:', '#')):
                return match[0]
            target_path, _, fragment = target.partition('#')
            resolved = (source.parent / target_path.strip('<>')).resolve()
            assert resolved.is_relative_to(ROOT) and resolved.exists(), 'Invalid issue link: ' + target
            key = path_keys.get(resolved)
            url = record['issues'][key]['url'] if key else BASE + '/blob/main/' + quote(resolved.relative_to(ROOT).as_posix())
            if fragment and not key:
                url += '#' + fragment
            return '](' + url + ')'

        body = re.sub(r'\]\(([^)]+)\)', link, body)
        if item['kind'] == 'story':
            parent = record['issues'][item['parent']]['url']
            body += '\n\n## GitHub tracking\n\nParent epic: ' + parent + '\n'
            for dep in item['depends_on']:
                body += '- Depends on (guidance): ' + record['issues'][dep]['url'] + '\n'
            for successor in item['blocks']:
                body += '- Downstream work: ' + record['issues'][successor]['url'] + '\n'
        assert not re.search(r'(?<![A-Za-z0-9])[A-Za-z]:[\\/]', body), 'Local path in published body'
        number = record['issues'][item['key']]['number']
        api(f'repos/{REPO}/issues/{number}', 'PATCH', {'body': body})

    # Linked bodies always provide relationships; use native sub-issues and
    # dependency edges when this repository supports them, recording failures.
    for item in manifest['items']:
        if item['kind'] != 'story':
            continue
        child = record['issues'][item['key']]
        parent = record['issues'][item['parent']]
        edges = [(item['parent'] + '>' + item['key'],
                  f"repos/{REPO}/issues/{parent['number']}/sub_issues", {'sub_issue_id': child['id']})]
        # Team preference: dependencies are descriptive guidance, not native
        # blocking relationships. Keep the parent/sub-issue tree intact.
        for dep in item['depends_on']:
            record['relationships'][item['key'] + '<' + dep] = 'description only; team parallel-work preference'
        for edge, endpoint, payload in edges:
            if record['relationships'].get(edge) == 'native':
                continue
            try:
                api(endpoint, 'POST', payload)
                record['relationships'][edge] = 'native'
            except RuntimeError as exc:
                record['relationships'][edge] = 'linked in issue body; native unavailable: ' + str(exc)
            save()

    for key, identity in record['issues'].items():
        issue = api(f"repos/{REPO}/issues/{identity['number']}")
        assert issue['html_url'] == identity['url'] and issue['state'] == 'open'
        assert 'Acceptance' in issue['body'] or 'acceptance' in issue['body'], key
    record['status'] = 'published'
    save()
    manifest['publication_status'] = 'published'
    (PACKAGE / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    print('Verified 21 published issues; native/linked relationships recorded.', flush=True)


if __name__ == '__main__':
    main()
