import type { components } from '../../shared/api/generated'

type Scan = components['schemas']['Scan']
export function reportMarkdown(scan: Scan) {
  const lines = ['# VibeGuard security review', '', `Scan: ${scan.scan_id}`, `Status: ${scan.status}`,
    `Input: ${scan.input.target_redacted ?? scan.input.repository ?? 'Uploaded source tree'}`,
    `Revision / observation: ${scan.input.revision ?? scan.input.observation_id ?? 'Uploaded snapshot'}`,
    `Coverage: ${scan.coverage.completed_count}/${scan.coverage.required_count} required checks completed.`,
    '', 'Automated findings are candidates for review. Absence does not prove security or successful credential rotation.', '', '## Checks']
  for (const tool of scan.tools) lines.push(`- ${tool.name}: ${tool.status}${tool.reason ? ` (${tool.reason})` : ''}`)
  lines.push('', '## Coverage limitations', ...scan.warnings.map(warning => `- ${warning}`),
    ...scan.coverage.exclusions.map(item => `- ${item.resource_key}: ${item.reason}`), '', '## Findings')
  if (!scan.findings.length) lines.push(scan.status === 'complete' ? 'No findings detected within completed checks.' : 'No findings available; coverage is incomplete.')
  for (const finding of scan.findings) {
    const location = finding.location.kind === 'source' ? `${finding.location.path}:${finding.location.line_start ?? 'unknown'}` : `${finding.location.url_redacted} | ${finding.location.part}${finding.location.line_start ? ` | line ${finding.location.line_start}` : ''}${finding.location.parameter_redacted ? ` | ${finding.location.parameter_redacted}` : ''}`
    lines.push('', `### ${finding.severity.toUpperCase()}: ${finding.title}`, `Location: ${location}`,
      `Rule: ${finding.rule_id} | Confidence: ${finding.confidence}`, finding.confidence_reason,
      '', `Evidence (masked): ${finding.evidence_redacted ?? 'Unavailable'}`, '', finding.explanation, '', `Required change: ${finding.fix_guidance}`, '', 'Verification:',
      ...finding.verification_steps.map(step => `- ${step}`), ...finding.human_actions.map(action => `- Human action: ${action}`))
  }
  if (scan.repair) lines.push('', '## Consolidated repair prompt', `Guidance: ${scan.repair.mode} (${scan.repair.status})`, scan.repair.model_reason ?? '', '', scan.repair.prompt_redacted)
  // Render the complete report literally: source-controlled names cannot become
  // links, remote images or HTML when a Markdown viewer opens the export.
  const text = lines.join('\n')
  const longest = Math.max(2, ...Array.from(text.matchAll(/`+/g), match => match[0].length))
  const fence = '`'.repeat(longest + 1)
  return `${fence}text\n${text}\n${fence}\n`
}
export function downloadReport(scan: Scan) {
  const url = URL.createObjectURL(new Blob([reportMarkdown(scan)], { type: 'text/markdown;charset=utf-8' }))
  const link = document.createElement('a')
  link.href = url; link.download = `vibeguard-${scan.scan_id}.md`
  document.body.append(link); link.click(); link.remove()
  setTimeout(() => URL.revokeObjectURL(url), 1000)
}
