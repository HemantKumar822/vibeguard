import { act } from 'react'
import { createRoot } from 'react-dom/client'
import { expect, test, vi } from 'vitest'
import Comparison from './Comparison'
import { fixtures } from '../../test/fixtures.generated'
import type { components } from '../../shared/api/generated'

test('renders paired labels, truthful absence and retained actions with keyboard buttons', async () => {
  vi.stubGlobal('IS_REACT_ACT_ENVIRONMENT', true)
  const scan = fixtures.find(item => item.name === 'source-baseline')!.data as components['schemas']['Scan']
  const result = fixtures.find(item => item.name === 'comparison')!.data as components['schemas']['Comparison']
  const host = document.createElement('div'); document.body.append(host)
  const root = createRoot(host)
  await act(async () => root.render(<Comparison baseline={scan} current={scan} result={result} />))
  expect(host.textContent).toContain('Before · baseline')
  expect(host.textContent).toContain('After · new scan')
  expect(host.textContent).toContain('does not prove repair or credential rotation')
  expect(host.querySelector('button')?.getAttribute('aria-pressed')).toBe('true')
  const back = Array.from(host.querySelectorAll('button')).find(button => button.textContent?.includes('Back to comparison'))!
  await act(async () => back.click())
  expect(document.activeElement).toBe(host.querySelector('button'))
  await act(async () => root.unmount()); host.remove(); vi.unstubAllGlobals()
})
