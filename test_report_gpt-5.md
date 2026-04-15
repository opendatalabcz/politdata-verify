# Political Classification Test Report

## 1. Statistics by Party

| Party | Correct | Wrong | Accuracy |
| :--- |:--------|:------|:---------|
| SPD | 10      | 0     | 100.0%   |
| Starostové a nezávislí | 9       | 1     | 90.0%    |
| Piráti | 10      | 0     | 100.0%   |
| Motoristé sobě | 9       | 1     | 90.0%    |
| SPOLU | 10      | 0     | 100.0%   |
| ANO 2011 | 10      | 0     | 100.0%   |

## 2. Failure Log (Reason & Confidence)

| Party | Statement | Expected | Actual / Rationale |
| :--- | :--- | :--- | :--- |
| Starostové a nezávislí | Z ekologických i strategických důvodů podporujeme rychlou výstavbu nových paroplynových zdrojů přesně tam, kde dříve stály uhelné elektrárny. | SUPPORTED | AssertionError: Verdict: INSUFFICIENT | Confidence: 0.63 | Rationale: Program zmiňuje zrychlení výstavby paroplynových zdrojů na místech bývalých uhelných elektráren. Neuvádí však, že je to z ekologických i strategických důvodů. Chybí tedy potvrzení motivace uvedené v tvrzení. assert 'INSUFFICIENT' == 'SUPPORTED'      [0m[91m- SUPPORTED[39;49;00m[90m[39;49;00m   [92m+ INSUFFICIENT[39;49;00m[90m[39;49;00m |
| Motoristé sobě | Zavedeme daň z cukru a slazených nápojů, abychom získali prostředky na financování zdravotnictví. | INSUFFICIENT | AssertionError: Verdict: CONTRADICTED | Confidence: 0.79 | Rationale: Program strany výslovně odmítá zvyšování daní a uvádí, že nové výdaje se mají krýt úsporami, nikoli novými daněmi. O zavedení daně z cukru či slazených nápojů není v kontextu zmínka. assert 'CONTRADICTED' == 'INSUFFICIENT'      [0m[91m- INSUFFICIENT[39;49;00m[90m[39;49;00m   [92m+ CONTRADICTED[39;49;00m[90m[39;49;00m |
