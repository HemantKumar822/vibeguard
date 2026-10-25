import SourceIntake from '../features/intake/SourceIntake'
import { useEffect, useState } from 'react'
import type { components } from '../shared/api/generated'

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
  return <div className="app-shell">
    <a className="skip-link" href="#workspace">Skip to review workspace</a>
    <aside className="sidebar" aria-label="Workspace navigation">
      <a className="brand" href="#workspace" aria-label="VibeGuard workspace"><span className="brand-mark" aria-hidden="true">V<span>/</span></span><span>VibeGuard<small>SECURITY WORKSPACE</small></span></a>
      <p className="nav-caption">WORKSPACE</p>
      <nav><a className="nav-link is-active" href="#workspace" aria-current="page"><span aria-hidden="true">⊞</span> Security review <span className="nav-indicator" /></a>
        <a className="nav-link" href="#review-guide"><span aria-hidden="true">≡</span> How review works</a></nav>
      <div className="sidebar-note"><span className="eyebrow">YOUR REVIEW WORKFLOW</span><p>Scan. Investigate. Repair.<br />Rescan to verify changes.</p></div>
    </aside>
    <main id="workspace" tabIndex={-1}>
    <header className="workspace-header"><div className="breadcrumb">Workspace <span aria-hidden="true">/</span> <strong>Security review</strong></div>
      <span className={`connection connection-${health}`} role="status"><span className="connection-dot" />{health === 'checking' ? 'Checking the API connection…' : health === 'ok' ? 'API connected · contract v1' : 'API unavailable. Start the backend and retry this page.'}</span></header>
    <section className="intro" aria-labelledby="title"><div><p className="eyebrow intro-eyebrow">SECURITY REVIEW</p><h1 id="title">A clear path to safer code.</h1><p className="lede">Review your code or website. Follow the checks. Fix what matters.</p></div></section>
    <SourceIntake />
    <details id="review-guide" className="review-guide"><summary>How review works</summary><ol><li><strong>Submit an authorized input</strong><span>Choose a codebase, public repository or website.</span></li><li><strong>Follow the checks and inspect findings</strong><span>Review real locations, masked evidence and coverage limits.</span></li><li><strong>Repair and rescan</strong><span>Copy the repair prompt, update your code and compare a new scan.</span></li></ol></details>
    <footer><span>VibeGuard <span className="muted">/ Evidence before confidence.</span></span><span>Review only code you are authorized to assess.</span></footer>
  </main>
  </div>
}

