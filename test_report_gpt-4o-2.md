# Political Classification Test Report

## 1. Statistics by Party

| Party | Correct | Wrong | Accuracy |
| :--- | :--- | :--- | :--- |
| SPD | 8 | 2 | 80.0% |
| Starostové a nezávislí | 9 | 1 | 90.0% |
| Piráti | 10 | 0 | 100.0% |
| Motoristé sobě | 10 | 0 | 100.0% |
| SPOLU | 10 | 0 | 100.0% |
| ANO 2011 | 9 | 1 | 90.0% |

## 2. Failure Log (Reason & Confidence)

| Party | Statement | Expected | Actual / Rationale |
| :--- | :--- | :--- | :--- |
| SPD | Každý mladý občan by měl mít povinnost projít alespoň základním armádním výcvikem, abychom posílili obranu státu. | CONTRADICTED | AssertionError: Verdict: INSUFFICIENT | Confidence: 0.8 | Rationale: V kontextu není zmínka o povinnosti základního armádního výcviku pro mladé občany. Taková informace o zavedení povinného výcviku chybí. assert 'INSUFFICIENT' == 'CONTRADICTED'      [0m[91m- CONTRADICTED[39;49;00m[90m[39;49;00m   [92m+ INSUFFICIENT[39;49;00m[90m[39;49;00m |
| SPD | Stát by měl aktivně finančně pomáhat obcím v tom, aby mohly samy stavět dostupné bydlení pro své obyvatele. | SUPPORTED | AssertionError: Verdict: INSUFFICIENT | Confidence: 0.8 | Rationale: Text se zaměřuje na podporu bytové výstavby obcemi, avšak konkrétní finanční pomoc státu směrem k obcím pro účely výstavby dostupného bydlení explicitně nezmiňuje. assert 'INSUFFICIENT' == 'SUPPORTED'      [0m[91m- SUPPORTED[39;49;00m[90m[39;49;00m   [92m+ INSUFFICIENT[39;49;00m[90m[39;49;00m |
| Starostové a nezávislí | Podnikatelé by neměli mít žádné speciální daňové úlevy jen proto, že uvolňují své zaměstnance k zásahům dobrovolných hasičů. | CONTRADICTED | AssertionError: Verdict: SUPPORTED | Confidence: 1.0 | Rationale: Program Starostové a nezávislí obsahuje návrh na daňové úlevy pro podniky, které uvolňují své zaměstnance k zásahům dobrovolných hasičů. assert 'SUPPORTED' == 'CONTRADICTED'      [0m[91m- CONTRADICTED[39;49;00m[90m[39;49;00m   [92m+ SUPPORTED[39;49;00m[90m[39;49;00m |
| ANO 2011 | Zřídíme nové Ministerstvo pro digitalizaci a inovace, aby stát lépe komunikoval s občany. | INSUFFICIENT | AssertionError: Verdict: CONTRADICTED | Confidence: 0.9 | Rationale: V kontextu je uvedeno, že funkci ministra pro vědu zrušíme [ANO 2011, 2025, 36]. Není zmíněno zřízení nového ministerstva pro digitalizaci a inovace. assert 'CONTRADICTED' == 'INSUFFICIENT'      [0m[91m- INSUFFICIENT[39;49;00m[90m[39;49;00m   [92m+ CONTRADICTED[39;49;00m[90m[39;49;00m |
