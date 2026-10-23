import { useRef, useState } from 'react'
import type { components } from './generated/api'
type Scan = components['schemas']['Scan']
type Result = components['schemas']['Comparison']
const labels = { still_detected: 'Still detected', not_detected: 'Not detected', newly_detected: 'Newly detected', unverified: 'Unverified' }
export default function Comparison({ baseline, current, result }: { baseline: Scan; current: Scan; result: Result }) {
  const [selected, setSelected] = useState(0)
  const detail = useRef<HTMLElement>(null)
  const buttons = useRef<(HTMLButtonElement | null)[]>([])
  const active = result.items[selected]
  function evidence(scan: Scan, id: string | null | undefined, label: string) {
    const finding = scan.findings.find(item => item.id === id)
    return <article><h4>{label}</h4><p>{scan.input.revision ?? scan.input.observation_id ?? scan.scan_id}</p>
      <p>{scan.input.repository ?? scan.input.target_redacted ?? scan.input.display_name}</p>
      {finding ? <><p>{finding.scanner} · {finding.rule_id} · {finding.severity}</p><p>{finding.location.kind === 'source' ? `${finding.location.path}:${finding.location.line_start}` : finding.location.url_redacted}</p><pre>{finding.evidence_redacted}</pre></> : <p>No paired finding observed. Review the comparison reason and coverage.</p>}
      <p>{scan.coverage.completed_count}/{scan.coverage.required_count} required checks · {scan.coverage.inspected.length} inspected resources</p>
      <details><summary>Coverage and exclusions</summary>{scan.tools.filter(tool => tool.required).map(tool => <p key={tool.name}>{tool.name}: {tool.status} · {tool.version ?? 'unknown version'} · image {tool.image_digest ?? 'unknown'} · rules {tool.rules_fingerprint ?? 'unknown'}</p>)}{scan.coverage.exclusions.map((item, index) => <p key={index}>{item.resource_key}: {item.reason}</p>)}</details>
    </article>
  }
  return <section aria-label="Rescan comparison"><h3>Before and after · {result.status}</h3><p>Not detected means no observation in comparable checks. It does not prove repair or credential rotation.</p>
    {result.items.length === 0 && <p>No findings were observed. Inspect coverage before drawing conclusions.</p>}
    <ul className="comparison-list" aria-label="Comparison findings">{result.items.map((item, index) => <li key={`${item.baseline_finding_id}-${item.new_finding_id}`}><button ref={node => { buttons.current[index] = node }} aria-pressed={selected === index} onClick={() => { setSelected(index); if (matchMedia('(max-width: 767px)').matches) detail.current?.focus() }}>{labels[item.status]} · {baseline.findings.find(f => f.id === item.baseline_finding_id)?.title ?? current.findings.find(f => f.id === item.new_finding_id)?.title}</button></li>)}</ul>
    {active && <section ref={detail} tabIndex={-1} aria-label="Paired evidence"><button onClick={() => buttons.current[selected]?.focus()}>Back to comparison selection</button><h4>{labels[active.status]}</h4><p>Reason: {active.reason_code.replaceAll('_', ' ')}</p><div className="paired-evidence">{evidence(baseline, active.baseline_finding_id, 'Before · baseline')}{evidence(current, active.new_finding_id, 'After · new scan')}</div></section>}
    {result.human_actions.length > 0 && <aside><h4>Retained human actions</h4><ul>{result.human_actions.map(action => <li key={action}>{action}</li>)}</ul></aside>}
  </section>
}
