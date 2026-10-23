import SourceIntake from './SourceIntake'
import { useEffect, useState } from 'react'
import type { components } from './generated/api'

export default function App() {
  const [health, setHealth] = useState<'checking' | 'ok' | 'unavailable'>('checking')
  useEffect(() => {
    const controller = new AbortController()
    let active = true
    const deadline = setTimeout(() => {
      if (active) setHealth('unavailable')
      controller.abort()
    }, 10_000)
    fetch('/api/v1/health', { signal: controller.signal })
      .then(async response => {
        if (!response.ok) throw new Error('Health request failed')
        const data: components['schemas']['Health'] = await response.json()
        if (data.status !== 'ok' || data.contract_version !== 'v1') throw new Error('Unexpected health response')
        if (active && !controller.signal.aborted) setHealth('ok')
      })
      .catch(() => { if (active && !controller.signal.aborted) setHealth('unavailable') })
      .finally(() => clearTimeout(deadline))
    return () => { active = false; clearTimeout(deadline); controller.abort() }
  }, [])
  return <main>
    <header><span className="wordmark">VibeGuard<span aria-hidden="true"> /</span></span><span className="eyebrow">CY-02 · Security reviewer</span></header>
    <section className="intro" aria-labelledby="title">
      <p className="eyebrow">Source review workspace</p>
      <h1 id="title">Evidence before<br />confidence.</h1>
      <p className="lede">Review authorized source trees or public GitHub snapshots.<br />Inspect masked evidence and copy concrete repair guidance.</p>
    </section>
    {import.meta.env.DEV && <section className="panel" aria-label="Development health">
      <h2>Development connection</h2>
      <p role="status">{health === 'checking' ? 'Checking the API connection…' : health === 'ok' ? 'API connected · contract v1' : 'API unavailable. Start the backend and retry this page.'}</p>
      <p className="muted">This checks the application connection. No security scan has run.</p>
    </section>}
    <SourceIntake />
    <footer>Inspect. Understand. Repair. Recheck.</footer>
  </main>
}

