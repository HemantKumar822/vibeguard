import { useEffect, useLayoutEffect, useRef, useState } from 'react'
import type { components } from '../../shared/api/generated'
import Report from '../report/Report'
import Comparison from '../comparison/Comparison'
type Scan = components['schemas']['Scan']

export default function SourceIntake() {
  const [mode, setMode] = useState<'codebase' | 'repository' | 'website'>('codebase')
  const [website, setWebsite] = useState('')
  const [repository, setRepository] = useState('')
  const [ref, setRef] = useState('')
  const [reconnectId, setReconnectId] = useState('')
  const [files, setFiles] = useState<File[]>([])
  const [paths, setPaths] = useState('')
  const [mapped, setMapped] = useState(false)
  const [permission, setPermission] = useState(false)
  const [sharing, setSharing] = useState(false)
  const [pending, setPending] = useState(false)
  const [inputOpen, setInputOpen] = useState(false)
  const [error, setError] = useState('')
  const [scan, setScan] = useState<Scan | null>(null)
  const [baseline, setBaseline] = useState<Scan | null>(null)
  const [repeat, setRepeat] = useState(false)
  const [comparison, setComparison] = useState<components['schemas']['Comparison'] | null>(null)
  const [comparisonError, setComparisonError] = useState('')
  const [comparisonRetry, setComparisonRetry] = useState(0)
  const [deletion, setDeletion] = useState<components['schemas']['Deletion'] | null>(null)
  const csrf = useRef('')
  const generation = useRef(0)
  const currentIdentity = useRef<string | null>(null)
  const pendingAdmission = useRef(false)
  const confirmation = useRef<HTMLDialogElement>(null)
  const resultHeading = useRef<HTMLHeadingElement>(null)
  const scanId = scan?.scan_id
  useEffect(() => { if (scanId) resultHeading.current?.focus() }, [scanId])
  useLayoutEffect(() => { currentIdentity.current = scanId ?? null }, [scanId])
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
    if (pendingAdmission.current) return
    const requestGeneration = ++generation.current
    setComparison(null); setComparisonError(''); setError('')
    if (!/^[a-f0-9]{32}$/.test(id)) { setError('Enter the 32-character Scan ID from your report.'); return }
    try {
      await sessionToken()
      const response = await fetch(`/api/v1/scans/${id}`, { signal: AbortSignal.timeout(15_000) })
      if (!response.ok) throw new Error('Scan is unavailable, expired, or belongs to another session.')
      const restored: Scan = await response.json()
      if (requestGeneration !== generation.current) return
      if (restored.scan_id !== id) throw new Error('Unexpected scan identity.')
      if (restored.baseline_id) {
        const original = await fetch(`/api/v1/scans/${restored.baseline_id}`, { signal: AbortSignal.timeout(15_000) })
        if (original.ok) {
          const originalScan: Scan = await original.json()
          if (requestGeneration !== generation.current) return
          if (originalScan.scan_id !== restored.baseline_id) throw new Error('Unexpected baseline identity.')
          setBaseline(originalScan)
        }
        else { if (requestGeneration !== generation.current) return; setBaseline(null); setComparisonError('Baseline report is unavailable or expired. Start a new submission.') }
      } else setBaseline(null)
      if (requestGeneration !== generation.current) return
      currentIdentity.current = restored.scan_id
      setScan(restored); setRepeat(false); setInputOpen(false); setError(''); setDeletion(null)
    } catch (failure) { if (requestGeneration === generation.current) setError(failure instanceof Error ? failure.message : 'Reconnect failed. Retry the same Scan ID.') }
  }
  useEffect(() => {
    if (!scanId || !scanStatus || !['queued', 'running'].includes(scanStatus)) return
    const controller = new AbortController()
    const stale = () => controller.signal.aborted || currentIdentity.current !== scanId
    let polling = false
    const timer = setInterval(async () => {
      if (polling) return
      polling = true
      try {
        const response = await fetch(`/api/v1/scans/${scanId}`, { signal: AbortSignal.any([controller.signal, AbortSignal.timeout(15_000)]) })
        if (stale()) return
        if (response.status === 404) { clearInterval(timer); setScan(null); setError('Scan is unavailable or expired.'); return }
        if (!response.ok) throw new Error('Scan status is temporarily unavailable.')
        const updated: Scan = await response.json()
        if (!stale() && updated.scan_id === scanId) { setScan(updated); setError('') }
      } catch (failure) { if (!stale()) setError(failure instanceof Error ? failure.message : 'Connection interrupted.') }
      finally { polling = false }
    }, 1000)
    return () => { clearInterval(timer); controller.abort() }
  }, [scanId, scanStatus])
  useEffect(() => {
    if (!baseline || !scan || scan.baseline_id !== baseline.scan_id || ['queued', 'running'].includes(scan.status)) return
    const controller = new AbortController()
    const requestGeneration = generation.current
    fetch(`/api/v1/scans/${baseline.scan_id}/comparisons/${scan.scan_id}`, { signal: AbortSignal.any([controller.signal, AbortSignal.timeout(15_000)]) })
      .then(async response => { if (!response.ok) throw new Error('Comparison or baseline is unavailable. Reconnect or start a new submission.'); return response.json() })
      .then((result: components['schemas']['Comparison']) => {
        if (controller.signal.aborted || requestGeneration !== generation.current || currentIdentity.current !== scan.scan_id) return
        if (result.baseline_id !== baseline.scan_id || result.new_id !== scan.scan_id) throw new Error('Unexpected comparison identity. Reconnect this scan.')
        setComparison(result); setComparisonError('')
      })
      .catch(failure => { if (!controller.signal.aborted && requestGeneration === generation.current && currentIdentity.current === scan.scan_id) setComparisonError(failure.message) })
    return () => controller.abort()
  }, [baseline, scan, comparisonRetry])
  function startRepeat() {
    if (!scan) return
    setBaseline(scan); setRepeat(true); setMode(scan.mode); setPermission(false); setSharing(false)
    setFiles([]); setPaths(''); setMapped(false); setComparison(null); setComparisonError(''); changed()
    setRepository(scan.input.repository ?? ''); setRef(''); setWebsite(scan.input.target_redacted?.includes('?') ? '' : scan.input.target_redacted ?? '')
    const heading = document.getElementById('source-title')
    heading?.scrollIntoView?.({ behavior: 'instant' })
    heading?.focus()
  }
  function newSubmission() { if (pendingAdmission.current) return; ++generation.current; setRepeat(false); setInputOpen(true); setBaseline(null); setComparison(null); setComparisonError(''); setPermission(false); setSharing(false); changed() }
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
    if (!scan || pendingAdmission.current) return
    const requestGeneration = ++generation.current
    setComparison(null); setComparisonError('')
    const deletingId = scan.scan_id
    try {
      const response = await fetch(`/api/v1/scans/${scan.scan_id}`, { method: 'DELETE', headers: { 'X-CSRF-Token': csrf.current }, signal: AbortSignal.timeout(15_000) })
      if (!response.ok) throw new Error('Deletion could not be requested. Reconnect the session and retry.')
      const deleted = await response.json()
      if (requestGeneration !== generation.current || currentIdentity.current !== deletingId) return
      setDeletion(deleted)
      currentIdentity.current = null
      setScan(current => current?.scan_id === deletingId ? null : current)
    } catch (failure) { setError(failure instanceof Error ? failure.message : 'Connection interrupted.') }
  }
  const retryKey = useRef<string | null>(null)
  function changed() { retryKey.current = null }
  function select(input: HTMLInputElement, directory: boolean) {
    changed()
    const selected = Array.from(input.files ?? [])
    const defaultPaths = selected.map(file => file.webkitRelativePath || file.name).join('\n')
    setFiles(selected); setMapped(!directory); setPaths(defaultPaths); setError('')
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
    pendingAdmission.current = true
    const requestGeneration = ++generation.current
    setComparison(null); setComparisonError('')
    setPending(true)
    retryKey.current ??= crypto.randomUUID()
    try {
      const csrf_token = await sessionToken()
      if (mode === 'website') {
        const response = await fetch('/api/v1/capabilities', { signal: AbortSignal.timeout(15_000) })
        if (!response.ok) throw new Error('Website readiness could not be checked. Retry without changing your input.')
        const capability: components['schemas']['Capabilities'] = await response.json()
        if (!capability.permitted_modes.includes('website')) throw new Error('Website scanning is unavailable: the required networking/ZAP safety verification is missing or stale.')
      }
      const metadata: components['schemas']['CodebaseMetadata'] = { mode: 'codebase', authorization_confirmed: true,
        allow_external_ai: sharing, files: names.map((relative_path, index) => ({ part_id: `file_${index}`, relative_path })) }
      const body = new FormData()
      body.append('metadata', JSON.stringify(metadata))
      files.forEach((file, index) => body.append(`file_${index}`, file))
      const response = await fetch(repeat && baseline ? `/api/v1/scans/${baseline.scan_id}/rescans` : '/api/v1/scans', { method: 'POST', signal: AbortSignal.timeout(75_000),
        headers: { 'X-CSRF-Token': csrf_token, 'Idempotency-Key': retryKey.current, ...(mode !== 'codebase' ? { 'Content-Type': 'application/json' } : {}) },
        body: mode === 'repository' ? JSON.stringify({ mode, repository_url: repository, ref: ref || null, authorization_confirmed: true, allow_external_ai: sharing }) : mode === 'website' ? JSON.stringify({ mode, target_url: website, authorization_confirmed: true, allow_external_ai: sharing }) : body })
      if (!response.ok) {
        const result: components['schemas']['ErrorResponse'] = await response.json()
        throw new Error(`Submission rejected (${result.error.code}). Check permission, paths, mapping and limits.`)
      }
      const accepted: Scan = await response.json()
      if (requestGeneration !== generation.current) return
      currentIdentity.current = accepted.scan_id
      setScan(accepted)
      setInputOpen(false)
      setRepeat(false); setPermission(false); setSharing(false); setComparison(null)
      if (!repeat) setBaseline(null)
      setDeletion(null)
      retryKey.current = null
    } catch (failure) {
      setError(failure instanceof Error ? failure.message : 'Connection interrupted. Submission status is unknown.')
    } finally { pendingAdmission.current = false; setPending(false) }
  }
  return <section className="workspace" aria-labelledby="source-title">
    <details className="panel intake-panel" open={!scan || repeat || inputOpen} onToggle={event => { if (scan && !repeat) setInputOpen(event.currentTarget.open) }}>
    <summary className="intake-summary"><div><p className="eyebrow">{scan && !repeat ? 'REVIEW INPUT' : 'NEW REVIEW'}</p><h2 id="source-title" tabIndex={-1}>{repeat ? 'Recheck corrected input.' : scan ? 'Start another review' : 'What would you like to review?'}</h2></div><span className="disclosure-hint">{scan && !repeat ? 'Expand to submit' : 'Choose your input'}</span></summary>
    {repeat && <p role="status">Same-mode repeat of {baseline?.scan_id}. Baseline evidence remains below. <button type="button" disabled={pending} onClick={newSubmission}>New submission</button></p>}
    <form onSubmit={submit} className="intake-form">
      <div className="source-controls"><label>Submission mode<select value={mode} disabled={pending || repeat} onChange={event => { changed(); setMode(event.target.value as 'codebase' | 'repository' | 'website') }}><option value="codebase">Codebase</option><option value="repository">Repository</option><option value="website">Website URL</option></select></label><span className="mode-description">{mode === 'codebase' ? 'Keep your original file structure.' : mode === 'repository' ? 'Review one exact repository snapshot.' : 'Inspect captured responses, never private backend source.'}</span></div>
      <p className="limit-strip">{mode === 'website' ? '200 requests · 50 pages · 50 linked assets · 20 MiB responses' : '25 MiB total · 5,000 files · 2 MiB per file · path depth 20 · 240 UTF-8 bytes per path'}</p>
      <div className="submission-layout"><div className="source-fields">
      {mode === 'website' ? <>
        <div className="repository-heading"><span className="source-symbol" aria-hidden="true">↗</span><h3>Review an authorized website</h3><p>Bounded public responses. Passive ZAP checks and browser-visible credential candidates.</p></div>
        <label>Website URL<input type="url" required value={website} placeholder="https://your-authorized-site.example" disabled={pending} onChange={event => { changed(); setWebsite(event.target.value) }} /></label>
        <p className="field-help">Public HTTP/HTTPS only, standard ports, exact-origin GET requests. No login, active attacks, browser JavaScript or cross-origin crawling.</p>
        <p className="field-help">50 pages · 50 linked text assets · 200 requests · 20 MiB responses · 2 MiB/body. Runtime-loaded and unvisited resources remain outside the observed scope.</p>
      </> : mode === 'repository' ? <>
        <div className="repository-heading"><span className="source-symbol" aria-hidden="true">⌥</span><h3>Connect a public repository</h3><p>Choose a branch, tag or commit. We’ll record exactly what was reviewed.</p></div>
        <label>Public GitHub repository URL<input type="url" required value={repository} placeholder="https://github.com/owner/repository" disabled={pending} onChange={event => { changed(); setRepository(event.target.value) }} /></label>
        <label>Branch, tag, or commit (optional)<input value={ref} maxLength={256} disabled={pending} onChange={event => { changed(); setRef(event.target.value) }} /></label>
      <p className="field-help">Public repositories only. One resolved commit; no private credentials, history, submodules, LFS downloads, hooks or builds.</p>
      </> : <>
      <div className="directory-picker"><span className="source-symbol" aria-hidden="true"><svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5"><path d="M3 7V5a1 1 0 0 1 1-1h5l2 3h9a1 1 0 0 1 1 1v10a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V7Z" /><path d="M3 9h18M12 12v5m-2-2 2 2 2-2" /></svg></span><h3>A source tree, ready for a closer look.</h3><p>Select your project folder. We’ll preserve its paths<br className="desktop-break" /> and make the accepted review scope explicit.</p><label>Choose directory<input type="file" multiple {...{ webkitdirectory: '' }} onChange={event => select(event.currentTarget, true)} disabled={pending} /></label><span className="field-help">Your app is never installed, built or executed.</span></div>
      <details className="mapped-picker" open><summary>Choose individual files instead (shows all .ts, .js files)</summary><label>Choose files<input type="file" multiple onChange={event => select(event.currentTarget, false)} disabled={pending} /></label><p className="field-help">Pick one or more source files directly. File names are automatically mapped.</p></details>
      {mapped && <label>Relative paths, one per selected file<textarea value={paths} onChange={event => { if (event.target.value !== paths) changed(); setPaths(event.target.value) }} disabled={pending} /></label>}
      {files.length > 0 && <details className="selected-files"><summary>{files.length} files selected · {(files.reduce((total, file) => total + file.size, 0) / 1024).toFixed(1)} KiB</summary><ol>{files.map((file, index) => <li key={index}>{mapped ? file.name : file.webkitRelativePath} · {file.size} bytes</li>)}</ol></details>}
      </>}
      </div><aside className="submission-context" aria-label="Review scope"><span className="context-icon" aria-hidden="true">{'{ }'}</span><h3>Know what you’re reviewing.</h3><p>{mode === 'website' ? 'Passive response and header checks, plus private-credential candidates in observed browser-visible text.' : 'Selected checks for credentials, unsafe input, insecure configuration and access-check candidates.'}</p><div className="scope-facts"><div><span>{mode === 'website' ? 'Total response budget' : 'Maximum source size'}</span><strong>{mode === 'website' ? '20 MiB' : '25 MiB'}</strong></div><div><span>{mode === 'website' ? 'Maximum GET requests' : 'Files per review'}</span><strong>{mode === 'website' ? '200' : '5,000'}</strong></div><div><span>{mode === 'website' ? 'Maximum response body' : 'Maximum file size'}</span><strong>2 MiB</strong></div></div><p className="field-help">{mode === 'website' ? '50 pages · 50 linked text assets · exact origin only' : 'Path depth 20 · 240 UTF-8 bytes per path'}</p><div className="privacy-note"><strong>Evidence without exposed values</strong><p>Reports omit source literals. Exposed credentials still need revocation or rotation.</p></div></aside></div>
      <div className="consent-area"><label className="checkbox-row"><input type="checkbox" checked={permission} onChange={event => { changed(); setPermission(event.target.checked) }} disabled={pending} required /><span>{mode === 'website' ? 'I have permission to review this website.' : 'I have permission to review this source.'}<small>{mode === 'website' ? 'Only assess sites you own or are authorized to review.' : 'Only submit code you own or are authorized to assess.'}</small></span></label>
      <label className="checkbox-row secondary-consent"><input type="checkbox" checked={sharing} onChange={event => { changed(); setSharing(event.target.checked) }} disabled={pending} /><span>Use AI explanations (optional).<small>Shares sanitized findings with an external AI service when configured. Off by default; repair guidance works without it.</small></span></label></div>
      <div className="submit-row"><p>{pending ? 'Preparing your submission. Keep this page open.' : 'Select your input and confirm permission to begin.'}</p><button className="primary-button" type="submit" disabled={pending || !permission || (mode === 'codebase' ? files.length === 0 : mode === 'repository' ? !repository : !website)}>{pending ? 'Submitting…' : mode === 'repository' ? 'Review repository' : mode === 'website' ? 'Review website' : 'Submit source tree'}</button></div>
    </form>
    <details className="reconnect-panel"><summary>Reconnect to an existing scan</summary><p>Use the same browser session and Scan ID after refresh. Reconnecting does not submit new work. Lost cookies cannot be recovered.</p>
      <label>Scan ID<input value={reconnectId} maxLength={32} onChange={event => setReconnectId(event.target.value)} /></label><button type="button" disabled={pending} onClick={() => reconnect()}>Reconnect</button></details>
    </details>
    {error && <p role="alert" className="error-banner">{error}</p>}
    {baseline && baseline.scan_id !== scan?.scan_id && <div className="panel results-panel"><h3>Before - preserved baseline</h3><Report scan={baseline} /></div>}
    {comparison && baseline && scan && comparison.baseline_id === baseline.scan_id && comparison.new_id === scan.scan_id && <div className="panel results-panel"><Comparison key={`${baseline.scan_id}:${scan.scan_id}`} baseline={baseline} current={scan} result={comparison} /></div>}
    {comparisonError && <p role="alert">{comparisonError} <button onClick={() => setComparisonRetry(value => value + 1)}>Retry comparison</button><button disabled={pending} onClick={newSubmission}>New submission</button></p>}
    {scan && <div className="panel results-panel"><div className="results-heading"><div><p className="eyebrow">YOUR REVIEW</p><h3 ref={resultHeading} tabIndex={-1} role="status">{{ queued: 'Review queued', running: 'Review in progress', complete: 'Review complete', partial: 'Review complete with limitations', failed: 'Review could not complete' }[scan.status]}</h3></div><span className="scope-tag">{scan.mode === 'repository' ? 'REPOSITORY' : scan.mode === 'website' ? 'WEBSITE' : 'CODEBASE'}</span></div>
      <Report scan={scan} key={scan.scan_id} />
      {['complete', 'partial', 'failed'].includes(scan.status) && !repeat && <button className="primary-button" type="button" disabled={pending} onClick={startRepeat}>Rescan corrected input</button>}
      {error && <button type="button" disabled={pending} onClick={() => reconnect(scan.scan_id)}>Reconnect this scan</button>}
      <div className="report-footer"><p>Scan ID: <code>{scan.scan_id}</code></p><button className="danger-button" type="button" onClick={() => confirmation.current?.showModal()}>Delete scan</button></div></div>}
    {!scan && !deletion && <div className="report-placeholder"><span className="placeholder-mark" aria-hidden="true">[ / ]</span><div><h3>Your evidence will appear here.</h3><p>Submit authorized source to inspect real findings and copy a repair prompt.</p></div><span className="scope-tag">AWAITING SOURCE</span></div>}
    {deletion && <p role="status">Cleanup: {deletion.status}{deletion.status === 'failed' ? ' · Cleanup is incomplete; the coordinator will retry.' : ''}</p>}
    <dialog ref={confirmation}><h3>Delete this scan and source?</h3><p>Access is revoked immediately. Cleanup status remains visible.</p><button autoFocus onClick={() => confirmation.current?.close()}>Cancel</button><button onClick={remove}>Delete scan</button></dialog>
  </section>
}

