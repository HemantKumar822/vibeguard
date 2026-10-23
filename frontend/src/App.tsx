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
  return <div className="app-shell">
    <a className="skip-link" href="#workspace">Skip to review workspace</a>
    <aside className="sidebar" aria-label="Workspace navigation">
      <a className="brand" href="#workspace" aria-label="VibeGuard workspace"><span className="brand-mark" aria-hidden="true">V<span>/</span></span><span>VibeGuard<small>SECURITY WORKSPACE</small></span></a>
      <p className="nav-caption">WORKSPACE</p>
      <nav><a className="nav-link is-active" href="#workspace" aria-current="page"><span aria-hidden="true">⊞</span> Source review <span className="nav-indicator" /></a>
        <a className="nav-link" href="#review-guide"><span aria-hidden="true">≡</span> How review works</a></nav>
      <div className="sidebar-scope"><p className="nav-caption">REVIEW INPUTS</p><p><span className="availability-dot" />Codebase upload</p><p><span className="availability-dot" />Public GitHub repository</p><p><span className="availability-dot" />Website URL <small>Readiness gated</small></p></div>
      <div className="sidebar-note"><span className="eyebrow">Built for a closer look.</span><p>Real checks. Masked evidence.<br />Repairs you can act on.</p><span className="version-tag">CY-02 / LOCAL WORKSPACE</span></div>
    </aside>
    <main id="workspace" tabIndex={-1}>
    <header className="workspace-header"><div className="breadcrumb">Workspace <span aria-hidden="true">/</span> <strong>Source review</strong></div>
      <span className={`connection connection-${health}`} role="status"><span className="connection-dot" />{health === 'checking' ? 'Checking the API connection…' : health === 'ok' ? 'API connected · contract v1' : 'API unavailable. Start the backend and retry this page.'}</span></header>
    <section className="intro" aria-labelledby="title">
      <div><p className="eyebrow intro-eyebrow"><span className="intro-line" /> FROM SOURCE TO A CLEAR NEXT STEP</p>
      <h1 id="title">Evidence before confidence<span>.</span></h1>
      <p className="lede">Find the risks hiding in your code. Understand the evidence.<br className="desktop-break" /> Leave with a concrete plan to fix them.</p></div>
      <div className="intro-stamp"><span aria-hidden="true">⌘</span><div>Built for your next fix<small>JS / TS · Web configuration</small></div></div>
    </section>
    <SourceIntake />
    <section id="review-guide" className="review-guide" aria-labelledby="guide-title"><div><p className="eyebrow">THE REVIEW PROCESS</p><h2 id="guide-title">A finding is the start.<br />Context makes it useful.</h2><p>Static checks highlight candidates for review. Confirm the impact in your application before making changes.</p></div>
      <ol><li><strong>Submit authorized source</strong><span>Choose a source tree or an exact public repository revision.</span></li><li><strong>Inspect the evidence</strong><span>Review affected files, real locations, confidence and coverage.</span></li><li><strong>Take the next step</strong><span>Copy repair guidance. Rotate exposed credentials separately.</span></li></ol></section>
    <footer><span>VibeGuard <span className="muted">/ Evidence before confidence.</span></span><span>Review only code you are authorized to assess.</span></footer>
  </main>
  </div>
}

