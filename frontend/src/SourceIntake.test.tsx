import { act } from 'react'
import { createRoot, type Root } from 'react-dom/client'
import { beforeEach, afterEach, expect, test, vi } from 'vitest'
import SourceIntake from './SourceIntake'
let host: HTMLDivElement
let root: Root
beforeEach(() => { vi.stubGlobal('IS_REACT_ACT_ENVIRONMENT', true); host = document.createElement('div'); document.body.append(host); root = createRoot(host) })
afterEach(async () => { await act(async () => root.unmount()); host.remove(); vi.useRealTimers(); vi.unstubAllGlobals() })

async function repositoryForm() {
  const mode = host.querySelector<HTMLSelectElement>('select')!
  await act(async () => { mode.value = 'repository'; mode.dispatchEvent(new Event('change', { bubbles: true })) })
  const url = host.querySelector<HTMLInputElement>('input[type=url]')!
  await act(async () => {
    Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value')!.set!.call(url, 'https://github.com/team/project')
    url.dispatchEvent(new Event('input', { bubbles: true }))
  })
  await act(async () => host.querySelector<HTMLInputElement>('input[type=checkbox]')!.click())
  return mode
}

test('repeat preserves baseline, resets consent, and sends owned same-mode request', async () => {
  const oldId='a'.repeat(32), newId='b'.repeat(32)
  const report={scan_id:oldId,mode:'repository',status:'complete',input:{repository:'https://github.com/team/project',revision:'c'.repeat(40)},accepted_files:[],findings:[],tools:[],warnings:[],coverage:{exclusions:[],inspected:[],completed_count:2,required_count:2},repair:{prompt_redacted:'Baseline guidance',human_actions:[]}}
  const fetch=vi.fn().mockImplementation(async(url:string)=>({ok:true,json:async()=>url.endsWith('/session')?{csrf_token:'csrf'}:url.endsWith('/rescans')?{...report,scan_id:newId,baseline_id:oldId,status:'queued',repair:null}:report}))
  vi.stubGlobal('fetch',fetch)
  await act(async()=>root.render(<SourceIntake/>))
  await repositoryForm()
  await act(async()=>host.querySelector('form')!.dispatchEvent(new Event('submit',{bubbles:true,cancelable:true})))
  await act(async()=>Array.from(host.querySelectorAll('button')).find(button=>button.textContent==='Rescan corrected input')!.click())
  expect(host.textContent).toContain('Baseline guidance')
  expect(host.querySelector<HTMLSelectElement>('select')!.disabled).toBe(true)
  expect(host.querySelector<HTMLInputElement>('input[type=checkbox]')!.checked).toBe(false)
  await act(async()=>host.querySelector<HTMLInputElement>('input[type=checkbox]')!.click())
  await act(async()=>host.querySelector('form')!.dispatchEvent(new Event('submit',{bubbles:true,cancelable:true})))
  const call=fetch.mock.calls.find(call=>call[0]===`/api/v1/scans/${oldId}/rescans`)!
  expect(JSON.parse(call[1].body)).toMatchObject({mode:'repository',authorization_confirmed:true,allow_external_ai:false})
  expect(host.textContent).toContain('Before - preserved baseline')
  expect(host.textContent).toContain('Scan ID: '+newId)
})

test('a delayed reconnect cannot overwrite a newer accepted submission', async () => {
  let release!: (value:unknown)=>void
  const deferred=new Promise(resolve=>{release=resolve})
  const oldId='a'.repeat(32), newId='b'.repeat(32)
  const report={mode:'repository',status:'queued',input:{},accepted_files:[],findings:[],tools:[],warnings:[],coverage:{exclusions:[]}}
  const fetch=vi.fn().mockImplementation(async(url:string)=>{
    if(url.endsWith('/session'))return{ok:true,json:async()=>({csrf_token:'csrf'})}
    if(url.endsWith('/'+oldId))return deferred
    return{ok:true,json:async()=>({...report,scan_id:newId})}
  })
  vi.stubGlobal('fetch',fetch)
  await act(async()=>root.render(<SourceIntake/>))
  const id=host.querySelector<HTMLInputElement>('input[maxlength="32"]')!
  await act(async()=>{Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value')!.set!.call(id,oldId);id.dispatchEvent(new Event('input',{bubbles:true}))})
  await act(async()=>Array.from(host.querySelectorAll('button')).find(button=>button.textContent==='Reconnect')!.click())
  await repositoryForm()
  await act(async()=>host.querySelector('form')!.dispatchEvent(new Event('submit',{bubbles:true,cancelable:true})))
  await act(async()=>{release({ok:true,json:async()=>({...report,scan_id:oldId})});await deferred})
  expect(host.textContent).toContain('Scan ID: '+newId)
})

test('repository submission preserves report across mode changes and reconnects without resubmitting', async () => {
  const report = { scan_id: 'a'.repeat(32), status: 'complete', mode: 'repository',
    input: { repository: 'https://github.com/team/project', requested_ref: 'main', revision: 'b'.repeat(40) },
    accepted_files: ['src/app.ts'], findings: [], tools: [], warnings: [],
    coverage: { exclusions: [], inspected: ['src/app.ts'], completed_count: 2, required_count: 2 },
    repair: { prompt_redacted: 'Review completed checks.', human_actions: [] } }
  const fetch = vi.fn().mockImplementation(async (url: string) => ({ ok: true, json: async () => url.endsWith('/session') ? { csrf_token: 'csrf' } : report }))
  vi.stubGlobal('fetch', fetch)
  await act(async () => root.render(<SourceIntake />))
  const mode = await repositoryForm()
  await act(async () => host.querySelector('form')!.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true })))
  expect(JSON.parse(fetch.mock.calls[1][1].body)).toMatchObject({ mode: 'repository', ref: null, allow_external_ai: false })
  expect(host.textContent).toContain('Resolved commit: ' + 'b'.repeat(40))
  await act(async () => { mode.value = 'codebase'; mode.dispatchEvent(new Event('change', { bubbles: true })) })
  expect(host.textContent).toContain('Resolved commit: ' + 'b'.repeat(40))
  expect(fetch).toHaveBeenCalledTimes(2)
  await act(async () => root.unmount())
  root = createRoot(host)
  await act(async () => root.render(<SourceIntake />))
  const id = host.querySelector<HTMLInputElement>('input[maxlength="32"]')!
  await act(async () => {
    Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value')!.set!.call(id, report.scan_id)
    id.dispatchEvent(new Event('input', { bubbles: true }))
  })
  await act(async () => Array.from(host.querySelectorAll('button')).find(button => button.textContent === 'Reconnect')!.click())
  expect(host.textContent).toContain('Resolved commit: ' + 'b'.repeat(40))
  expect(fetch.mock.calls.filter(call => call[0] === '/api/v1/scans')).toHaveLength(1)
  expect(fetch.mock.calls.at(-1)![0]).toBe('/api/v1/scans/' + report.scan_id)
})

test('repository rejection leaves the input editable with a safe reason', async () => {
  vi.stubGlobal('fetch', vi.fn().mockResolvedValueOnce({ ok: true, json: async () => ({ csrf_token: 'csrf' }) })
    .mockResolvedValueOnce({ ok: false, json: async () => ({ error: { code: 'repository_retrieval_failed' } }) }))
  await act(async () => root.render(<SourceIntake />))
  await repositoryForm()
  await act(async () => host.querySelector('form')!.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true })))
  const input = host.querySelector<HTMLInputElement>('input[type=url]')!
  expect(input.value).toBe('https://github.com/team/project')
  expect(input.disabled).toBe(false)
  expect(host.querySelector('[role=alert]')?.textContent).toContain('repository_retrieval_failed')
})

test('an old polling 404 cannot clear a newly accepted report', async () => {
  vi.useFakeTimers()
  let resolveOld!: (value: { status: number }) => void
  const oldResponse = new Promise(resolve => { resolveOld = resolve })
  let submissions = 0
  const oldId = 'a'.repeat(32), newId = 'b'.repeat(32)
  const report = { status: 'queued', input: {}, accepted_files: [], findings: [], tools: [], warnings: [], coverage: { exclusions: [] } }
  const fetch = vi.fn().mockImplementation(async (url: string) => {
    if (url.endsWith('/session')) return { ok: true, json: async () => ({ csrf_token: 'csrf' }) }
    if (url === `/api/v1/scans/${oldId}`) return oldResponse
    submissions++
    return { ok: true, json: async () => ({ ...report, scan_id: submissions === 1 ? oldId : newId }) }
  })
  vi.stubGlobal('fetch', fetch)
  await act(async () => root.render(<SourceIntake />))
  await repositoryForm()
  const submit = () => host.querySelector('form')!.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }))
  await act(async () => { submit() })
  await act(async () => vi.advanceTimersByTimeAsync(1000))
  await act(async () => host.querySelector<HTMLInputElement>('input[type=checkbox]')!.click())
  await act(async () => { submit() })
  await act(async () => { resolveOld({ status: 404 }); await oldResponse })
  expect(host.textContent).toContain('Scan ID: ' + newId)
  expect(host.textContent).not.toContain('Scan is unavailable or expired')
})

test.each([true, false])('website admission checks measured readiness (%s)', async available => {
  const fetch = vi.fn().mockImplementation(async (url: string) => {
    if (url.endsWith('/session')) return { ok: true, json: async () => ({ csrf_token: 'csrf' }) }
    if (url.endsWith('/capabilities')) return { ok: true, json: async () => ({ permitted_modes: available ? ['website'] : ['codebase', 'repository'] }) }
    return { ok: true, json: async () => ({ scan_id: 'c'.repeat(32), mode: 'website', status: 'queued', findings: [], tools: [], warnings: [], coverage: { exclusions: [] }, input: { target_redacted: 'https://example.com/', observation_id: 'c'.repeat(32) } }) }
  })
  vi.stubGlobal('fetch', fetch)
  await act(async () => root.render(<SourceIntake />))
  const mode = host.querySelector('select')!
  await act(async () => { mode.value = 'website'; mode.dispatchEvent(new Event('change', { bubbles: true })) })
  const url = host.querySelector<HTMLInputElement>('input[type=url]')!
  await act(async () => {
    Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value')!.set!.call(url, 'https://example.com/')
    url.dispatchEvent(new Event('input', { bubbles: true }))
  })
  await act(async () => host.querySelector<HTMLInputElement>('input[type=checkbox]')!.click())
  await act(async () => host.querySelector('form')!.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true })))
  if (available) {
    expect(JSON.parse(fetch.mock.calls[2][1].body)).toMatchObject({ mode: 'website', target_url: 'https://example.com/', authorization_confirmed: true, allow_external_ai: false })
    expect(host.textContent).toContain('Website observation')
    expect(host.textContent).toContain('No browser JavaScript')
  } else {
    expect(fetch.mock.calls.filter(call => call[0] === '/api/v1/scans')).toHaveLength(0)
    expect(host.querySelector('[role=alert]')?.textContent).toContain('safety verification is missing or stale')
    expect(url.value).toBe('https://example.com/')
  }
})
test('requires permission and leaves sharing off', async () => {
  await act(async () => root.render(<SourceIntake />))
  expect(host.querySelector('button')?.disabled).toBe(true)
  expect(Array.from(host.querySelectorAll<HTMLInputElement>('input[type=checkbox]')).every(input => !input.checked)).toBe(true)
  expect(host.querySelector('select')?.textContent).toContain('Website URL')
})
test('explains lost directory paths and offers explicit mapping', async () => {
  await act(async () => root.render(<SourceIntake />))
  const input = host.querySelector<HTMLInputElement>('input[type=file]')!
  Object.defineProperty(input, 'files', { value: [new File(['x'], 'main.ts')] })
  await act(async () => input.dispatchEvent(new Event('change', { bubbles: true })))
  expect(host.querySelector('[role=alert]')?.textContent).toContain('browser lost directory paths')
  expect(host.textContent).toContain('Choose mapped files')
})
test('submits mapped tree and displays real queued inventory', async () => {
  const fetch = vi.fn().mockResolvedValueOnce({ ok: true, json: async () => ({csrf_token:'csrf'}) }).mockResolvedValueOnce({ok:true,json:async()=>({scan_id:'owned',status:'queued',accepted_files:['src/main.ts'],coverage:{exclusions:[]},tools:[{name:'semgrep',status:'queued'}],warnings:['Waiting for the trusted coordinator.']})})
  vi.stubGlobal('fetch', fetch)
  await act(async () => root.render(<SourceIntake />))
  const input = host.querySelectorAll<HTMLInputElement>('input[type=file]')[1]
  Object.defineProperty(input, 'files', { value: [new File(['const x=1'], 'main.ts')] })
  await act(async () => input.dispatchEvent(new Event('change', {bubbles:true})))
  const area = host.querySelector('textarea')!
  const setter = Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype,'value')!.set!
  await act(async () => { setter.call(area, 'src/main.ts'); area.dispatchEvent(new Event('input',{bubbles:true})) })
  await act(async () => host.querySelector<HTMLInputElement>('input[type=checkbox]')!.click())
  await act(async () => host.querySelector('form')!.dispatchEvent(new Event('submit',{bubbles:true,cancelable:true})))
  expect(fetch).toHaveBeenCalledTimes(2)
  expect(host.textContent).toContain('Accepted · queued')
  expect(host.textContent).toContain('src/main.ts')
  const body = fetch.mock.calls[1][1].body as FormData
  expect(JSON.parse(body.get('metadata') as string).allow_external_ai).toBe(false)
})

test.each(['failed', '404', 'delete'])('polling and deletion expose actual %s outcome', async outcome => {
  vi.useFakeTimers()
  const queued = {scan_id:'owned',status:'queued',accepted_files:[],coverage:{exclusions:[]},tools:[{name:'semgrep',status:'queued'}],warnings:[]}
  const fetch = vi.fn().mockResolvedValueOnce({ok:true,json:async()=>({csrf_token:'csrf'})})
    .mockResolvedValueOnce({ok:true,json:async()=>queued})
    .mockResolvedValueOnce(outcome === '404' ? {status:404} : {ok:true,json:async()=> outcome === 'delete'
      ? {operation_id:'cleanup',scan_id:'owned',status:'pending'}
      : {...queued,status:'failed',tools:[{name:'semgrep',status:'failed'}],repair:{prompt_redacted:'Review manually'},error:{message:'Checks unavailable'}}})
    .mockResolvedValue({ok:true,json:async()=>({operation_id:'cleanup',scan_id:'owned',status:'complete'})})
  vi.stubGlobal('fetch',fetch)
  await act(async()=>root.render(<SourceIntake/>))
  const input=host.querySelectorAll<HTMLInputElement>('input[type=file]')[1]
  Object.defineProperty(input,'files',{value:[new File(['x'],'main.ts')]})
  await act(async()=>input.dispatchEvent(new Event('change',{bubbles:true})))
  const area=host.querySelector('textarea')!
  await act(async()=>{Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype,'value')!.set!.call(area,'main.ts');area.dispatchEvent(new Event('input',{bubbles:true}))})
  await act(async()=>host.querySelector<HTMLInputElement>('input[type=checkbox]')!.click())
  await act(async()=>host.querySelector('form')!.dispatchEvent(new Event('submit',{bubbles:true,cancelable:true})))
  if(outcome==='delete') {
    const dialog=host.querySelector('dialog')!
    dialog.showModal=()=>dialog.setAttribute('open','')
    dialog.close=()=>dialog.removeAttribute('open')
    const trigger=Array.from(host.querySelectorAll('button')).find(button=>button.textContent==='Delete scan' && !dialog.contains(button))!
    await act(async()=>trigger.click())
    expect(dialog.hasAttribute('open')).toBe(true)
    await act(async()=>dialog.querySelectorAll('button')[1].click())
    expect(host.textContent).toContain('Cleanup: pending')
    expect(fetch.mock.calls[2][1].headers['X-CSRF-Token']).toBe('csrf')
    await act(async()=>vi.advanceTimersByTimeAsync(1000))
    expect(host.textContent).toContain('Cleanup: complete')
  } else {
    await act(async()=>vi.advanceTimersByTimeAsync(1000))
    if(outcome==='404') expect(host.textContent).toContain('Scan is unavailable or expired')
    else {expect(host.textContent).toContain('semgrep: failed');expect(host.textContent).toContain('Review manually')}
    const signal=fetch.mock.calls[2][1].signal as AbortSignal
    expect(signal.aborted).toBe(true)
  }
})

test.each(['unchanged','path','permission','sharing','files'])('retry key follows actual %s payload changes', async change => {
  const fetch = vi.fn().mockImplementation(async (url: string) => {
    if (url.endsWith('/session')) return {ok:true,json:async()=>({csrf_token:'csrf'})}
    throw new Error('response lost')
  })
  vi.stubGlobal('fetch', fetch)
  await act(async () => root.render(<SourceIntake />))
  const fileInput = host.querySelectorAll<HTMLInputElement>('input[type=file]')[1]
  const file = new File(['const x=1'],'main.ts')
  Object.defineProperty(fileInput,'files',{value:[file],configurable:true})
  await act(async () => fileInput.dispatchEvent(new Event('change',{bubbles:true})))
  const area = host.querySelector('textarea')!
  const setter = Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype,'value')!.set!
  async function path(value: string) {
    await act(async () => {setter.call(area,value);area.dispatchEvent(new Event('input',{bubbles:true}))})
  }
  await path(' src/main.ts ')
  const permission = host.querySelectorAll<HTMLInputElement>('input[type=checkbox]')[0]
  await act(async () => permission.click())
  async function submit() {
    await act(async () => host.querySelector('form')!.dispatchEvent(new Event('submit',{bubbles:true,cancelable:true})))
  }
  await submit()
  if(change==='path') await path('src/other.ts')
  if(change==='permission') {await act(async()=>permission.click());await act(async()=>permission.click())}
  if(change==='sharing') await act(async()=>host.querySelectorAll<HTMLInputElement>('input[type=checkbox]')[1].click())
  if(change==='files') {
    Object.defineProperty(fileInput,'files',{value:[new File(['changed'],'main.ts')],configurable:true})
    await act(async()=>fileInput.dispatchEvent(new Event('change',{bubbles:true})))
    await path(' src/main.ts ')
  }
  await submit()
  const posts = fetch.mock.calls.filter(call=>call[0].endsWith('/scans'))
  expect(posts).toHaveLength(2)
  const first = posts[0][1] as {headers: Record<string,string>,body:FormData}
  const second = posts[1][1] as {headers: Record<string,string>}
  expect(JSON.parse(first.body.get('metadata') as string).files[0].relative_path).toBe(' src/main.ts ')
  if(change==='unchanged') expect(first.headers['Idempotency-Key']).toBe(second.headers['Idempotency-Key'])
  else expect(first.headers['Idempotency-Key']).not.toBe(second.headers['Idempotency-Key'])
})
