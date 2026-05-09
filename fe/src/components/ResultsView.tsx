import { useState } from 'react'
import type { StatsResult, SpeakerStats } from '../types'
import SpeakerCard from './SpeakerCard'

function exportJson(stats: StatsResult) {
  const blob = new Blob([JSON.stringify(stats, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `politdata-verify-${new Date().toISOString().slice(0, 10)}.json`
  a.click()
  URL.revokeObjectURL(url)
}

type Filter = 'all' | 'supported' | 'contradicted' | 'insufficient'

interface Props {
  stats: StatsResult
  onReset: () => void
}

function filterSpeaker(speaker: SpeakerStats, filter: Filter): SpeakerStats | null {
  if (filter === 'all') return speaker
  const key = filter as 'supported' | 'contradicted' | 'insufficient'
  if (speaker[key].length === 0) return null
  return { ...speaker, total_statements: speaker[key].length }
}

export default function ResultsView({ stats, onReset }: Props) {
  const [filter, setFilter] = useState<Filter>('all')

  const totalSupported    = stats.speakers_stats.reduce((n, s) => n + s.supported.length, 0)
  const totalContradicted = stats.speakers_stats.reduce((n, s) => n + s.contradicted.length, 0)
  const totalInsufficient = stats.speakers_stats.reduce((n, s) => n + s.insufficient.length, 0)

  const filtered = stats.speakers_stats
    .map(s => filterSpeaker(s, filter))
    .filter(Boolean) as SpeakerStats[]

  const FILTERS: { key: Filter; label: string; count: number }[] = [
    { key: 'all',          label: 'Vše',            count: stats.total_statements },
    { key: 'supported',    label: '✅ Podpořeno',   count: totalSupported },
    { key: 'contradicted', label: '❌ Odporuje',    count: totalContradicted },
    { key: 'insufficient', label: '❓ Nedostatek',  count: totalInsufficient },
  ]

  return (
    <div>
      <div className="results-summary">
        <div className="summary-stat">
          <div className="summary-num">{stats.total_speakers}</div>
          <div className="summary-lbl">Řečníků</div>
        </div>
        <div className="summary-stat">
          <div className="summary-num">{stats.total_statements}</div>
          <div className="summary-lbl">Výroků celkem</div>
        </div>
        <div className="summary-stat" style={{ color: '#86efac' }}>
          <div className="summary-num">{totalSupported}</div>
          <div className="summary-lbl">✅ Podpořeno</div>
        </div>
        <div className="summary-stat" style={{ color: '#fca5a5' }}>
          <div className="summary-num">{totalContradicted}</div>
          <div className="summary-lbl">❌ Odporuje</div>
        </div>
        <div className="summary-stat" style={{ color: '#e2e8f0' }}>
          <div className="summary-num">{totalInsufficient}</div>
          <div className="summary-lbl">❓ Nedostatek dat</div>
        </div>
      </div>

      <div className="results-toolbar">
        <h2 className="section-title" style={{ margin: 0 }}>👥 Výsledky po řečnících</h2>
        <div className="verdict-filter">
          {FILTERS.map(f => (
            <button
              key={f.key}
              className={`filter-btn${filter === f.key ? ' active' : ''}`}
              onClick={() => setFilter(f.key)}
            >
              {f.label}
              <span className="filter-count">{f.count}</span>
            </button>
          ))}
        </div>
      </div>

      {filtered.length === 0 ? (
        <div className="filter-empty">Žádné výroky odpovídající filtru.</div>
      ) : (
        <div className="results-grid">
          {filtered.map((speaker, i) => (
            <SpeakerCard
              key={`${filter}-${speaker.speaker.name}-${speaker.speaker.surname}`}
              speaker={speaker}
              colorIndex={i}
              filterVerdict={filter === 'all' ? undefined : filter}
            />
          ))}
        </div>
      )}

      <div className="reset-row">
        <button className="btn btn-ghost" onClick={onReset}>↩ Nová analýza</button>
        <button className="btn btn-ghost" onClick={() => exportJson(stats)}>⬇ Export JSON</button>
      </div>
    </div>
  )
}
