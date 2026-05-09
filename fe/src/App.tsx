import { useState, useEffect } from 'react'
import NavTabs from './components/NavTabs'
import AnalysisPage from './pages/AnalysisPage'
import DocumentsPage from './pages/DocumentsPage'
import Footer from './components/Footer'
import AboutModal from './components/AboutModal'

type Tab = 'analysis' | 'documents'

export default function App() {
  const [dark, setDark] = useState(() => {
    const saved = localStorage.getItem('theme')
    if (saved) return saved === 'dark'
    return window.matchMedia('(prefers-color-scheme: dark)').matches
  })

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', dark ? 'dark' : 'light')
    localStorage.setItem('theme', dark ? 'dark' : 'light')
  }, [dark])

  const [tab, setTab]           = useState<Tab>('analysis')
  const [aboutOpen, setAbout]   = useState(false)
  const [adminUnlocked, setAdminUnlocked] = useState(
    () => !!sessionStorage.getItem('admin_token')
  )
  const [pwInput, setPwInput]   = useState('')
  const [pwError, setPwError]   = useState(false)
  const [pwLoading, setPwLoading] = useState(false)

  async function handlePasswordSubmit(e: React.FormEvent) {
    e.preventDefault()
    setPwLoading(true)
    try {
      const { adminLogin } = await import('./api/client')
      const token = await adminLogin(pwInput)
      sessionStorage.setItem('admin_token', token)
      setAdminUnlocked(true)
      setPwError(false)
    } catch {
      setPwError(true)
      setPwInput('')
    } finally {
      setPwLoading(false)
    }
  }

  return (
    <>
      <header className="app-header">
        <div className="header-eyebrow">FIT ČVUT Praha · Bakalářská práce</div>
        <h1>PolitData Verify</h1>
        <p>Automatické ověřování politických výroků na základě stranických programů</p>

        <div className="header-actions">
          <button className="header-btn header-btn-icon" onClick={() => setDark(d => !d)} title={dark ? 'Světlý režim' : 'Tmavý režim'}>
            {dark ? <SunIcon /> : <MoonIcon />}
          </button>
          <button className="header-btn" onClick={() => setAbout(true)}>
            O projektu
          </button>
          <a
            href={`${import.meta.env.VITE_API_URL ?? ''}/docs`}
            target="_blank"
            rel="noopener noreferrer"
            className="header-btn"
            title="API dokumentace"
          >
            API docs
          </a>
          <a
            href="https://github.com/petaherec"
            target="_blank"
            rel="noopener noreferrer"
            className="header-btn header-btn-icon"
            title="GitHub"
          >
            <GitHubIcon />
          </a>
          <a
            href="https://www.linkedin.com/in/petr-her%C4%8Dko-55a28027b/"
            target="_blank"
            rel="noopener noreferrer"
            className="header-btn header-btn-icon"
            title="LinkedIn"
          >
            <LinkedInIcon />
          </a>
        </div>
      </header>

      <NavTabs active={tab} onChange={setTab} />

      <main>
        {tab === 'analysis' && <AnalysisPage />}
        {tab === 'documents' && (
          <>
            <DocumentsPage adminUnlocked={adminUnlocked} />
            {!adminUnlocked && (
              <div className="card" style={{ marginTop: '16px' }}>
                <div className="card-header">🔒 Administrace</div>
                <div className="card-body">
                  <form onSubmit={handlePasswordSubmit} className="admin-gate">
                    <p className="section-hint">Přihlaste se pro přidávání a mazání dokumentů.</p>
                    <div className="form-group" style={{ maxWidth: '320px' }}>
                      <label htmlFor="admin-pw">Heslo</label>
                      <input
                        id="admin-pw"
                        type="password"
                        value={pwInput}
                        placeholder="Vložte heslo"
                        onChange={e => { setPwInput(e.target.value); setPwError(false) }}
                        autoFocus
                      />
                      {pwError && <p style={{ color: 'var(--red)', fontSize: '13px', marginTop: '6px' }}>Nesprávné heslo.</p>}
                    </div>
                    <div className="form-actions">
                      <button className="btn btn-primary" type="submit" disabled={pwLoading}>
                        {pwLoading ? 'Ověřuji…' : 'Odemknout'}
                      </button>
                    </div>
                  </form>
                </div>
              </div>
            )}
          </>
        )}
      </main>

      <Footer />

      {aboutOpen && <AboutModal onClose={() => setAbout(false)} />}
    </>
  )
}

function LinkedInIcon() {
  return (
    <svg height="20" width="20" viewBox="0 0 24 24" fill="currentColor">
      <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853
        0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9
        1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337
        7.433a2.062 2.062 0 01-2.063-2.065 2.064 2.064 0 112.063 2.065zm1.782
        13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0
        1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24
        22.271V1.729C24 .774 23.2 0 22.222 0h.003z"
      />
    </svg>
  )
}

function MoonIcon() {
  return (
    <svg height="20" width="20" viewBox="0 0 24 24" fill="currentColor">
      <path d="M21 12.79A9 9 0 1111.21 3a7 7 0 109.79 9.79z" />
    </svg>
  )
}

function SunIcon() {
  return (
    <svg height="20" width="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
      <circle cx="12" cy="12" r="5"/>
      <line x1="12" y1="1" x2="12" y2="3"/>
      <line x1="12" y1="21" x2="12" y2="23"/>
      <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/>
      <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/>
      <line x1="1" y1="12" x2="3" y2="12"/>
      <line x1="21" y1="12" x2="23" y2="12"/>
      <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/>
      <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>
    </svg>
  )
}

function GitHubIcon() {
  return (
    <svg height="20" width="20" viewBox="0 0 16 16" fill="currentColor">
      <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38
        0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13
        -.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66
        .07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15
        -.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27
        .68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12
        .51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48
        0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"
      />
    </svg>
  )
}
