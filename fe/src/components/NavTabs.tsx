interface Props {
  active: 'analysis' | 'documents'
  onChange: (tab: 'analysis' | 'documents') => void
}

export default function NavTabs({ active, onChange }: Props) {
  return (
    <nav className="nav-tabs">
      <button
        className={`nav-tab${active === 'analysis' ? ' active' : ''}`}
        onClick={() => onChange('analysis')}
      >
        🔍 Analýza výroků
      </button>
      <button
        className={`nav-tab${active === 'documents' ? ' active' : ''}`}
        onClick={() => onChange('documents')}
      >
        📄 Správa dokumentů
      </button>
    </nav>
  )
}
