const PARTY_COLORS: Record<string, { bg: string; text: string }> = {
  'ANO 2011':                { bg: '#0070C0', text: '#fff' },
  'ODS':                     { bg: '#004A99', text: '#fff' },
  'TOP 09':                  { bg: '#C02942', text: '#fff' },
  'KDU-ČSL':                 { bg: '#d4a800', text: '#fff' },
  'STAN':                    { bg: '#E91E8C', text: '#fff' },
  'Starostové a nezávislí':  { bg: '#E91E8C', text: '#fff' },
  'Piráti':                  { bg: '#231F20', text: '#fff' },
  'Česká pirátská strana':   { bg: '#231F20', text: '#fff' },
  'SPD':                     { bg: '#8B0000', text: '#fff' },
  'Motoristé sobě':          { bg: '#FF6C00', text: '#fff' },
  'SPOLU':                   { bg: '#004A99', text: '#fff' },
  'ČSSD':                    { bg: '#F4733D', text: '#fff' },
}

const DEFAULT = { bg: '#64748b', text: '#fff' }

export function getPartyColor(party: string | null | undefined) {
  if (!party) return DEFAULT
  return PARTY_COLORS[party] ?? DEFAULT
}
