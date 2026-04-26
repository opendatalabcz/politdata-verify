import { useState } from 'react'
import type { SpeakerStats, ClassifiedStatementWithContext } from '../types'
import StatementItem from './StatementItem'
import { getPartyLogo } from '../data/partyLogos'
import { getPartyColor } from '../data/partyColors'

interface Props {
  speaker: SpeakerStats
  colorIndex: number
  filterVerdict?: 'supported' | 'contradicted' | 'insufficient'
}

const AVATAR_COLORS = ['#1e3a5f', '#2d6a4f', '#6b21a8', '#9a3412', '#1e40af', '#065f46', '#7c2d12']

function initials(name: string, surname: string) {
  return `${name[0]}${surname[0]}`.toUpperCase()
}

export default function SpeakerCard({ speaker, colorIndex, filterVerdict }: Props) {
  const [open, setOpen] = useState(false)

  const color = AVATAR_COLORS[colorIndex % AVATAR_COLORS.length]
  const total = speaker.total_statements
  const nS = speaker.supported.length
  const nC = speaker.contradicted.length
  const nI = speaker.insufficient.length
  const pS = total ? (nS / total) * 100 : 0
  const pC = total ? (nC / total) * 100 : 0
  const pI = total ? (nI / total) * 100 : 0

  const allStatements: ClassifiedStatementWithContext[] = filterVerdict
    ? speaker[filterVerdict]
    : [
        ...speaker.supported,
        ...speaker.contradicted,
        ...speaker.insufficient,
      ]

  const { name, surname, party, photo_url } = speaker.speaker
  const logoUrl = getPartyLogo(party)
  const partyColor = getPartyColor(party)

  return (
    <div className="speaker-card">
      <div className="speaker-header" onClick={() => setOpen(o => !o)}>
        <div className="avatar-wrap">
          {photo_url ? (
            <img src={photo_url} alt={`${name} ${surname}`} className="avatar avatar-photo" />
          ) : (
            <div className="avatar" style={{ background: color }}>{initials(name, surname)}</div>
          )}
          {logoUrl && (
            <img src={logoUrl} alt={party ?? ''} className="party-logo-badge" />
          )}
        </div>

        <div className="speaker-info">
          <div className="speaker-name">{name} {surname}</div>
          <span
            className="party-badge"
            style={{ background: partyColor.bg, color: partyColor.text }}
          >{party || 'Neznámá strana'}</span>
        </div>

        <div className="verdict-pills">
          {nS > 0 && <span className="pill pill-green">✅ {nS} podpořeno</span>}
          {nC > 0 && <span className="pill pill-red">❌ {nC} odporuje</span>}
          {nI > 0 && <span className="pill pill-gray">❓ {nI} neurčito</span>}
        </div>

        <span className={`chevron${open ? ' open' : ''}`}>▾</span>
      </div>

      {/* Stacked progress bar showing proportion of verdicts */}
      <div className="progress-bar">
        <div className="seg seg-green" style={{ width: `${pS}%` }} />
        <div className="seg seg-red"   style={{ width: `${pC}%` }} />
        <div className="seg seg-gray"  style={{ width: `${pI}%` }} />
      </div>

      {open && (
        <div className="statements-list">
          {allStatements.map((stmt, i) => (
            <StatementItem key={i} statement={stmt} />
          ))}
        </div>
      )}
    </div>
  )
}
