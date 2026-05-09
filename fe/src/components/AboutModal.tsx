interface Props {
  onClose: () => void
}

export default function AboutModal({ onClose }: Props) {
  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal modal-wide" onClick={e => e.stopPropagation()}>

        <div className="modal-header">
          <span>O projektu</span>
          <button className="modal-close" onClick={onClose}>✕</button>
        </div>

        <div className="modal-body about-body">

          <p className="about-lead">
            PolitData Verify je nástroj pro automatické ověřování politických výroků
            na základě předvolebních programů politických stran. Systém využívá
            embedding modely a velké jazykové modely (LLM) pro sémantické porovnávání
            parlamentních projevů s obsahem stranických programů.
          </p>

          <div className="about-section">
            <h3>Jak nástroj používat</h3>

            <div className="how-to-grid">
              <div className="how-to-card">
                <div className="how-to-icon">💬</div>
                <div>
                  <strong>Analýza debaty</strong>
                  <p>
                    Vložte text parlamentního stenozáznamu. Systém automaticky
                    rozpozná řečníky, extrahuje jejich politické výroky a každý
                    výrok ověří vůči stranickým programům. Volitelně můžete
                    předvyplnit seznam řečníků pro přesnější přiřazení stran.
                  </p>
                  <p style={{ marginTop: '8px' }}>
                    <strong>⚡ Paralelní režim</strong> — výroky se zpracovávají
                    současně, analýza je rychlejší. Doporučeno pro většinu případů.
                    <br />
                    <strong>🐢 Postupný režim</strong> — výroky se zpracovávají
                    jeden po druhém, vhodné při výpadcích nebo limitech API.
                  </p>
                </div>
              </div>

              <div className="how-to-card">
                <div className="how-to-icon">🔎</div>
                <div>
                  <strong>Ověření jednotlivého výroku</strong>
                  <p>
                    Zadejte konkrétní politický výrok, vyberte stranu a rok
                    programu. Systém vyhledá relevantní části stranického
                    programu a vydá verdikt s citací důkazů.
                  </p>
                </div>
              </div>

              <div className="how-to-card">
                <div className="how-to-icon">📄</div>
                <div>
                  <strong>Správa dokumentů</strong>
                  <p>
                    Nahrajte stranické programy ve formátu PDF přes URL odkaz.
                    Dokument je automaticky zpracován, rozdělen na části
                    a uložen do vektorové databáze pro pozdější vyhledávání.
                  </p>
                </div>
              </div>
            </div>
          </div>

          <div className="about-section">
            <h3>Verdikty</h3>
            <div className="verdict-legend">
              <div className="legend-item">
                <span className="pill pill-green">✅ Podpořeno</span>
                <span>Výrok je v souladu se stranickým programem.</span>
              </div>
              <div className="legend-item">
                <span className="pill pill-red">❌ Odporuje</span>
                <span>Výrok je v přímém rozporu se stranickým programem.</span>
              </div>
              <div className="legend-item">
                <span className="pill pill-gray">❓ Nedostatek dat</span>
                <span>Program neobsahuje dostatek informací k ověření výroku.</span>
              </div>
            </div>
          </div>

          <div className="about-confidence">
            <h4>Jak číst hodnotu jistoty (confidence)</h4>
            <p>Každý verdikt je doprovázen hodnotou jistoty — jak přesvědčený byl model při klasifikaci. Čím vyšší číslo, tím spolehlivější výsledek.</p>
            <div className="conf-example-row">
              <div className="conf-example high">
                <span className="conf-num">71–100 %</span>
                <span>Model si verdiktem byl jistý</span>
              </div>
              <div className="conf-example low">
                <span className="conf-num">0–70 %</span>
                <span>Nízká jistota — doporučujeme manuální přezkum</span>
              </div>
            </div>
            <p className="about-note">
              Výroky s jistotou 70 % a méně jsou zvýrazněny žlutým okrajem. Může jít o hraniční případ nebo výrok, jehož téma program zmiňuje jen okrajově.
            </p>
          </div>

          <div className="about-section">
            <h3>Použité technologie</h3>
            <div className="tech-list">
              <span className="tech-tag">GPT-4o (OpenAI)</span>
              <span className="tech-tag">Jina AI Embeddings</span>
              <span className="tech-tag">Milvus</span>
              <span className="tech-tag">FastAPI</span>
              <span className="tech-tag">React + TypeScript</span>
              <span className="tech-tag">RAG Pipeline</span>
            </div>
          </div>

        </div>

        <div className="modal-footer">
          <button className="btn btn-primary" onClick={onClose}>Zavřít</button>
        </div>

      </div>
    </div>
  )
}
