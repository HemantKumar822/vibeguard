import { useEffect, useRef, useState } from 'react'
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
  const [deletion, setDeletion] = useState<components['schemas']['Deletion'] | null>(null)
  const csrf = useRef('')
  const confirmation = useRef<HTMLDialogElement>(null)
  const scanId = scan?.scan_id
  const scanStatus = scan?.status
  const deletionId = deletion?.operation_id
  const deletionStatus = deletion?.status
  useEffect(() => {
    if (!scanId || !scanStatus || !['queued', 'running'].includes(scanStatus)) return
    const controller = new AbortController()
    const timer = setInterval(async () => {
      try {
        const response = await fetch(`/api/v1/scans/${scanId}`, { signal: controller.signal })
        if (response.status === 404) { clearInterval(timer); setScan(null); setError('Scan is unavailable or expired.'); return }
        if (!response.ok) throw new Error('Scan status is temporarily unavailable.')
        setScan(await response.json())
      } catch (failure) { if (!controller.signal.aborted) setError(failure instanceof Error ? failure.message : 'Connection interrupted.') }
    }, 1000)
    return () => { clearInterval(timer); controller.abort() }
  }, [scanId, scanStatus])
  useEffect(() => {
    if (!deletionId || deletionStatus === 'complete') return
    const controller = new AbortController()
    const timer = setInterval(async () => {
      try {
        const response = await fetch(`/api/v1/deletions/${deletionId}`, { signal: controller.signal })
        if (response.status === 404) { clearInterval(timer); setDeletion(null); setError('Deletion operation is unavailable.'); return }
        if (response.ok) setDeletion(await response.json())
      } catch { /* Keep the last observed cleanup state during a disconnect. */ }
    }, 1000)
    return () => { clearInterval(timer); controller.abort() }
  }, [deletionId, deletionStatus])
  async function remove() {
    confirmation.current?.close()
    if (!scan) return
    try {
      const response = await fetch(`/api/v1/scans/${scan.scan_id}`, { method: 'DELETE', headers: { 'X-CSRF-Token': csrf.current } })
      if (!response.ok) throw new Error('Deletion could not be requested. Reconnect the session and retry.')
      setDeletion(await response.json()); setScan(null)
    } catch (failure) { setError(failure instanceof Error ? failure.message : 'Connection interrupted.') }
  }
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
      csrf.current = csrf_token
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
    {scan && <div role="status"><h3>Accepted · {scan.status}</h3>
      <ul>{scan.tools?.map(tool => <li key={tool.name}>{tool.name}: {tool.status}{tool.reason ? ` (${tool.reason})` : ''}</li>)}</ul>
      {scan.warnings?.map((warning, index) => <p key={index}>{warning}</p>)}
      {scan.error && <p role="alert">{scan.error.message}</p>}
      {scan.repair && <p>{scan.repair.prompt_redacted}</p>}
      <button type="button" onClick={() => confirmation.current?.showModal()}>Delete scan</button>
      <p>Scan ID: {scan.scan_id}</p><h4>Accepted files</h4><ul>{scan.accepted_files?.map(path => <li key={path}>{path}</li>)}</ul>
      <h4>Exclusions</h4><ul>{scan.coverage.exclusions.map(item => <li key={item.resource_key}>{item.resource_key}: {item.reason}</li>)}</ul></div>}
    {deletion && <p role="status">Cleanup: {deletion.status}{deletion.status === 'failed' ? ' · Cleanup is incomplete; the coordinator will retry.' : ''}</p>}
    <dialog ref={confirmation}><h3>Delete this scan and source?</h3><p>Access is revoked immediately. Cleanup status remains visible.</p><button autoFocus onClick={() => confirmation.current?.close()}>Cancel</button><button onClick={remove}>Delete scan</button></dialog>
  </section>
}

