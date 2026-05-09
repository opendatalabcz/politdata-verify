import { useState, useRef, useEffect } from 'react'
import { startVerification, startSingleStatement, pollJobResult } from '../api/client'
import type { StatsResult, ClassifiedStatement, Speaker } from '../types'
import InputForm from '../components/InputForm'
import SingleStatementForm from '../components/SingleStatementForm'
import LoadingState from '../components/LoadingState'
import ResultsView from '../components/ResultsView'
import SingleStatementResult from '../components/SingleStatementResult'
import PoliticianModal from '../components/PoliticianModal'
import RateLimitModal from '../components/RateLimitModal'

type Mode   = 'conversation' | 'statement'
type Phase  = 'input' | 'loading' | 'results'
type Result = { kind: 'stats'; data: StatsResult }
            | { kind: 'statement'; data: ClassifiedStatement; query: string }

export default function AnalysisPage() {
  const [mode, setMode]           = useState<Mode>('conversation')
  const [phase, setPhase]         = useState<Phase>('input')
  const [result, setResult]       = useState<Result | null>(null)
  const [error, setError]           = useState<string | null>(null)
  const [speakers, setSpeakers]     = useState<Speaker[]>([])
  const [modalOpen, setModalOpen]   = useState(false)
  const [rateLimitMsg, setRateLimit] = useState<string | null>(null)

  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null)

  useEffect(() => {
    return () => { if (pollRef.current) clearInterval(pollRef.current) }
  }, [])

  function startPolling(jobId: string, kind: 'stats' | 'statement', query = '') {
    pollRef.current = setInterval(async () => {
      try {
        const data = await pollJobResult(jobId)
        if (data.status === 'COMPLETED') {
          clearInterval(pollRef.current!)
          if (kind === 'stats') {
            setResult({ kind: 'stats', data: data.result as StatsResult })
          } else {
            const stmts = (data.result as { classified_statements: ClassifiedStatement[] }).classified_statements
            setResult({ kind: 'statement', data: stmts[0], query })
          }
          setPhase('results')
        } else if (data.status === 'FAILED') {
          clearInterval(pollRef.current!)
          setError(data.error ?? 'Neznámá chyba.')
          setPhase('input')
        }
      } catch { /* network hiccup */ }
    }, 3000)
  }

  function handleApiError(err: unknown) {
    const e = err as Error & { status?: number }
    if (e.status === 429) {
      setRateLimit(e.message)
    } else {
      setError(e.message)
    }
  }

  async function handleConversationSubmit(text: string, collection: string, year: number, mode: 'sync' | 'async') {
    setError(null)
    try {
      const jobId = await startVerification(text, collection, year, speakers, mode)
      setPhase('loading')
      startPolling(jobId, 'stats')
    } catch (err) {
      handleApiError(err)
    }
  }

  async function handleStatementSubmit(query: string, collection: string, party: string | null, year: number) {
    setError(null)
    try {
      const jobId = await startSingleStatement(query, collection, party, year)
      setPhase('loading')
      startPolling(jobId, 'statement', query)
    } catch (err) {
      handleApiError(err)
    }
  }

  function handleReset() {
    if (pollRef.current) clearInterval(pollRef.current)
    setResult(null)
    setError(null)
    setPhase('input')
  }

  function handleModeChange(m: Mode) {
    handleReset()
    setMode(m)
  }

  return (
    <div>
      {/* Mode toggle — only show when in input phase */}
      {phase === 'input' && (
        <div className="mode-toggle-wrap">
          <div className="mode-toggle">
            <button
              className={`mode-btn${mode === 'conversation' ? ' active' : ''}`}
              onClick={() => handleModeChange('conversation')}
            >
              💬 Z debaty
            </button>
            <button
              className={`mode-btn${mode === 'statement' ? ' active' : ''}`}
              onClick={() => handleModeChange('statement')}
            >
              🔎 Jednotlivý výrok
            </button>
          </div>
        </div>
      )}

      <div className="card">
        {phase === 'input' && (
          <>
            <div className="card-header">
              {mode === 'conversation' ? '📋 Parlamentní stenozáznam' : '🔎 Ověření výroku'}
            </div>
            <div className="card-body">
              {mode === 'conversation' ? (
                <InputForm
                  speakers={speakers}
                  onOpenSpeakers={() => setModalOpen(true)}
                  onSubmit={handleConversationSubmit}
                  error={error}
                />
              ) : (
                <SingleStatementForm
                  onSubmit={handleStatementSubmit}
                  error={error}
                />
              )}
            </div>
          </>
        )}

        {phase === 'loading' && <LoadingState mode={mode} />}
      </div>

      {phase === 'results' && result?.kind === 'stats' && (
        <ResultsView stats={result.data} onReset={handleReset} />
      )}

      {phase === 'results' && result?.kind === 'statement' && (
        <div className="card" style={{ marginTop: '24px' }}>
          <div className="card-header">🔎 Výsledek ověření</div>
          <div className="card-body">
            <SingleStatementResult
              statement={result.data}
              query={result.query}
              onReset={handleReset}
            />
          </div>
        </div>
      )}

      {modalOpen && (
        <PoliticianModal
          speakers={speakers}
          onConfirm={setSpeakers}
          onClose={() => setModalOpen(false)}
        />
      )}

      {rateLimitMsg && (
        <RateLimitModal
          message={rateLimitMsg}
          onClose={() => setRateLimit(null)}
        />
      )}
    </div>
  )
}
