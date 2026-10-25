import type { components } from '../../shared/api/generated'

type Scan = components['schemas']['Scan']
type Tool = components['schemas']['Tool']
const names: Record<Tool['name'], string> = {
  gitleaks: 'Exposed credentials', semgrep: 'Code security',
  zap: 'Website security', asset_secrets: 'Browser-visible credentials',
}
const descriptions: Record<Tool['name'], string> = {
  gitleaks: 'Gitleaks · secrets in submitted source',
  semgrep: 'Semgrep · input handling, configuration and access checks',
  zap: 'OWASP ZAP · passive checks on captured responses',
  asset_secrets: 'Gitleaks · secrets in captured text assets',
}
const labels: Record<Tool['status'], string> = {
  queued: 'Waiting', running: 'Running', complete: 'Completed',
  failed: 'Failed', timed_out: 'Timed out', skipped: 'Skipped',
}
function timestamp(value: string) {
  return new Date(value).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
}
export default function ScanActivity({ scan }: { scan: Scan }) {
  const active = scan.status === 'queued' || scan.status === 'running'
  const tools = scan.tools.filter(tool => tool.applicable)
  const excluded = scan.tools.filter(tool => !tool.applicable)
  const running = tools.find(tool => tool.status === 'running')
  const events: { id: string; at: string; message: string }[] = [
    { id: 'accepted', at: scan.created_at, message: 'Submission accepted into the review queue.' },
  ]
  if (scan.started_at) events.push({ id: 'started', at: scan.started_at, message: 'Review started. Preparing authorized input.' })
  for (const tool of tools) {
    if (tool.started_at) events.push({ id: `${tool.name}-start`, at: tool.started_at, message: `${names[tool.name]} started.` })
    if (tool.finished_at) events.push({ id: `${tool.name}-finish`, at: tool.finished_at, message: `${names[tool.name]}: ${labels[tool.status].toLowerCase()}.${tool.status === 'complete' && !tool.coverage.scope_complete ? ' Coverage is incomplete.' : ''}` })
  }
  if (scan.finished_at) events.push({ id: 'finished', at: scan.finished_at, message: `Review finished: ${scan.status}.` })
  events.sort((a, b) => Date.parse(a.at) - Date.parse(b.at))
  return <section className="scan-activity" aria-label="Checks and coverage">
    <div className="activity-heading"><div><p className="eyebrow">SCAN ACTIVITY</p><h3>Checks and coverage</h3></div>
      <span className={`activity-state ${active ? 'is-live' : ''}`}>{active ? 'Live status' : 'Run summary'}</span></div>
    <p className="activity-summary" role="status">{active
      ? running ? `${names[running.name]} is running.` : scan.status === 'queued' ? 'Waiting for an available worker.' : tools.every(tool => !['queued', 'running'].includes(tool.status)) ? 'Preparing the report and repair guidance.' : 'Preparing input for the next check.'
      : `${scan.coverage.completed_count}/${scan.coverage.required_count} required checks completed with intended coverage.`}</p>
    <ol className="check-list" aria-label="Security checks">{tools.map(tool => <li key={tool.name} data-state={tool.status}>
      <span className="check-symbol" aria-hidden="true">{tool.status === 'complete' ? '✓' : ['failed', 'timed_out'].includes(tool.status) ? '!' : tool.status === 'skipped' ? '–' : '·'}</span>
      <div className="check-description"><strong>{names[tool.name]}</strong><span>{descriptions[tool.name]}</span>
        {tool.status === 'complete' && <small>{tool.coverage.inspected.length} inspected resources{!tool.coverage.scope_complete ? ' · incomplete coverage' : ''}</small>}
        {(tool.error || tool.reason) && <small>{tool.error?.message ?? tool.reason}</small>}
      </div><span className="check-badge">{labels[tool.status]}</span>
    </li>)}</ol>
    <details className="activity-log" open={active}>
      <summary>Activity log <span>{events.length} recorded events</span></summary>
      <p className="field-help">Recorded scanner events from the latest status response. Individual rule execution and raw scanner output are not available.</p>
      <ol aria-label="Recorded scan events">{events.map(event => <li key={event.id}><time dateTime={event.at} title={new Date(event.at).toLocaleString()}>{timestamp(event.at)}</time><span>{event.message}</span></li>)}</ol>
    </details>
    <details className="technical-details"><summary>Scanner versions and skipped checks</summary>
      <ul>{scan.tools.map(tool => <li key={tool.name}>{tool.name}: {tool.status}{tool.version ? ` · v${tool.version}` : ''}{tool.reason ? ` · ${tool.reason}` : ''}</li>)}</ul>
      {excluded.length > 0 && <p className="field-help">{excluded.length} scanners do not apply to this input type.</p>}
    </details>
    <p className="field-help">Completed checks produce candidates for review, not a guarantee that the application is secure.</p>
  </section>
}
