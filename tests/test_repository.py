import io
import json
import tarfile
import time
from unittest.mock import Mock
import pytest
from backend.adapters import repository
from backend.api.session import IntakeError
from backend.core.contracts import RepositoryIntake
from test_intake import runtime


def archive(entries):
    output=io.BytesIO()
    with tarfile.open(fileobj=output,mode='w:gz') as tar:
        for name,content,kind in entries:
            member=tarfile.TarInfo(name); member.size=len(content)
            if kind=='link': member.type=tarfile.SYMTYPE; member.linkname='../escape'
            tar.addfile(member,io.BytesIO(content))
    return output.getvalue()


@pytest.mark.parametrize('url,ref',[
    ('https://user:password@github.com/owner/repo',None),('http://github.com/owner/repo',None),
    ('https://github.com.evil.test/owner/repo',None),('https://github.com/owner/repo?token=x',None),
    ('https://github.com/owner/repo','../main'),('https://github.com/owner/repo','-upload-pack=x'),
    ('https://github.com/owner/repo','x'*257),('file:///owner/repo',None)])
def test_unsafe_identity_rejected(url,ref):
    with pytest.raises(IntakeError): repository.identity(url,ref)


def test_extract_equivalent_inventory_and_exclusions(tmp_path):
    data=archive([('root/src/app.ts',b'const x=1','file'),('root/node_modules/pkg/a.js',b'x','file')])
    accepted,excluded=repository.extract(data,tmp_path,time.monotonic()+60)
    assert accepted==['src/app.ts']
    assert excluded==[{'resource_key':'node_modules/pkg/a.js','reason':'vendor_or_build_output'}]
    assert (tmp_path/'file_0').read_bytes()==b'const x=1'
    assert json.loads((tmp_path/'manifest.json').read_text())['files'][0]['relative_path']=='src/app.ts'


@pytest.mark.parametrize('entries',[
    [('root/../a.js',b'x','file')],[('root/link.js',b'','link')],
    [('root/a.js',b'x','file'),('root/A.js',b'y','file')],
    [('root/a.js',b'x','file'),('other/b.js',b'y','file')],
    [('root/a.js',b'x'*(2*1024*1024+1),'file')],
    [('root/a.js',b'x','file'),('root/a.js/b.ts',b'y','file')]])
def test_hostile_archives_rejected(tmp_path,entries):
    with pytest.raises((ValueError,IntakeError)): repository.extract(archive(entries),tmp_path,time.monotonic()+60)
    assert not list(tmp_path.iterdir())


def test_nonpublic_dns_fails_before_connect(monkeypatch):
    monkeypatch.setattr(repository.socket,'getaddrinfo',lambda *a,**kw:[(2,1,6,'',('127.0.0.1',443))])
    with pytest.raises(ValueError): repository.public_addresses('api.github.com')


def test_lfs_pointer_is_excluded_without_retrieval(tmp_path):
    data=archive([('root/app.ts',b'const x=1','file'),('root/large.js',b'version https://git-lfs.github.com/spec/v1\noid sha256:synthetic\nsize 123\n','file')])
    accepted,excluded=repository.extract(data,tmp_path,time.monotonic()+60)
    assert accepted==['app.ts'] and excluded[0]['reason']=='git_lfs_pointer_not_retrieved'


def test_redirect_is_not_followed(monkeypatch):
    connection=Mock(); response=Mock(status=302)
    response.getheader.return_value='identity'; connection.getresponse.return_value=response
    constructor=Mock(return_value=connection); monkeypatch.setattr(repository,'PinnedHTTPS',constructor)
    with pytest.raises(ValueError): repository.fetch('api.github.com','/repos/o/r',time.monotonic()+60,1000)
    assert constructor.call_count==1 and connection.request.call_count==1
    connection.close.assert_called_once()


def test_commit_resolution_fixed_endpoints_and_safe_failure(tmp_path,monkeypatch):
    sha='a'*40
    answers=[json.dumps({'private':False,'default_branch':'main'}).encode(),json.dumps({'sha':sha}).encode(),archive([('root/main.ts',b'const x=1','file')])]
    fetch=Mock(side_effect=answers); monkeypatch.setattr(repository,'fetch',fetch)
    result=repository.retrieve(RepositoryIntake(mode='repository',repository_url='https://github.com/owner/repo',authorization_confirmed=True),tmp_path)
    assert result[3:] == ('main',sha)
    assert [call.args[:2] for call in fetch.call_args_list]==[('api.github.com','/repos/owner/repo'),('api.github.com','/repos/owner/repo/commits/main'),('codeload.github.com',f'/owner/repo/tar.gz/{sha}')]


def test_repository_admission_idempotency_and_attribution(runtime,monkeypatch):
    client,headers,store=runtime
    def retrieve(submission,directory):
        (directory/'file_0').write_text('const x=1')
        (directory/'manifest.json').write_text(json.dumps({'files':[{'part_id':'file_0','relative_path':'src/app.ts'}]}))
        return ['src/app.ts'],[],'https://github.com/owner/repo','main','a'*40
    fetched=Mock(side_effect=retrieve)
    monkeypatch.setattr('backend.api.main.retrieve',fetched)
    body={'mode':'repository','repository_url':'https://github.com/owner/repo','ref':'main','authorization_confirmed':True}
    first=client.post('/api/v1/scans',headers=headers,json=body)
    assert first.status_code==202,first.text
    assert first.json()['mode']=='repository' and first.json()['input']['revision']=='a'*40
    assert first.json()['input']['requested_ref']=='main'
    assert client.post('/api/v1/scans',headers=headers,json=body).json()['scan_id']==first.json()['scan_id']
    assert fetched.call_count==1
    assert client.post('/api/v1/scans',headers=headers,json={**body,'ref':'other'}).status_code==409
    assert len(list(store.staging.iterdir()))==1


def test_failed_repository_not_published(runtime,monkeypatch):
    client,headers,store=runtime
    monkeypatch.setattr('backend.api.main.retrieve',Mock(side_effect=IntakeError(422,'repository_retrieval_failed')))
    response=client.post('/api/v1/scans',headers=headers,json={'mode':'repository','repository_url':'https://github.com/owner/repo','authorization_confirmed':True})
    assert response.status_code==422 and not list(store.staging.iterdir())
