export interface Politician {
  name: string
  surname: string
  party: string
}

export const POLITICIANS: Politician[] = [
  { name: 'Andrej',    surname: 'Babiš',               party: 'ANO 2011' },
  { name: 'Aleš',      surname: 'Juchelka',             party: 'ANO 2011' },
  { name: 'Karel',     surname: 'Havlíček',             party: 'ANO 2011' },
  { name: 'Radek',     surname: 'Vondráček',            party: 'ANO 2011' },
  { name: 'Petr',      surname: 'Fiala',                party: 'ODS' },
  { name: 'Jana',      surname: 'Černochová',           party: 'ODS' },
  { name: 'Zbyněk',   surname: 'Stanjura',             party: 'ODS' },
  { name: 'Vojtěch',  surname: 'Munzar',               party: 'ODS' },
  { name: 'Markéta',  surname: 'Pekarová Adamová',     party: 'TOP 09' },
  { name: 'Helena',   surname: 'Langšádlová',          party: 'TOP 09' },
  { name: 'Vlastimil', surname: 'Válek',               party: 'TOP 09' },
  { name: 'Marian',   surname: 'Jurečka',              party: 'KDU-ČSL' },
  { name: 'Vít',      surname: 'Rakušan',              party: 'STAN' },
  { name: 'Ivan',     surname: 'Bartoš',               party: 'Piráti' },
  { name: 'Olga',     surname: 'Richterová',           party: 'Piráti' },
  { name: 'Zdeněk',  surname: 'Hřib',                 party: 'Piráti' },
  { name: 'Mikuláš', surname: 'Ferjenčík',            party: 'Piráti' },
  { name: 'Tomáš',   surname: 'Okamura',              party: 'SPD' },
  { name: 'Radim',   surname: 'Fiala',                party: 'SPD' },
  { name: 'Petr',    surname: 'Fiala',                party: 'SPD' },
  { name: 'Jana',    surname: 'Maláčová',             party: 'ČSSD' },
  { name: 'Jiří',    surname: 'Pospíšil',             party: 'TOP 09' },
  { name: 'Patrik',  surname: 'Nacher',               party: 'ANO 2011' },
  { name: 'Jiří',    surname: 'Barták',               party: 'ANO 2011' },
  { name: 'Petr',    surname: 'Pavel',                party: 'Nezávislý' },
]

export const PARTIES = [...new Set(POLITICIANS.map(p => p.party))].sort()
