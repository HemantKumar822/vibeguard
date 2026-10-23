import { useRef, useState } from 'react'
import type { components } from './generated/api'
type Scan = components['schemas']['Scan']

export default function SourceIntake() {
  const [files, setFiles] = useState<File[]>([])
  const [paths, setPaths] = useState('')
  const [mapped, setMapped] = useState(false)
  const [permission, setPermission] = useState(false)
  const [sharing, setSharing] = useState(false)
  const [pending, setPending] = useState(false)
  const [error, setError] = useState('')
  const [scan, setScan] = useState<Scan | null>(null)
  const retryKey = useRef<string | null>(null)
  function changed() { retryKey.current = null }
  function select(input: HTMLInputElement, directory: boolean) {
    changed()
    const selected = Array.from(input.files ?? [])
    setFiles(selected); setMapped(!directory); setPaths(''); setError('')
    if (directory && selected.some(file => !file.webkitRelativePath)) {
      setFiles([]); setError('This browser lost directory paths. Use mapped files and enter one relative path per file.')
    }
  }
  async function submit(event: React.FormEvent) {
    event.preventDefault()
    if (pending) return
    if (!permission) { setError('Permission confirmation is required.'); return }
    setError('')
    const names = mapped ? paths.split('\n') : files.map(file => file.webkitRelativePath)
    if (!files.length || names.length !== files.length || names.some(name => !name)) {
      setError('Select files and supply exactly one relative path per file, in the displayed order.'); return
    }
    if (files.length > 5000 || files.some(file => file.size > 2 * 1024 * 1024) || files.reduce((sum, file) => sum + file.size, 0) > 25 * 1024 * 1024) {
      setError('Selection exceeds the upload limits.'); return
    }
    setPending(true)
    retryKey.current ??= crypto.randomUUID()
    try {
      const session = await fetch('/api/v1/session', { method: 'POST' })
      if (!session.ok) throw new Error('Session unavailable. Check the configured same-origin runtime.')
      const { csrf_token }: components['schemas']['SessionResponse'] = await session.json()
      const metadata: components['schemas']['CodebaseMetadata'] = { mode: 'codebase', authorization_confirmed: true,
        allow_external_ai: sharing, files: names.map((relative_path, index) => ({ part_id: `file_${index}`, relative_path })) }
      const body = new FormData()
      body.append('metadata', JSON.stringify(metadata))
      files.forEach((file, index) => body.append(`file_${index}`, file))
      const response = await fetch('/api/v1/scans', { method: 'POST', headers: { 'X-CSRF-Token': csrf_token, 'Idempotency-Key': retryKey.current }, body })
      if (!response.ok) {
        const result: components['schemas']['ErrorResponse'] = await response.json()
        throw new Error(`Submission rejected (${result.error.code}). Check permission, paths, mapping and limits.`)
      }
      setScan(await response.json())
      retryKey.current = null
    } catch (failure) {
      setError(failure instanceof Error ? failure.message : 'Connection interrupted. Submission status is unknown.')
    } finally { setPending(false) }
  }
  return <section className="panel" aria-labelledby="source-title">
    <h2 id="source-title">Submit a source tree</h2>
    <p>JS/TS and relevant web configuration. Repository and website intake are unavailable.</p>
    <p className="muted">25 MiB total · 5,000 files · 2 MiB per file · depth 20 · 240 UTF-8 bytes per path</p>
    <form onSubmit={submit}>
      <label>Choose directory<input type="file" multiple {...{ webkitdirectory: '' }} onChange={event => select(event.currentTarget, true)} disabled={pending} /></label>
      <p>If directory selection is unavailable, choose mapped files and provide their original relative paths.</p>
      <label>Choose mapped files<input type="file" multiple onChange={event => select(event.currentTarget, false)} disabled={pending} /></label>
      {mapped && <label>Relative paths, one per selected file<textarea value={paths} onChange={event => { if (event.target.value !== paths) changed(); setPaths(event.target.value) }} disabled={pending} /></label>}
      {files.length > 0 && <ol>{files.map((file, index) => <li key={index}>{mapped ? file.name : file.webkitRelativePath} · {file.size} bytes</li>)}</ol>}
      <label><input type="checkbox" checked={permission} onChange={event => { changed(); setPermission(event.target.checked) }} disabled={pending} required />I have permission to review this source.</label>
      <label><input type="checkbox" checked={sharing} onChange={event => { changed(); setSharing(event.target.checked) }} disabled={pending} />Allow external AI sharing for this submission (AI is currently unavailable).</label>
      <button type="submit" disabled={pending || !permission || files.length === 0}>{pending ? 'Submitting…' : 'Submit source tree'}</button>
    </form>
    {error && <p role="alert">{error}</p>}
    {scan && <div role="status"><h3>Accepted · {scan.status}</h3><p>No scanner has run. Scanner orchestration is unavailable.</p>
      <p>Scan ID: {scan.scan_id}</p><h4>Accepted files</h4><ul>{scan.accepted_files?.map(path => <li key={path}>{path}</li>)}</ul>
      <h4>Exclusions</h4><ul>{scan.coverage.exclusions.map(item => <li key={item.resource_key}>{item.resource_key}: {item.reason}</li>)}</ul></div>}
  </section>
}

