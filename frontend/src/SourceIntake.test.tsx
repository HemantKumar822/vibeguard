import { act } from 'react'
import { createRoot, type Root } from 'react-dom/client'
import { beforeEach, afterEach, expect, test, vi } from 'vitest'
import SourceIntake from './SourceIntake'
let host: HTMLDivElement
let root: Root
beforeEach(() => { vi.stubGlobal('IS_REACT_ACT_ENVIRONMENT', true); host = document.createElement('div'); document.body.append(host); root = createRoot(host) })
afterEach(async () => { await act(async () => root.unmount()); host.remove(); vi.useRealTimers(); vi.unstubAllGlobals() })
test('requires permission and leaves sharing off', async () => {
  await act(async () => root.render(<SourceIntake />))
  expect(host.querySelector('button')?.disabled).toBe(true)
  expect(Array.from(host.querySelectorAll<HTMLInputElement>('input[type=checkbox]')).every(input => !input.checked)).toBe(true)
  expect(host.textContent).toContain('Repository and website intake are unavailable')
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
