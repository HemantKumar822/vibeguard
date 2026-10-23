import { act } from 'react'
import { createRoot, type Root } from 'react-dom/client'
import { afterEach, beforeEach, expect, test, vi } from 'vitest'
import type { components } from './generated/api'
import Report from './Report'
import { fixtures } from './generated/fixtures'

let host: HTMLDivElement
let root: Root
const scan = fixtures.find(item => item.name === 'source-baseline')!.data as components['schemas']['Scan']
beforeEach(() => { vi.stubGlobal('IS_REACT_ACT_ENVIRONMENT', true); host = document.createElement('div'); document.body.append(host); root = createRoot(host) })
afterEach(async () => { await act(async () => root.unmount()); host.remove(); vi.unstubAllGlobals() })

test('shows attributed escaped evidence and filter-empty state', async () => {
  const value = structuredClone(scan)
  value.findings[0].evidence_redacted = '<script>synthetic_evidence</script>'
  await act(async () => root.render(<Report scan={value} />))
  expect(host.querySelector('script')).toBeNull()
  expect(host.querySelector('pre')?.textContent).toContain('<script>synthetic_evidence</script>')
  expect(host.textContent).toContain(value.findings[0].rule_id)
  const select = host.querySelector('select')!
  await act(async () => { select.value = 'info'; select.dispatchEvent(new Event('change', { bubbles: true })) })
  expect(host.textContent).toContain('No findings match these filters')
})

test('copies only the sanitized consolidated prompt', async () => {
  const writeText = vi.fn().mockResolvedValue(undefined)
  Object.defineProperty(navigator, 'clipboard', { configurable: true, value: { writeText } })
  await act(async () => root.render(<Report scan={scan} />))
  const copy = Array.from(host.querySelectorAll('button')).find(button => button.textContent === 'Copy repair prompt')!
  await act(async () => copy.click())
  expect(writeText).toHaveBeenCalledWith(scan.repair!.prompt_redacted)
  expect(host.textContent).toContain('Repair prompt copied.')
})

test('clipboard failure leaves manually selectable sanitized guidance', async () => {
  Object.defineProperty(navigator, 'clipboard', { configurable: true, value: { writeText: vi.fn().mockRejectedValue(new Error('denied')) } })
  await act(async () => root.render(<Report scan={scan} />))
  const copy = Array.from(host.querySelectorAll('button')).find(button => button.textContent === 'Copy repair prompt')!
  await act(async () => copy.click())
  expect(host.textContent).toContain('Select and copy the sanitized text below manually')
  expect(host.querySelector('textarea')?.value).toBe(scan.repair!.prompt_redacted)
})

test('shows requested and resolved repository identity in the same report', async () => {
  await act(async () => root.render(<Report scan={{ ...scan, mode: 'repository', input: { ...scan.input, repository: 'https://github.com/team/project', requested_ref: 'main', revision: 'a'.repeat(40) } }} />))
  expect(host.textContent).toContain('Requested ref: main')
  expect(host.textContent).toContain('Resolved commit: ' + 'a'.repeat(40))
  expect(host.textContent).toContain(scan.findings[0].rule_id)
})

test('website findings use observed URLs and passive limitations', async () => {
  const website = fixtures.find(item => item.name === 'website')!.data as components['schemas']['Scan']
  await act(async () => root.render(<Report scan={website} />))
  expect(host.textContent).toContain('Website observation')
  expect(host.textContent).toContain(website.input.target_redacted)
  expect(host.textContent).toContain('No browser JavaScript, authenticated pages or private backend source')
  expect(host.textContent).toContain(website.findings[0].location.kind === 'web' ? website.findings[0].location.url_redacted : '')
})
