import { act } from 'react'
import { createRoot, type Root } from 'react-dom/client'
import { beforeEach, afterEach, expect, test, vi } from 'vitest'
import SourceIntake from './SourceIntake'
let host: HTMLDivElement
let root: Root
beforeEach(() => { vi.stubGlobal('IS_REACT_ACT_ENVIRONMENT', true); host = document.createElement('div'); document.body.append(host); root = createRoot(host) })
afterEach(async () => { await act(async () => root.unmount()); host.remove(); vi.unstubAllGlobals() })
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
  const fetch = vi.fn().mockResolvedValueOnce({ ok: true, json: async () => ({csrf_token:'csrf'}) }).mockResolvedValueOnce({ok:true,json:async()=>({scan_id:'owned',status:'queued',accepted_files:['src/main.ts'],coverage:{exclusions:[]}})})
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
