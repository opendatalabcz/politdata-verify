import { useState } from 'react'
import type { ClassifiedStatementWithContext } from '../types'

interface Props {
  statement: ClassifiedStatementWithContext
}

const VERDICT_CONFIG = {
  SUPPORTED:    { cls: 'supported',    icon: '✅' },
  CONTRADICTED: { cls: 'contradicted', icon: '❌' },
  INSUFFICIENT: { cls: 'insufficient', icon: '❓' },
} as const

export default function StatementItem({ statement }: Props) {
  const [open, setOpen] = useState(false)
  const cfg = VERDICT_CONFIG[statement.verdict]
  const conf = Math.round(statement.confidence * 100)

  const lowConf = statement.confidence <= 0.7

  return (
    <div className={`statement-item${lowConf ? ' low-conf' : ''}`} onClick={() => setOpen(o => !o)}>
      <div className="statement-row">
        <div className={`verdict-icon ${cfg.cls}`}>{cfg.icon}</div>
        <p className="statement-text">{statement.statement}</p>
        <div className="conf-bar-wrap" title={`Confidence: ${conf}%`}>
          <span className="conf-bar-label">{conf}%</span>
          <div className="conf-bar-track">
            <div
              className="conf-bar-fill"
              style={{ width: `${conf}%` }}
            />
          </div>
        </div>
      </div>

      {open && (
        <div className="statement-detail">
          {statement.rationale && (
            <>
              <p className="detail-label">Zdůvodnění</p>
              <p className="rationale">{statement.rationale}</p>
            </>
          )}
          {statement.evidence.length > 0 && (
            <>
              <p className="detail-label">Důkazy z programu</p>
              {statement.evidence.map((e, i) => (
                <div key={i} className="evidence-item">
                  <p className="evidence-quote">"{e.quote}"</p>
                  <p className="evidence-citation">{e.citation}</p>
                </div>
              ))}
            </>
          )}
        </div>
      )}
    </div>
  )
}
