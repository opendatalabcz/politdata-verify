import { useState, useEffect } from 'react'

const DEBATE_STEPS = [
  'Rozpoznávám řečníky a jejich stranické příslušnosti…',
  'Extrahuji politické výroky z textu…',
  'Generuji sémantické varianty dotazů…',
  'Prohledávám vektorovou databázi stranických programů…',
  'Porovnávám výroky s obsahem programů…',
  'Klasifikuji výroky pomocí jazykového modelu…',
  'Sestavuji výsledky a důkazy…',
]

const STATEMENT_STEPS = [
  'Připravuji dotaz k ověření…',
  'Generuji sémantické varianty výroku…',
  'Prohledávám stranický program…',
  'Hodnotím relevantní pasáže…',
  'Klasifikuji výrok jazykovým modelem…',
  'Sestavuji verdikt a citace…',
]

interface Props {
  mode: 'conversation' | 'statement'
}

export default function LoadingState({ mode }: Props) {
  const [elapsed, setElapsed] = useState(0)
  const [stepIdx, setStepIdx] = useState(0)

  const steps = mode === 'conversation' ? DEBATE_STEPS : STATEMENT_STEPS

  useEffect(() => {
    const timer = setInterval(() => setElapsed(s => s + 1), 1000)
    return () => clearInterval(timer)
  }, [])

  useEffect(() => {
    const interval = mode === 'conversation' ? 6000 : 5000
    const t = setInterval(() => {
      setStepIdx(i => (i + 1) % steps.length)
    }, interval)
    return () => clearInterval(t)
  }, [mode, steps.length])

  const title = mode === 'conversation' ? 'Analyzuji debatu…' : 'Ověřuji výrok…'

  return (
    <div className="loading-card">
      <div className="spinner" />
      <p className="loading-title">{title}</p>
      <p className="loading-step">{steps[stepIdx]}</p>
      <p className="elapsed">⏱ {elapsed} s</p>
    </div>
  )
}
