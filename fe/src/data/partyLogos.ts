// Maps party names (as returned by the backend) to logo URLs.
const PARTY_LOGOS: Record<string, string> = {
  'Piráti':                  'https://upload.wikimedia.org/wikipedia/commons/thumb/7/7c/Logo_Pir%C3%A1t%C5%AF.svg/3840px-Logo_Pir%C3%A1t%C5%AF.svg.png',
  'Starostové a nezávislí':  'https://www.starostove.cz/files/logo-starostove-ruzove.png',
  'ANO 2011':                'https://fe.anobudelip.cz/img/logo-ano.svg',
  'ODS':                     'https://www.ods.cz/img/logo/ods-logo-plna-barva.png',
  'KDU-ČSL':                 'https://www.kdu.cz/getmedia/1b0453e2-07c7-4d30-b1c1-3136252a5949/KDU-CSL---logo-zlute-pozadi.jpg.aspx?ext=.jpg&width=460',
  'TOP 09':                  'https://www.top09.cz/styles/assets/svg/logo-u.svg',
  'SPD':                     'https://spd.cz/wp-content/uploads/ke_stazeni/grafika/male-logo-spd.png',
  'Motoristé sobě':          'https://motoristesobe.cz/wp-content/uploads/header_motoriste-logo.jpg',
}

export function getPartyLogo(party: string | null | undefined): string | null {
  if (!party) return null
  return PARTY_LOGOS[party] ?? null
}
