import { useState, useEffect } from 'react'
import { fetchSpeakers, type SpeakerInfo } from '../api/client'
import { getPartyColor } from '../data/partyColors'
import type { Speaker } from '../types'

interface Props {
  speakers: Speaker[]
  onConfirm: (speakers: Speaker[]) => void
  onClose: () => void
}

export default function PoliticianModal({ speakers, onConfirm, onClose }: Props) {
  const [selected, setSelected] = useState<Speaker[]>(speakers)
  const [search, setSearch] = useState('')
  const [customName, setCustomName] = useState('')
  const [customSurname, setCustomSurname] = useState('')
  const [customParty, setCustomParty] = useState('')
  const [politicians, setPoliticians] = useState<SpeakerInfo[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchSpeakers()
      .then(setPoliticians)
      .catch(() => setPoliticians([]))
      .finally(() => setLoading(false))
  }, [])

  const filtered = politicians.filter(p => {
    const q = search.toLowerCase()
    return p.name.toLowerCase().includes(q) || p.party.toLowerCase().includes(q)
  })

  function parseName(fullName: string): { name: string; surname: string } {
    const idx = fullName.indexOf(' ')
    if (idx === -1) return { name: fullName, surname: '' }
    return { name: fullName.slice(0, idx), surname: fullName.slice(idx + 1) }
  }

  function toggle(p: SpeakerInfo) {
    const { name, surname } = parseName(p.name)
    const exists = selected.find(s => s.name === name && s.surname === surname)
    if (exists) {
      setSelected(prev => prev.filter(s => !(s.name === name && s.surname === surname)))
    } else {
      setSelected(prev => [...prev, { name, surname, party: p.party, photo_url: null }])
    }
  }

  function isSelected(p: SpeakerInfo) {
    const { name, surname } = parseName(p.name)
    return selected.some(s => s.name === name && s.surname === surname)
  }

  function addCustom() {
    if (!customName.trim() || !customSurname.trim()) return
    const exists = selected.find(s => s.name === customName.trim() && s.surname === customSurname.trim())
    if (!exists) {
      setSelected(prev => [...prev, { name: customName.trim(), surname: customSurname.trim(), party: customParty.trim() || null, photo_url: null }])
    }
    setCustomName(''); setCustomSurname(''); setCustomParty('')
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={e => e.stopPropagation()}>

        <div className="modal-header">
          <span>👤 Vybrat řečníky</span>
          <button className="modal-close" onClick={onClose}>✕</button>
        </div>

        <div className="modal-body">
          {selected.length > 0 && (
            <div className="selected-speakers">
              <p className="detail-label">Vybráni ({selected.length})</p>
              <div className="selected-list">
                {selected.map(s => (
                  <div key={`${s.name}-${s.surname}`} className="selected-tag">
                    <span>{s.name} {s.surname}</span>
                    <span className="tag-party">{s.party}</span>
                    <button onClick={() => setSelected(prev => prev.filter(x => !(x.name === s.name && x.surname === s.surname)))}>✕</button>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="form-group" style={{ marginTop: selected.length > 0 ? '16px' : '0' }}>
            <label htmlFor="pol-search">Hledat politika</label>
            <input
              id="pol-search"
              type="text"
              value={search}
              onChange={e => setSearch(e.target.value)}
              placeholder="Jméno nebo strana…"
              autoFocus
            />
          </div>

          <div className="politician-list">
            {loading && <p style={{ color: 'var(--text-muted)', fontSize: '14px', padding: '12px 0' }}>Načítám…</p>}
            {!loading && filtered.map(p => (
              <div
                key={p.name}
                className={`politician-row${isSelected(p) ? ' selected' : ''}`}
                onClick={() => toggle(p)}
              >
                <div className="pol-name">{p.name}</div>
                <span className="party-badge" style={{ background: getPartyColor(p.party).bg, color: getPartyColor(p.party).text }}>{p.party}</span>
                {isSelected(p) && <span className="pol-check">✓</span>}
              </div>
            ))}
            {!loading && filtered.length === 0 && (
              <p style={{ color: 'var(--text-muted)', fontSize: '14px', padding: '12px 0' }}>
                Žádný politik nenalezen.
              </p>
            )}
          </div>

          <div style={{ marginTop: '16px', paddingTop: '16px', borderTop: '1px solid var(--border)' }}>
            <p className="detail-label">Přidat vlastního řečníka</p>
            <div className="form-row" style={{ marginTop: '8px' }}>
              <div className="form-group">
                <label>Jméno</label>
                <input type="text" value={customName} onChange={e => setCustomName(e.target.value)} placeholder="Jméno" />
              </div>
              <div className="form-group">
                <label>Příjmení</label>
                <input type="text" value={customSurname} onChange={e => setCustomSurname(e.target.value)} placeholder="Příjmení" />
              </div>
            </div>
            <div className="form-group" style={{ marginTop: '8px' }}>
              <label>Strana (volitelné)</label>
              <input type="text" value={customParty} onChange={e => setCustomParty(e.target.value)} placeholder="Název strany" />
            </div>
            <button
              type="button"
              className="btn btn-ghost btn-sm"
              style={{ marginTop: '10px' }}
              onClick={addCustom}
              disabled={!customName.trim() || !customSurname.trim()}
            >
              + Přidat
            </button>
          </div>

        </div>

        <div className="modal-footer">
          <button className="btn btn-ghost" onClick={onClose}>Zrušit</button>
          <button className="btn btn-primary" onClick={() => { onConfirm(selected); onClose() }}>
            Potvrdit ({selected.length})
          </button>
        </div>

      </div>
    </div>
  )
}
