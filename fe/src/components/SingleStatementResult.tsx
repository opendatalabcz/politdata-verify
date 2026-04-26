import type { ClassifiedStatement } from '../types'

interface Props {
  statement: ClassifiedStatement
  query: string
  onReset: () => void
}

function exportJson(statement: ClassifiedStatement, query: string) {
  const payload = { query, ...statement }
  const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `politdata-verify-vyrok-${new Date().toISOString().slice(0, 10)}.json`
  a.click()
  URL.revokeObjectURL(url)
}

const VERDICT_CONFIG = {
  SUPPORTED:    { cls: 'supported',    icon: '✅', label: 'Podpořeno programem',   desc: 'Tento výrok je v souladu se stranickým programem.' },
  CONTRADICTED: { cls: 'contradicted', icon: '❌', label: 'Odporuje programu',     desc: 'Tento výrok je v rozporu se stranickým programem.' },
  INSUFFICIENT: { cls: 'insufficient', icon: '❓', label: 'Nedostatek dat',        desc: 'Program neobsahuje dostatek informací k ověření tohoto výroku.' },
} as const

export default function SingleStatementResult({ statement, query, onReset }: Props) {
  const cfg = VERDICT_CONFIG[statement.verdict]
  const conf = Math.round(statement.confidence * 100)

  return (
    <div className="single-result">
      {/* Verdict banner */}
      <div className={`verdict-banner ${cfg.cls}`}>
        <span className="verdict-banner-icon">{cfg.icon}</span>
        <div>
          <div className="verdict-banner-label">{cfg.label}</div>
          <div className="verdict-banner-desc">{cfg.desc}</div>
        </div>
        <div className="verdict-conf">{conf}%</div>
      </div>

      {/* Original statement */}
      <div className="result-section">
        <p className="detail-label">Ověřovaný výrok</p>
        <p className="result-query">"{query}"</p>
      </div>

      {/* Rationale */}
      {statement.rationale && (
        <div className="result-section">
          <p className="detail-label">Zdůvodnění</p>
          <p className="rationale">{statement.rationale}</p>
        </div>
      )}

      {/* Evidence */}
      {statement.evidence.length > 0 && (
        <div className="result-section">
          <p className="detail-label">Důkazy z programu</p>
          {statement.evidence.map((e, i) => (
            <div key={i} className="evidence-item">
              <p className="evidence-quote">"{e.quote}"</p>
              <p className="evidence-citation">{e.citation}</p>
            </div>
          ))}
        </div>
      )}

      <div className="reset-row">
        <button className="btn btn-ghost" onClick={onReset}>↩ Ověřit další výrok</button>
        <button className="btn btn-ghost" onClick={() => exportJson(statement, query)}>⬇ Export JSON</button>
      </div>
    </div>
  )
}
