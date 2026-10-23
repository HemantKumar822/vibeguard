import { useEffect, useState } from 'react'
import type { components } from './generated/api'

export default function App() {
  const [health, setHealth] = useState<'checking' | 'ok' | 'unavailable'>('checking')
  useEffect(() => {
    const controller = new AbortController()
    fetch('/api/v1/health', { signal: controller.signal })
      .then(async response => {
        if (!response.ok) throw new Error('Health request failed')
        const data: components['schemas']['Health'] = await response.json()
        if (data.status !== 'ok' || data.contract_version !== 'v1') throw new Error('Unexpected health response')
        setHealth('ok')
      })
      .catch(() => { if (!controller.signal.aborted) setHealth('unavailable') })
    return () => controller.abort()
  }, [])
  return <main>
    <header><span className="wordmark">VibeGuard<span aria-hidden="true"> /</span></span><span className="eyebrow">CY-02 · Security reviewer</span></header>
    <section className="intro" aria-labelledby="title">
      <p className="eyebrow">Project foundation</p>
      <h1 id="title">Evidence before<br />confidence.</h1>
      <p className="lede">A workspace for reviewing AI-built websites.<br />The scanning workflow is not available yet.</p>
    </section>
    {import.meta.env.DEV && <section className="panel" aria-label="Development health">
      <h2>Development connection</h2>
      <p role="status">{health === 'checking' ? 'Checking the API connection…' : health === 'ok' ? 'API connected · contract v1' : 'API unavailable. Start the backend and retry this page.'}</p>
      <p className="muted">This checks the application connection. No security scan has run.</p>
    </section>}
    <footer>Inspect. Understand. Repair. Recheck.</footer>
  </main>
}
