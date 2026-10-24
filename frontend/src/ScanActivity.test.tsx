import { act } from 'react'
import { createRoot, type Root } from 'react-dom/client'
import { afterEach, beforeEach, expect, test, vi } from 'vitest'
import type { components } from './generated/api'
import { fixtures } from './generated/fixtures'
import ScanActivity from './ScanActivity'
import { reportMarkdown } from './reportExport'

type Scan = components['schemas']['Scan']
let host: HTMLDivElement
let root: Root
const baseline = fixtures.find(item => item.name === 'source-baseline')!.data as Scan
beforeEach(() => { vi.stubGlobal('IS_REACT_ACT_ENVIRONMENT', true); host = document.createElement('div'); document.body.append(host); root = createRoot(host) })
afterEach(async () => { await act(async () => root.unmount()); host.remove(); vi.unstubAllGlobals() })

test('renders actual sequential scanner states and updates without inventing events', async () => {
  const scan = structuredClone(baseline)
  scan.status = 'running'; scan.finished_at = null; scan.repair = null
  const tools = scan.tools.filter(tool => tool.applicable)
  tools[0].status = 'running'; tools[0].finished_at = null
  tools[1].status = 'queued'; tools[1].started_at = null; tools[1].finished_at = null
  await act(async () => root.render(<ScanActivity scan={scan} />))
  expect(host.querySelectorAll('.check-list > li')).toHaveLength(2)
  expect(host.querySelector('[data-state=running]')).not.toBeNull()
  expect(host.querySelector('[data-state=queued]')).not.toBeNull()
  expect(host.querySelector('.activity-log')?.hasAttribute('open')).toBe(true)
  expect(host.querySelector('[aria-label="Recorded scan events"]')?.textContent).not.toContain('Code security started')
  await act(async () => root.render(<ScanActivity scan={baseline} />))
  expect(host.querySelector('[data-state=running]')).toBeNull()
  expect(host.querySelector('.activity-log')?.hasAttribute('open')).toBe(false)
  const dates = Array.from(host.querySelectorAll('time')).map(time => Date.parse(time.dateTime))
  expect(dates).toEqual([...dates].sort((a, b) => a - b))
})

test('partial and timed-out checks are never presented as successful coverage', async () => {
  const scan = structuredClone(baseline)
  scan.status = 'partial'; scan.coverage.completed_count = 1
  scan.tools[0].status = 'timed_out'; scan.tools[0].coverage.scope_complete = false
  await act(async () => root.render(<ScanActivity scan={scan} />))
  expect(host.textContent).toContain('1/2 required checks')
  expect(host.querySelector('[data-state=timed_out]')?.textContent).toContain('Timed out')
  expect(host.textContent).not.toContain('Live status')
})

test('report export retains attribution, limitations, all findings and human actions', () => {
  const scan = structuredClone(baseline)
  scan.warnings = ['One resource could not be assessed.']
  const output = reportMarkdown(scan)
  expect(output).toContain(scan.scan_id)
  expect(output).toContain(scan.warnings[0])
  for (const finding of scan.findings) {
    expect(output).toContain(finding.rule_id)
    expect(output).toContain(finding.fix_guidance)
    for (const action of finding.human_actions) expect(output).toContain(action)
  }
  expect(output).toContain(scan.repair!.prompt_redacted)
})

test('export fences hostile Markdown and retains web asset line attribution', () => {
  const scan = structuredClone(fixtures.find(item => item.name === 'website')!.data as Scan)
  scan.warnings = ['![remote](https://example.invalid/pixel)\n```\n<script>untrusted</script>']
  const location = scan.findings[0].location
  if (location.kind !== 'web') throw new Error('Expected website fixture')
  location.line_start = 42
  const output = reportMarkdown(scan)
  expect(output.startsWith('````text\n')).toBe(true)
  expect(output.endsWith('\n````\n')).toBe(true)
  expect(output).toContain(`| ${location.part} | line 42`)
})
