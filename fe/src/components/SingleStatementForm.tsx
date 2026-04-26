import { useState, useEffect, type FormEvent } from 'react'
import { fetchCollections } from '../api/client'

interface Props {
  onSubmit: (query: string, collection: string, party: string | null, year: number) => void
  error: string | null
}

export default function SingleStatementForm({ onSubmit, error }: Props) {
  const [query, setQuery] = useState('')
  const [collection, setCollection] = useState('test_collection')
  const [parties, setParties] = useState<string[]>([])
  const [party, setParty] = useState('')
  const [year, setYear] = useState(2025)
  const [submitting, setSubmitting] = useState(false)
  const [loadingParties, setLoadingParties] = useState(false)

  useEffect(() => {
    if (!collection.trim()) return
    setLoadingParties(true)
    setParty('')
    fetchCollections()
      .then(cols => {
        const col = cols.find(c => c.collection_name === collection)
        const names = col ? col.parties.map(p => p.party).sort() : []
        setParties(names)
        if (names.length > 0) setParty(names[0])
      })
      .catch(() => setParties([]))
      .finally(() => setLoadingParties(false))
  }, [collection])

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    if (!query.trim() || !party) return
    setSubmitting(true)
    await onSubmit(query, collection, party, year)
    setSubmitting(false)
  }

  return (
    <form onSubmit={handleSubmit}>
      <div className="form-group">
        <label htmlFor="query">Výrok k ověření</label>
        <textarea
          id="query"
          value={query}
          onChange={e => setQuery(e.target.value)}
          rows={4}
          placeholder="Vložte konkrétní politický výrok, který chcete ověřit vůči stranickému programu…"
        />
      </div>

      <div className="form-row" style={{ marginTop: '16px' }}>
        <div className="form-group">
          <label htmlFor="s-collection">Kolekce (Milvus)</label>
          <input
            id="s-collection"
            type="text"
            value={collection}
            onChange={e => setCollection(e.target.value)}
          />
        </div>
        <div className="form-group">
          <label htmlFor="s-party">Strana</label>
          {loadingParties ? (
            <select id="s-party" className="select-input" disabled>
              <option>Načítám…</option>
            </select>
          ) : parties.length === 0 ? (
            <select id="s-party" className="select-input" disabled>
              <option>Žádné strany v kolekci</option>
            </select>
          ) : (
            <select
              id="s-party"
              value={party}
              onChange={e => setParty(e.target.value)}
              className="select-input"
              required
            >
              {parties.map(p => <option key={p} value={p}>{p}</option>)}
            </select>
          )}
        </div>
        <div className="form-group form-group-narrow">
          <label htmlFor="s-year">Rok</label>
          <input
            id="s-year"
            type="number"
            value={year}
            onChange={e => setYear(Number(e.target.value))}
            min={2000}
            max={2100}
          />
        </div>
      </div>

      {error && <div className="error-box"><strong>❌ Chyba:</strong> {error}</div>}

      <div className="form-actions">
        <button className="btn btn-primary" type="submit" disabled={submitting || parties.length === 0}>
          🔍 Ověřit výrok
        </button>
        <span className="hint">Ověření trvá obvykle 10–30 sekund.</span>
      </div>
    </form>
  )
}
