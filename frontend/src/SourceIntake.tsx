import { useEffect, useRef, useState } from 'react'
import type { components } from './generated/api'
import Report from './Report'
type Scan = components['schemas']['Scan']

export default function SourceIntake() {
  const [mode, setMode] = useState<'codebase' | 'repository'>('codebase')
  const [repository, setRepository] = useState('')
  const [ref, setRef] = useState('')
  const [reconnectId, setReconnectId] = useState('')
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
  async function sessionToken() {
    const response = await fetch('/api/v1/session', { method: 'POST', signal: AbortSignal.timeout(15_000) })
    if (!response.ok) throw new Error('Session unavailable. Check the configured same-origin runtime.')
    const data: components['schemas']['SessionResponse'] = await response.json()
    csrf.current = data.csrf_token
    return data.csrf_token
  }
  async function reconnect(id = reconnectId) {
    if (!/^[a-f0-9]{32}$/.test(id)) { setError('Enter the 32-character Scan ID from your report.'); return }
    try {
      await sessionToken()
      const response = await fetch(`/api/v1/scans/${id}`, { signal: AbortSignal.timeout(15_000) })
      if (!response.ok) throw new Error('Scan is unavailable, expired, or belongs to another session.')
      setScan(await response.json()); setError(''); setDeletion(null)
    } catch (failure) { setError(failure instanceof Error ? failure.message : 'Reconnect failed. Retry the same Scan ID.') }
  }
  useEffect(() => {
    if (!scanId || !scanStatus || !['queued', 'running'].includes(scanStatus)) return
    const controller = new AbortController()
    let polling = false
    const timer = setInterval(async () => {
      if (polling) return
      polling = true
      try {
        const response = await fetch(`/api/v1/scans/${scanId}`, { signal: AbortSignal.any([controller.signal, AbortSignal.timeout(15_000)]) })
        if (controller.signal.aborted) return
        if (response.status === 404) { clearInterval(timer); setScan(null); setError('Scan is unavailable or expired.'); return }
        if (!response.ok) throw new Error('Scan status is temporarily unavailable.')
        const updated: Scan = await response.json()
        if (!controller.signal.aborted) { setScan(updated); setError('') }
      } catch (failure) { if (!controller.signal.aborted) setError(failure instanceof Error ? failure.message : 'Connection interrupted.') }
      finally { polling = false }
    }, 1000)
    return () => { clearInterval(timer); controller.abort() }
  }, [scanId, scanStatus])
  useEffect(() => {
    if (!deletionId || deletionStatus === 'complete') return
    const controller = new AbortController()
    let polling = false
    const timer = setInterval(async () => {
      if (polling) return
      polling = true
      try {
        const response = await fetch(`/api/v1/deletions/${deletionId}`, { signal: AbortSignal.any([controller.signal, AbortSignal.timeout(15_000)]) })
        if (controller.signal.aborted) return
        if (response.status === 404) { clearInterval(timer); setDeletion(null); setError('Deletion operation is unavailable.'); return }
        if (response.ok) {
          const updated: components['schemas']['Deletion'] = await response.json()
          if (!controller.signal.aborted) setDeletion(updated)
        }
      } catch { /* Keep the last observed cleanup state during a disconnect. */ }
      finally { polling = false }
    }, 1000)
    return () => { clearInterval(timer); controller.abort() }
  }, [deletionId, deletionStatus])
  async function remove() {
    confirmation.current?.close()
    if (!scan) return
    const deletingId = scan.scan_id
    try {
      const response = await fetch(`/api/v1/scans/${scan.scan_id}`, { method: 'DELETE', headers: { 'X-CSRF-Token': csrf.current }, signal: AbortSignal.timeout(15_000) })
      if (!response.ok) throw new Error('Deletion could not be requested. Reconnect the session and retry.')
      setDeletion(await response.json())
      setScan(current => current?.scan_id === deletingId ? null : current)
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
    if (mode === 'codebase' && (!files.length || names.length !== files.length || names.some(name => !name))) {
      setError('Select files and supply exactly one relative path per file, in the displayed order.'); return
    }
    if (mode === 'codebase' && (files.length > 5000 || files.some(file => file.size > 2 * 1024 * 1024) || files.reduce((sum, file) => sum + file.size, 0) > 25 * 1024 * 1024)) {
      setError('Selection exceeds the upload limits.'); return
    }
    setPending(true)
    retryKey.current ??= crypto.randomUUID()
    try {
      const csrf_token = await sessionToken()
      const metadata: components['schemas']['CodebaseMetadata'] = { mode: 'codebase', authorization_confirmed: true,
        allow_external_ai: sharing, files: names.map((relative_path, index) => ({ part_id: `file_${index}`, relative_path })) }
      const body = new FormData()
      body.append('metadata', JSON.stringify(metadata))
      files.forEach((file, index) => body.append(`file_${index}`, file))
      const response = await fetch('/api/v1/scans', { method: 'POST', signal: AbortSignal.timeout(75_000),
        headers: { 'X-CSRF-Token': csrf_token, 'Idempotency-Key': retryKey.current, ...(mode === 'repository' ? { 'Content-Type': 'application/json' } : {}) },
        body: mode === 'repository' ? JSON.stringify({ mode, repository_url: repository, ref: ref || null, authorization_confirmed: true, allow_external_ai: sharing }) : body })
      if (!response.ok) {
        const result: components['schemas']['ErrorResponse'] = await response.json()
        throw new Error(`Submission rejected (${result.error.code}). Check permission, paths, mapping and limits.`)
      }
      setScan(await response.json())
      setDeletion(null)
      retryKey.current = null
    } catch (failure) {
      setError(failure instanceof Error ? failure.message : 'Connection interrupted. Submission status is unknown.')
    } finally { setPending(false) }
  }
  return <section className="panel" aria-labelledby="source-title">
    <h2 id="source-title">Submit authorized source</h2>
    <p>JS/TS and relevant web configuration. Public GitHub snapshots supported. Website intake is unavailable.</p>
    <p className="muted">25 MiB total · 5,000 files · 2 MiB per file · depth 20 · 240 UTF-8 bytes per path</p>
    <form onSubmit={submit}>
      <label>Submission mode<select value={mode} disabled={pending} onChange={event => { changed(); setMode(event.target.value as 'codebase' | 'repository') }}><option value="codebase">Codebase</option><option value="repository">Repository</option></select></label>
      {mode === 'repository' ? <>
        <label>Public GitHub repository URL<input type="url" required value={repository} placeholder="https://github.com/owner/repository" disabled={pending} onChange={event => { changed(); setRepository(event.target.value) }} /></label>
        <label>Branch, tag, or commit (optional)<input value={ref} maxLength={256} disabled={pending} onChange={event => { changed(); setRef(event.target.value) }} /></label>
        <p>Public repositories only. One resolved commit; no private credentials, history, submodules, LFS downloads, hooks or builds.</p>
      </> : <>
      <label>Choose directory<input type="file" multiple {...{ webkitdirectory: '' }} onChange={event => select(event.currentTarget, true)} disabled={pending} /></label>
      <p>If directory selection is unavailable, choose mapped files and provide their original relative paths.</p>
      <label>Choose mapped files<input type="file" multiple onChange={event => select(event.currentTarget, false)} disabled={pending} /></label>
      {mapped && <label>Relative paths, one per selected file<textarea value={paths} onChange={event => { if (event.target.value !== paths) changed(); setPaths(event.target.value) }} disabled={pending} /></label>}
      {files.length > 0 && <ol>{files.map((file, index) => <li key={index}>{mapped ? file.name : file.webkitRelativePath} · {file.size} bytes</li>)}</ol>}
      </>}
      <label><input type="checkbox" checked={permission} onChange={event => { changed(); setPermission(event.target.checked) }} disabled={pending} required />I have permission to review this source.</label>
      <label><input type="checkbox" checked={sharing} onChange={event => { changed(); setSharing(event.target.checked) }} disabled={pending} />Allow external AI sharing for this submission (AI is currently unavailable).</label>
      <button type="submit" disabled={pending || !permission || (mode === 'codebase' ? files.length === 0 : !repository)}>{pending ? 'Submitting…' : mode === 'repository' ? 'Review repository' : 'Submit source tree'}</button>
    </form>
    <details><summary>Reconnect to an existing scan</summary><p>Use the same browser session and Scan ID after refresh. Reconnecting does not submit new work. Lost cookies cannot be recovered.</p>
      <label>Scan ID<input value={reconnectId} maxLength={32} onChange={event => setReconnectId(event.target.value)} /></label><button type="button" onClick={() => reconnect()}>Reconnect</button></details>
    {error && <p role="alert">{error}</p>}
    {scan && <div><h3 role="status">Accepted · {scan.status}</h3>
      <Report scan={scan} key={scan.scan_id} />
      <button type="button" onClick={() => confirmation.current?.showModal()}>Delete scan</button>
      <p>Scan ID: <code>{scan.scan_id}</code></p></div>}
    {deletion && <p role="status">Cleanup: {deletion.status}{deletion.status === 'failed' ? ' · Cleanup is incomplete; the coordinator will retry.' : ''}</p>}
    <dialog ref={confirmation}><h3>Delete this scan and source?</h3><p>Access is revoked immediately. Cleanup status remains visible.</p><button autoFocus onClick={() => confirmation.current?.close()}>Cancel</button><button onClick={remove}>Delete scan</button></dialog>
  </section>
}

