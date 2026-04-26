import { useState, useRef, useEffect, type FormEvent } from 'react'
import { startAddDocument, pollJobResult, fetchCollections, deleteParty } from '../api/client'
import type { CollectionStats } from '../api/client'
import { PARTIES } from '../data/politicians'

type Phase = 'form' | 'loading' | 'success' | 'error'

function CollectionsTable() {
  const [collections, setCollections] = useState<CollectionStats[] | null>(null)
  const [loading, setLoading]         = useState(false)
  const [deleting, setDeleting]       = useState<string | null>(null)
  const [error, setError]             = useState('')

  useEffect(() => { load() }, [])

  async function load() {
    setLoading(true)
    setError('')
    try {
      setCollections(await fetchCollections())
    } catch {
      setError('Nepodařilo se načíst kolekce.')
    } finally {
      setLoading(false)
    }
  }

  async function handleDelete(collection: string, party: string) {
    const key = `${collection}::${party}`
    setDeleting(key)
    try {
      await deleteParty(collection, party)
      await load()
    } catch {
      setError('Mazání selhalo.')
    } finally {
      setDeleting(null)
    }
  }

  const totalChunks = collections?.flatMap(c => c.parties).reduce((s, p) => s + p.chunk_count, 0) ?? 0

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
        <span style={{ color: 'var(--text-muted)', fontSize: '13px' }}>
          {loading ? 'Načítám…' : collections ? `${collections.length} kolekcí · ${totalChunks} chunků` : ''}
        </span>
        <button className="btn btn-ghost" style={{ fontSize: '13px', padding: '4px 12px' }} onClick={load} disabled={loading}>
          ↻ Obnovit
        </button>
      </div>

      {error && <p style={{ color: 'var(--red)', marginBottom: '12px' }}>{error}</p>}

      {loading && <p className="section-hint">Načítám…</p>}

      {!loading && collections !== null && collections.length === 0 && (
        <p className="section-hint">Databáze je prázdná.</p>
      )}

      {!loading && collections !== null && collections.length > 0 && collections.map(col => (
        <div key={col.collection_name} style={{ marginBottom: '20px' }}>
          <p style={{ fontWeight: 600, color: 'var(--accent)', marginBottom: '8px', fontSize: '14px' }}>
            📁 {col.collection_name}
          </p>
          {col.parties.length === 0 ? (
            <p className="section-hint" style={{ paddingLeft: '16px' }}>Žádné záznamy.</p>
          ) : (
            <table className="db-table">
              <thead>
                <tr>
                  <th>Strana</th>
                  <th style={{ textAlign: 'right' }}>Počet Chunků</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {col.parties.map(p => {
                  const key = `${col.collection_name}::${p.party}`
                  return (
                    <tr key={p.party}>
                      <td>{p.party}</td>
                      <td style={{ textAlign: 'right', fontVariantNumeric: 'tabular-nums' }}>{p.chunk_count}</td>
                      <td style={{ textAlign: 'right' }}>
                        <button
                          className="btn-delete"
                          disabled={deleting === key}
                          onClick={() => handleDelete(col.collection_name, p.party)}
                        >
                          {deleting === key ? '…' : '✕'}
                        </button>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          )}
        </div>
      ))}
    </div>
  )
}

export default function DocumentsPage() {
  const [phase, setPhase]     = useState<Phase>('form')
  const [url, setUrl]         = useState('')
  const [name, setName]       = useState('')
  const [collection, setCol]  = useState('test_collection')
  const [party, setParty]     = useState('')
  const [customParty, setCustomParty] = useState('')
  const [year, setYear]       = useState(2025)
  const [elapsed, setElapsed] = useState(0)
  const [errorMsg, setError]  = useState('')

  const pollRef    = useRef<ReturnType<typeof setInterval> | null>(null)
  const timerRef   = useRef<ReturnType<typeof setInterval> | null>(null)

  useEffect(() => {
    return () => {
      if (pollRef.current)  clearInterval(pollRef.current)
      if (timerRef.current) clearInterval(timerRef.current)
    }
  }, [])

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    if (!url.trim() || !name.trim()) return

    setPhase('loading')
    setElapsed(0)
    timerRef.current = setInterval(() => setElapsed(s => s + 1), 1000)

    try {
      const resolvedParty = party === '__custom__' ? (customParty.trim() || null) : (party || null)
      const jobId = await startAddDocument(url, name, collection, resolvedParty, year)

      pollRef.current = setInterval(async () => {
        try {
          const data = await pollJobResult(jobId)
          if (data.status === 'COMPLETED') {
            clearInterval(pollRef.current!)
            clearInterval(timerRef.current!)
            setPhase('success')
          } else if (data.status === 'FAILED') {
            clearInterval(pollRef.current!)
            clearInterval(timerRef.current!)
            setError(data.error ?? 'Neznámá chyba.')
            setPhase('error')
          }
        } catch { /* network hiccup */ }
      }, 3000)
    } catch (err) {
      clearInterval(timerRef.current!)
      setError((err as Error).message)
      setPhase('error')
    }
  }

  function handleAddAnother() {
    setUrl('')
    setName('')
    setPhase('form')
  }

  const [dbOpen, setDbOpen] = useState(false)

  return (
    <>
    <div className="card" style={{ marginTop: '24px' }}>
      <div className="card-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <span>📄 Přidat dokument do Milvus</span>
        <button className="btn btn-ghost" style={{ fontSize: '13px', padding: '4px 12px' }} onClick={() => setDbOpen(true)}>
          🗄️ Všechny soubory
        </button>
      </div>
      <div className="card-body">

        {phase === 'form' && (
          <form onSubmit={handleSubmit}>
            <p className="section-hint">
              Vložte URL k PDF souboru (stranický program, výroční zpráva apod.).
              Dokument bude automaticky rozsekaný na chunky a uložen do vektorové databáze.
            </p>

            <div className="form-group" style={{ marginTop: '16px' }}>
              <label htmlFor="doc-url">URL dokumentu (PDF)</label>
              <input
                id="doc-url"
                type="text"
                value={url}
                onChange={e => setUrl(e.target.value)}
                placeholder="https://example.com/program-strany.pdf"
                required
              />
            </div>

            <div className="form-row" style={{ marginTop: '16px' }}>
              <div className="form-group">
                <label htmlFor="doc-name">Název dokumentu</label>
                <input
                  id="doc-name"
                  type="text"
                  value={name}
                  onChange={e => setName(e.target.value)}
                  placeholder="Volební program 2025"
                  required
                />
              </div>
              <div className="form-group">
                <label htmlFor="doc-collection">Kolekce</label>
                <input
                  id="doc-collection"
                  type="text"
                  value={collection}
                  onChange={e => setCol(e.target.value)}
                />
              </div>
              <div className="form-group form-group-narrow">
                <label htmlFor="doc-year">Rok</label>
                <input
                  id="doc-year"
                  type="number"
                  value={year}
                  onChange={e => setYear(Number(e.target.value))}
                  min={2000}
                  max={2100}
                />
              </div>
            </div>

            <div className="form-group" style={{ marginTop: '16px' }}>
              <label htmlFor="doc-party">Strana</label>
              <select
                id="doc-party"
                value={party}
                onChange={e => setParty(e.target.value)}
                className="select-input"
              >
                <option value="">Neurčeno</option>
                {PARTIES.map(p => <option key={p} value={p}>{p}</option>)}
                <option value="__custom__">Jiná strana…</option>
              </select>
              {party === '__custom__' && (
                <input
                  type="text"
                  value={customParty}
                  onChange={e => setCustomParty(e.target.value)}
                  placeholder="Název strany"
                  style={{ marginTop: '8px' }}
                />
              )}
            </div>

            <div className="form-actions">
              <button className="btn btn-primary" type="submit">
                📤 Nahrát dokument
              </button>
            </div>
          </form>
        )}

        {phase === 'loading' && (
          <div className="doc-status">
            <div className="spinner" />
            <p className="loading-title">Nahrávám dokument…</p>
            <p className="loading-sub">
              Dokument se stahuje, rozděluje na části a ukládá do vektorové databáze.
              <br />Tento proces může trvat i několik minut u větších souborů.
            </p>
            <p className="elapsed">⏱ {elapsed} s</p>
          </div>
        )}

        {phase === 'success' && (
          <div className="doc-status">
            <div className="success-icon">✅</div>
            <p className="loading-title" style={{ color: 'var(--green)' }}>Dokument úspěšně nahrán!</p>
            <p className="loading-sub">
              Dokument <strong>"{name}"</strong> byl rozsekaný a uložen do kolekce <strong>{collection}</strong>.
            </p>
            <div style={{ marginTop: '24px', display: 'flex', gap: '12px', justifyContent: 'center' }}>
              <button className="btn btn-primary" onClick={handleAddAnother}>
                📤 Přidat další dokument
              </button>
            </div>
          </div>
        )}

        {phase === 'error' && (
          <div className="doc-status">
            <div className="error-icon">❌</div>
            <p className="loading-title" style={{ color: 'var(--red)' }}>Nahrávání selhalo</p>
            <p className="loading-sub">{errorMsg}</p>
            <div style={{ marginTop: '24px' }}>
              <button className="btn btn-ghost" onClick={() => setPhase('form')}>
                ↩ Zkusit znovu
              </button>
            </div>
          </div>
        )}

      </div>
    </div>

    {dbOpen && (
      <div className="modal-overlay" onClick={() => setDbOpen(false)}>
        <div className="modal modal-wide" onClick={e => e.stopPropagation()}>
          <div className="modal-header">
            <span>🗄️ Obsah databáze</span>
            <button className="modal-close" onClick={() => setDbOpen(false)}>✕</button>
          </div>
          <div className="modal-body">
            <CollectionsTable />
          </div>
        </div>
      </div>
    )}
    </>
  )
}
