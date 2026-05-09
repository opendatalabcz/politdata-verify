import { useState, useEffect, type FormEvent } from 'react'
import type { Speaker } from '../types'
import { fetchCollections } from '../api/client'

interface Props {
  speakers: Speaker[]
  onOpenSpeakers: () => void
  onSubmit: (text: string, collection: string, year: number, mode: 'sync' | 'async') => void
  error: string | null
}

export default function InputForm({ speakers, onOpenSpeakers, onSubmit, error }: Props) {
  const [text, setText] = useState('')
  const [collections, setCollections] = useState<string[]>([])
  const [collection, setCollection] = useState('')
  const [year, setYear] = useState(2025)
  const [mode, setMode] = useState<'sync' | 'async'>('async')
  const [submitting, setSubmitting] = useState(false)

  useEffect(() => {
    fetchCollections()
      .then(cols => {
        const names = cols.map(c => c.collection_name)
        setCollections(names)
        if (names.length > 0) setCollection(names[0])
      })
      .catch(() => {})
  }, [])

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    if (!text.trim()) return
    setSubmitting(true)
    await onSubmit(text, collection, year, mode)
    setSubmitting(false)
  }

  return (
    <form onSubmit={handleSubmit}>
      <div className="form-group">
        <label htmlFor="text">Vložte text stenozáznamu</label>
        <textarea
          id="text"
          value={text}
          onChange={e => setText(e.target.value)}
          rows={10}
          maxLength={5000}
          placeholder={
            'Vložte text parlamentní debaty nebo jiného politického projevu…\n\n' +
            'Příklad:\n' +
            'Poslankyně Olga Richterová: Děkuji. Já se ptám, kolik lidí vypadne z toho systému podpory…\n' +
            'Ministr práce Aleš Juchelka: Samozřejmě, tato vládní koalice myslí na mladé rodiny…'
          }
        />
        <div className={`char-counter${text.length >= 5000 ? ' char-counter-limit' : text.length > 4000 ? ' char-counter-warn' : ''}`}>
          {text.length} / 5 000 znaků
        </div>
      </div>

      <div className="form-row form-row-flush">
        <div className="form-group">
          <label htmlFor="collection">Kolekce</label>
          <select
            id="collection"
            value={collection}
            onChange={e => setCollection(e.target.value)}
            className="select-input"
            disabled={collections.length === 0}
          >
            {collections.length === 0
              ? <option>Načítám…</option>
              : collections.map(c => <option key={c} value={c}>{c}</option>)
            }
          </select>
        </div>
        <div className="form-group form-group-narrow">
          <label htmlFor="year">Rok</label>
          <input
            id="year"
            type="number"
            value={year}
            onChange={e => setYear(Number(e.target.value))}
            min={2000}
            max={2100}
          />
        </div>
      </div>

      <div className="speaker-row">
        <button type="button" className="btn btn-ghost btn-sm" onClick={onOpenSpeakers}>
          👤 Přidat řečníky {speakers.length > 0 && `(${speakers.length})`}
        </button>
        {speakers.length > 0 && (
          <div className="speaker-tags">
            {speakers.map(s => (
              <span key={`${s.name}-${s.surname}`} className="speaker-tag">
                {s.name} {s.surname} · {s.party}
              </span>
            ))}
          </div>
        )}
      </div>

      {error && <div className="error-box"><strong>❌ Chyba:</strong> {error}</div>}

      <div className="form-actions">
        <button className="btn btn-primary" type="submit" disabled={submitting}>
          🔍 Analyzovat debatu
        </button>
        <div className="mode-toggle-group">
          <span className="mode-toggle-label">Režim zpracování</span>
          <div className="mode-toggle mode-toggle-inline">
            <button
              type="button"
              className={`mode-btn${mode === 'async' ? ' active' : ''}`}
              onClick={() => setMode('async')}
              title="Výroky zpracovány paralelně — rychlejší, doporučeno"
            >⚡ Paralelní</button>
            <button
              type="button"
              className={`mode-btn${mode === 'sync' ? ' active' : ''}`}
              onClick={() => setMode('sync')}
              title="Výroky zpracovány postupně jeden po druhém"
            >🐢 Postupný</button>
          </div>
          <span className="mode-toggle-desc">
            {mode === 'async' ? 'Výroky se zpracují současně — rychlejší.' : 'Výroky se zpracují jeden po druhém.'}
          </span>
        </div>
        <span className="hint">Analýza může trvat 30–120 sekund.</span>
      </div>
    </form>
  )
}
