import { useState, useRef, useEffect, type FormEvent } from 'react'
import { startAddDocument, pollJobResult, fetchCollections, deleteParty, deleteCollection } from '../api/client'
import type { CollectionStats } from '../api/client'
import { PARTIES } from '../data/politicians'

type Phase = 'form' | 'loading' | 'success' | 'error'

function CollectionsTable({ canDelete, registerRefresh }: { canDelete: boolean; registerRefresh?: (fn: () => void) => void }) {
  const [collections, setCollections] = useState<CollectionStats[] | null>(null)
  const [loading, setLoading]         = useState(false)
  const [deleting, setDeleting]       = useState<string | null>(null)
  const [deletingCol, setDeletingCol] = useState<string | null>(null)
  const [error, setError]             = useState('')

  useEffect(() => { load() }, [])
  useEffect(() => { registerRefresh?.(load) }, [])

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

  async function handleDeleteCollection(collection: string) {
    if (!confirm(`Opravdu smazat celou kolekci "${collection}"? Tato akce je nevratná.`)) return
    setDeletingCol(collection)
    try {
      await deleteCollection(collection)
      await load()
    } catch {
      setError('Mazání kolekce selhalo.')
    } finally {
      setDeletingCol(null)
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
      {collections && (
        <p style={{ color: 'var(--text-muted)', fontSize: '13px', marginBottom: '16px' }}>
          {loading ? 'Načítám…' : `${collections.length} kolekcí · ${totalChunks} chunků`}
        </p>
      )}

      {error && <p style={{ color: 'var(--red)', marginBottom: '12px' }}>{error}</p>}

      {loading && <p className="section-hint">Načítám…</p>}

      {!loading && collections !== null && collections.length === 0 && (
        <p className="section-hint">Databáze je prázdná.</p>
      )}

      {!loading && collections !== null && collections.length > 0 && collections.map(col => (
        <div key={col.collection_name} style={{ marginBottom: '20px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
            <p style={{ fontWeight: 600, color: 'var(--accent)', fontSize: '14px', margin: 0 }}>
              📁 {col.collection_name}
            </p>
            {canDelete && (
              <button
                className="btn-delete"
                disabled={deletingCol === col.collection_name}
                onClick={() => handleDeleteCollection(col.collection_name)}
                title="Smazat celou kolekci"
              >
                {deletingCol === col.collection_name ? '…' : 'Smazat kolekci'}
              </button>
            )}
          </div>
          {col.parties.length === 0 ? (
            <p className="section-hint" style={{ paddingLeft: '16px' }}>Žádné záznamy.</p>
          ) : (
            <table className="db-table" style={{ tableLayout: 'fixed', width: '100%' }}>
              <colgroup>
                <col style={{ width: '22%' }} />
                <col />
                <col style={{ width: '16%' }} />
                {canDelete && <col style={{ width: '80px' }} />}
              </colgroup>
              <thead>
                <tr>
                  <th>Strana</th>
                  <th>Dokument</th>
                  <th style={{ textAlign: 'right' }}>Rozsah</th>
                  {canDelete && <th></th>}
                </tr>
              </thead>
              <tbody>
                {col.parties.map(p => {
                  const key = `${col.collection_name}::${p.party}`
                  return (
                    <tr key={p.party}>
                      <td>{p.party}</td>
                      <td style={{ color: 'var(--text-muted)', fontSize: '13px' }}>
                        {p.doc_names?.join(', ') || '—'}
                      </td>
                      <td style={{ textAlign: 'right', fontVariantNumeric: 'tabular-nums' }}>
                        {p.total_chars ? `${p.total_chars.toLocaleString('cs-CZ')} znaků` : `${p.chunk_count} částí`}
                      </td>
                      {canDelete && (
                        <td style={{ textAlign: 'right' }}>
                          <button
                            className="btn-delete"
                            disabled={deleting === key}
                            onClick={() => handleDelete(col.collection_name, p.party)}
                          >
                            {deleting === key ? '…' : '✕'}
                          </button>
                        </td>
                      )}
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

export default function DocumentsPage({ adminUnlocked }: { adminUnlocked: boolean }) {
  const [phase, setPhase]     = useState<Phase>('form')
  const [url, setUrl]         = useState('')
  const [name, setName]       = useState('')
  const [collections, setCollections] = useState<string[]>([])
  const [collection, setCol]  = useState('')
  const [customCol, setCustomCol] = useState('')
  const [party, setParty]     = useState('')
  const [customParty, setCustomParty] = useState('')
  const [year, setYear]       = useState(2025)

  useEffect(() => {
    fetchCollections()
      .then(cols => {
        const names = cols.map(c => c.collection_name)
        setCollections(names)
        if (names.length > 0) setCol(names[0])
      })
      .catch(() => {})
  }, [])
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
      const resolvedCol = collection === '__new__' ? customCol.trim() : collection
      const jobId = await startAddDocument(url, name, resolvedCol, resolvedParty, year)

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

  const refreshRef = useRef<(() => void) | null>(null)

  return (
    <>
    <div className="card" style={{ marginTop: '24px' }}>
      <div className="card-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <span>🗄️ Obsah znalostní báze</span>
        <button className="btn btn-ghost" style={{ fontSize: '13px', padding: '4px 12px' }} onClick={() => refreshRef.current?.()}>
          ↻ Obnovit
        </button>
      </div>
      <div className="card-body">
        <CollectionsTable canDelete={adminUnlocked} registerRefresh={fn => { refreshRef.current = fn }} />
      </div>
    </div>

    <div className="card" style={{ marginTop: '16px' }}>
      <div className="card-header">📄 Přidat dokument do Milvus</div>
      <div className="card-body">

        {!adminUnlocked && (
          <p className="section-hint" style={{ color: 'var(--text-muted)' }}>
            🔒 Přidávání dokumentů vyžaduje přihlášení administrátora.
          </p>
        )}

        {adminUnlocked && phase === 'form' && (
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
                <select
                  id="doc-collection"
                  value={collection}
                  onChange={e => setCol(e.target.value)}
                  className="select-input"
                >
                  {collections.map(c => <option key={c} value={c}>{c}</option>)}
                  <option value="__new__">+ Nová kolekce…</option>
                </select>
                {collection === '__new__' && (
                  <input
                    type="text"
                    value={customCol}
                    onChange={e => setCustomCol(e.target.value)}
                    placeholder="Název nové kolekce"
                    style={{ marginTop: '8px' }}
                    required
                  />
                )}
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

        {adminUnlocked && phase === 'loading' && (
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

        {adminUnlocked && phase === 'success' && (
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

        {adminUnlocked && phase === 'error' && (
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
    </>
  )
}
