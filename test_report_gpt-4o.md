# Political Classification Test Report

## 1. Statistics by Party

| Party | Correct | Wrong | Accuracy |
| :--- | :--- | :--- | :--- |
| SPD | 8 | 2 | 80.0% |
| Starostové a nezávislí | 9 | 1 | 90.0% |
| Piráti | 10 | 0 | 100.0% |
| Motoristé sobě | 9 | 1 | 90.0% |
| SPOLU | 9 | 1 | 90.0% |
| ANO 2011 | 10 | 0 | 100.0% |

## 2. Failure Log (Reason & Confidence)

| Party | Statement | Expected | Actual / Rationale |
| :--- | :--- | :--- | :--- |
| SPD | Každý mladý občan by měl mít povinnost projít alespoň základním armádním výcvikem, abychom posílili obranu státu. | CONTRADICTED | AssertionError: Verdict: INSUFFICIENT | Confidence: 0.85 | Rationale: V dostupném kontextu se nezmiňuje o povinnosti mladých občanů projít základním armádním výcvikem. Tento konkrétní aspekt v textu chybí. assert 'INSUFFICIENT' == 'CONTRADICTED'      [0m[91m- CONTRADICTED[39;49;00m[90m[39;49;00m   [92m+ INSUFFICIENT[39;49;00m[90m[39;49;00m |
| SPD | Stát by měl aktivně finančně pomáhat obcím v tom, aby mohly samy stavět dostupné bydlení pro své obyvatele. | SUPPORTED | AssertionError: Verdict: INSUFFICIENT | Confidence: 0.6 | Rationale: V rámci kontextu není dostatečně specifikováno, zda stát aktivně finančně pomáhá obcím při budování dostupného bydlení. Dokumenty se soustředí na jiná témata související s dostupným bydlením. assert 'INSUFFICIENT' == 'SUPPORTED'      [0m[91m- SUPPORTED[39;49;00m[90m[39;49;00m   [92m+ INSUFFICIENT[39;49;00m[90m[39;49;00m |
| Starostové a nezávislí | Aby se zvýšila kvalita veřejných vysokých škol, je nutné na nich neprodleně zavést plošné školné pro všechny studenty. | INSUFFICIENT | AssertionError: Verdict: CONTRADICTED | Confidence: 1.0 | Rationale: V uvedených dokumentech strana Starostové a nezávislí nevyžaduje zavedení plošného školného pro zvýšení kvality vysokých škol, což je v rozporu s dotazovaným tvrzením. assert 'CONTRADICTED' == 'INSUFFICIENT'      [0m[91m- INSUFFICIENT[39;49;00m[90m[39;49;00m   [92m+ CONTRADICTED[39;49;00m[90m[39;49;00m |
| Motoristé sobě | Zrušíme deváté třídy pro ty žáky, kteří budou pokračovat ve studiu na střední škole. [cite: 321] | SUPPORTED | AssertionError: Verdict: INSUFFICIENT | Confidence: 0.8 | Rationale: Kontext sice zmiňuje zrušení devátých tříd, ale nevyjasňuje, zda se toto zrušení týká jen žáků, kteří budou pokračovat ve studiu na střední škole. assert 'INSUFFICIENT' == 'SUPPORTED'      [0m[91m- SUPPORTED[39;49;00m[90m[39;49;00m   [92m+ INSUFFICIENT[39;49;00m[90m[39;49;00m |
| SPOLU | Zrušíme Ministerstvo pro místní rozvoj a omezíme duplicity agend. | SUPPORTED | AssertionError: Verdict: INSUFFICIENT | Confidence: 0.6 | Rationale: V kontextu se zmiňuje rušení Ministerstva pro místní rozvoj, ale konkrétní důkaz pro tvrzení není uveden. Kontext dále obsahuje body o omezení duplicit agend, ale bez specifikace, které konkrétní agendy to zahrnuje. assert 'INSUFFICIENT' == 'SUPPORTED'      [0m[91m- SUPPORTED[39;49;00m[90m[39;49;00m   [92m+ INSUFFICIENT[39;49;00m[90m[39;49;00m |
