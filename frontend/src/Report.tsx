import { useState } from 'react'
import type { components } from './generated/api'

type Scan = components['schemas']['Scan']
const rank = { critical: 0, high: 1, medium: 2, low: 3, info: 4 }

export default function Report({ scan }: { scan: Scan }) {
  const [severity, setSeverity] = useState('all')
  const [category, setCategory] = useState('all')
  const [tool, setTool] = useState('all')
  const [query, setQuery] = useState('')
  const [selected, setSelected] = useState<string | null>(null)
  const [copy, setCopy] = useState('')
  const findings = scan.findings ?? []
  const visible = findings.filter(item => (severity === 'all' || item.severity === severity)
    && (category === 'all' || item.category === category) && (tool === 'all' || item.scanner === tool)
    && `${item.title} ${item.rule_id} ${item.location.kind === 'source' ? item.location.path : item.location.url_redacted}`.toLowerCase().includes(query.toLowerCase()))
    .sort((a, b) => rank[a.severity] - rank[b.severity] || a.rule_id.localeCompare(b.rule_id))
  const active = visible.find(item => item.id === selected) ?? visible[0]
  async function copyPrompt() {
    try {
      await navigator.clipboard.writeText(scan.repair!.prompt_redacted)
      setCopy('Repair prompt copied.')
    } catch { setCopy('Clipboard unavailable. Select and copy the sanitized text below manually.') }
  }
  return <section aria-label="Investigate and repair" className="report">
    {scan.mode === 'website' && <div className="attribution"><h3>Website observation</h3><p>{scan.input.target_redacted}</p><p>Observation: <code>{scan.input.observation_id}</code></p><p>Passive review of captured responses and fetched text assets. No browser JavaScript, authenticated pages or private backend source was assessed.</p></div>}
    {scan.input?.repository && <div className="attribution"><h3>Repository snapshot</h3>
      <p>{scan.input.repository}</p><p>Requested ref: <code>{scan.input.requested_ref}</code></p>
      <p>Resolved commit: <code>{scan.input.revision ?? 'Not resolved'}</code></p>
      <p>One public source snapshot; private repositories and history are unsupported.</p></div>}
    <h3>Checks and coverage</h3>
    <p>{scan.coverage.completed_count ?? 0}/{scan.coverage.required_count ?? 2} required checks completed with intended coverage.</p>
    <ul className="tool-states">{scan.tools?.map(item => <li className="tool-state" data-state={item.status} key={item.name}>{item.name}: {item.status}{item.reason ? ` (${item.reason})` : ''}
      {item.version && <> · v{item.version}</>}
      {item.started_at && <> · started {new Date(item.started_at).toLocaleTimeString()}</>}
      {item.finished_at && <> · finished {new Date(item.finished_at).toLocaleTimeString()}</>}
    </li>)}</ul>
    <p className="muted">Static checks produce candidates for review. They do not prove the application is secure.</p>
    {scan.warnings?.length > 0 && <details className="coverage-notes" open={scan.status === 'partial' || scan.status === 'failed'}><summary>Review limits and notes · {scan.warnings.length}</summary>{scan.warnings.map((warning, index) => <p key={index}>{warning}</p>)}</details>}
    {scan.error && <p role="alert">{scan.error.message}</p>}
    {['complete', 'partial', 'failed'].includes(scan.status) && <>
      <h3>Findings · {findings.length}</h3>
      <div className="filters">
        <label>Severity<select value={severity} onChange={event => setSeverity(event.target.value)}><option value="all">All severities</option>{Object.keys(rank).map(value => <option key={value}>{value}</option>)}</select></label>
        <label>Category<select value={category} onChange={event => setCategory(event.target.value)}><option value="all">All categories</option>{['credential', 'unsafe_input', 'insecure_configuration', 'access_check', 'other'].map(value => <option key={value}>{value}</option>)}</select></label>
        <label>Tool<select value={tool} onChange={event => setTool(event.target.value)}><option value="all">All tools</option>{['gitleaks', 'semgrep', 'zap', 'asset_secrets'].map(value => <option key={value}>{value}</option>)}</select></label>
        <label>Search location or rule<input type="search" value={query} onChange={event => setQuery(event.target.value)} /></label>
      </div>
      {findings.length === 0 ? <p>{scan.status === 'complete' ? 'No findings detected within completed checks.' : 'No findings available. Review incomplete checks before drawing conclusions.'}</p>
        : visible.length === 0 ? <p role="status">No findings match these filters. The report still contains {findings.length} findings.</p>
          : <div className="investigation"><ul aria-label="Findings">{visible.map(item => <li key={item.id}><button type="button" aria-pressed={active?.id === item.id} onClick={() => setSelected(item.id)}>
            <span className="severity-badge" data-severity={item.severity}>{item.severity}</span><strong>{item.title}</strong><span>{item.location.kind === 'source' ? `${item.location.path}:${item.location.line_start ?? 'unknown'}` : `${item.location.url_redacted}${item.location.line_start ? ` · line ${item.location.line_start}` : ''}`}</span>
          </button></li>)}</ul>
            {active && <article aria-label="Selected finding"><h4>{active.title}</h4><p>{active.scanner} · {active.rule_id} · {active.severity}</p>
              <p>Confidence: {active.confidence}. {active.confidence_reason}</p>
              <p>{active.location.kind === 'source' ? `${active.location.path}:${active.location.line_start ?? 'unknown'}` : `${active.location.url_redacted} · ${active.location.part}${active.location.line_start ? ` · line ${active.location.line_start}` : ''}`}</p>
              <pre>{active.evidence_redacted ?? 'No source excerpt is available.'}</pre><h4>Impact and context</h4><p>{active.explanation}</p>
              <h4>Recommended fix</h4><p>{active.fix_guidance}</p><h4>Verification</h4><ul>{active.verification_steps.map(step => <li key={step}>{step}</li>)}</ul>
              {active.human_actions.length > 0 && <><h4>Separate human actions</h4><ul>{active.human_actions.map(action => <li key={action}>{action}</li>)}</ul></>}
            </article>}</div>}
    </>}
    {scan.repair && <section aria-label="Repair prompt"><h3>Consolidated repair prompt</h3>
      <p>Deterministic guidance · no AI required.</p><button className="primary-button" type="button" onClick={copyPrompt}>Copy repair prompt</button><p role="status">{copy}</p>
      <label>Sanitized repair prompt<textarea readOnly value={scan.repair.prompt_redacted} aria-label="Sanitized repair prompt" /></label>
      {scan.repair.human_actions?.length > 0 && <><h4>Separate human actions</h4><ul>{scan.repair.human_actions.map(action => <li key={action}>{action}</li>)}</ul></>}
    </section>}
    <details><summary>Accepted inventory and exclusions</summary><h4>Accepted files</h4><ul>{scan.accepted_files?.map(path => <li key={path}>{path}</li>)}</ul>
      <h4>Inspected resources</h4><ul>{scan.coverage.inspected?.map(path => <li key={path}>{path}</li>)}</ul>
      <h4>Exclusions</h4><ul>{scan.coverage.exclusions.map(item => <li key={item.resource_key}>{item.resource_key}: {item.reason}</li>)}</ul>
      <p>Rules fingerprint: <code>{scan.coverage.rules_fingerprint ?? 'No rules executed'}</code></p></details>
  </section>
}
