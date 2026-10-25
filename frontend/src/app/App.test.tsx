import { act } from 'react'
import { createRoot, type Root } from 'react-dom/client'
import { afterEach, beforeEach, expect, test, vi } from 'vitest'
import App from './App'

let host: HTMLDivElement
let root: Root

beforeEach(() => {
  vi.stubGlobal('IS_REACT_ACT_ENVIRONMENT', true)
  host = document.createElement('div')
  document.body.append(host)
  root = createRoot(host)
})
afterEach(async () => {
  await act(async () => root.unmount())
  host.remove()
  vi.useRealTimers()
  vi.unstubAllGlobals()
})

test('connects through the documented API route', async () => {
  const fetch = vi.fn().mockResolvedValue({ ok: true, json: async () => ({ status: 'ok', contract_version: 'v1' }) })
  vi.stubGlobal('fetch', fetch)
  await act(async () => root.render(<App />))
  expect(fetch).toHaveBeenCalledWith('/api/v1/health', expect.objectContaining({ signal: expect.any(AbortSignal) }))
  expect(host.textContent).toContain('API connected')
})

test.each([
  { ok: false, json: async () => ({}) },
  { ok: true, json: async () => ({ status: 'ok', contract_version: 'v2' }) },
])('shows unavailable for HTTP failure or an incompatible contract', async response => {
  vi.stubGlobal('fetch', vi.fn().mockResolvedValue(response))
  await act(async () => root.render(<App />))
  expect(host.textContent).toContain('API unavailable')
})

test('shows unavailable for a network failure', async () => {
  vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new Error('Network failure')))
  await act(async () => root.render(<App />))
  expect(host.textContent).toContain('API unavailable')
})

test('stops checking after a bounded deadline even if fetch never resolves', async () => {
  vi.useFakeTimers()
  vi.stubGlobal('fetch', vi.fn(() => new Promise(() => {})))
  await act(async () => root.render(<App />))
  expect(host.textContent).toContain('Checking')
  await act(async () => { vi.advanceTimersByTime(10_001) })
  expect(host.textContent).toContain('API unavailable')
})
