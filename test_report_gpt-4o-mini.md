# Political Classification Test Report

## 1. Statistics by Party

| Party | Correct | Wrong | Accuracy |
| :--- |:--------|:------|:---------|
| SPD | 10      | 0     | 100.0%   |
| Starostové a nezávislí | 9       | 1     | 90.0%    |
| Piráti | 10      | 0     | 100.0%   |
| Motoristé sobě | 7       | 3     | 70.0%    |
| SPOLU | 8       | 2     | 80.0%    |
| ANO 2011 | 9       | 1     | 90.0%    |

## 2. Failure Log (Reason & Confidence)

| Party | Statement | Expected | Actual / Rationale |
| :--- | :--- | :--- | :--- |
| Starostové a nezávislí | Aby se zvýšila kvalita veřejných vysokých škol, je nutné na nich neprodleně zavést plošné školné pro všechny studenty. | INSUFFICIENT | AssertionError: Verdict: CONTRADICTED | Confidence: 0.9 | Rationale: V textu není zmínka o zavedení plošného školného pro všechny studenty jako prostředku ke zvýšení kvality veřejných vysokých škol. Naopak, je zde zmíněno o podpoře stávajících vysokých škol a posílení jejich role ve společnosti. assert 'CONTRADICTED' == 'INSUFFICIENT'      [0m[91m- INSUFFICIENT[39;49;00m[90m[39;49;00m   [92m+ CONTRADICTED[39;49;00m[90m[39;49;00m |
| Motoristé sobě | Zavedeme daň z cukru a slazených nápojů, abychom získali prostředky na financování zdravotnictví. | INSUFFICIENT | AssertionError: Verdict: CONTRADICTED | Confidence: 0.9 | Rationale: V kontextu se nezmiňuje o zavedení daně z cukru a slazených nápojů jako prostředku financování zdravotnictví. Naopak, program Motoristů sobě se vymezuje proti zvyšování daní. assert 'CONTRADICTED' == 'INSUFFICIENT'      [0m[91m- INSUFFICIENT[39;49;00m[90m[39;49;00m   [92m+ CONTRADICTED[39;49;00m[90m[39;49;00m |
| Motoristé sobě | Zavedeme plošně bezplatnou městskou hromadnou dopravu pro všechny seniory a studenty. | INSUFFICIENT | AssertionError: Verdict: CONTRADICTED | Confidence: 0.9 | Rationale: Kontext neuvádí žádně zavedení plošné bezplatné městské hromadné dopravy pro seniory a studenty, ale spíše zdůrazňuje důležitost dopravy a potřebu jejího rozvoje. Neexistuje žádná podpora pro tvrzení o bezplatné dopravě pro uvedené skupiny. assert 'CONTRADICTED' == 'INSUFFICIENT'      [0m[91m- INSUFFICIENT[39;49;00m[90m[39;49;00m   [92m+ CONTRADICTED[39;49;00m[90m[39;49;00m |
| Motoristé sobě | Zvýšíme platy všech pedagogických pracovníků plošně na 130 % průměrné mzdy do konce volebního období. | INSUFFICIENT | AssertionError: Verdict: CONTRADICTED | Confidence: 0.9 | Rationale: Dokumenty nesouhlasí se zvýšením platů všech pedagogických pracovníků na 130 % průměrné mzdy. Místo toho se zmiňuje reforma platových tabulek a možnost dosažení nejvyššího stupně po pěti letech praxe, což nespecifikuje plošné zvýšení platů. assert 'CONTRADICTED' == 'INSUFFICIENT'      [0m[91m- INSUFFICIENT[39;49;00m[90m[39;49;00m   [92m+ CONTRADICTED[39;49;00m[90m[39;49;00m |
| SPOLU | Agendu cestovního ruchu přesuneme pod Ministerstvo dopravy. | CONTRADICTED | AssertionError: Verdict: INSUFFICIENT | Confidence: 0.0 | Rationale: Kontext neobsahuje žádné informace o tom, pod které ministerstvo by měla být agenda cestovního ruchu přesunuta. Nemáme tedy dostatek údajů k posouzení tvrzení. assert 'INSUFFICIENT' == 'CONTRADICTED'      [0m[91m- CONTRADICTED[39;49;00m[90m[39;49;00m   [92m+ INSUFFICIENT[39;49;00m[90m[39;49;00m |
| SPOLU | Zavedeme povinnou vojenskou službu pro všechny občany od 18 let věku v délce 12 měsíců. | INSUFFICIENT | AssertionError: Verdict: CONTRADICTED | Confidence: 0.9 | Rationale: Kontext nezmiňuje zavedení povinné vojenské služby pro všechny občany, naopak se věnuje motivaci společnosti k převzetí branné povinnosti a zveřejňuje programy pro školy a organizace, ale bez ohledu na povinnou službu. assert 'CONTRADICTED' == 'INSUFFICIENT'      [0m[91m- INSUFFICIENT[39;49;00m[90m[39;49;00m   [92m+ CONTRADICTED[39;49;00m[90m[39;49;00m |
| ANO 2011 | Zřídíme nové Ministerstvo pro digitalizaci a inovace, aby stát lépe komunikoval s občany. | INSUFFICIENT | AssertionError: Verdict: CONTRADICTED | Confidence: 0.9 | Rationale: V kontextu není zmínka o zřízení nového Ministerstva pro digitalizaci a inovace. Naopak, plánuje se zrušení ministerstva pro místní rozvoj, což naznačuje, že strategie nemá zahrnovat nový úřad pro digitalizaci. assert 'CONTRADICTED' == 'INSUFFICIENT'      [0m[91m- INSUFFICIENT[39;49;00m[90m[39;49;00m   [92m+ CONTRADICTED[39;49;00m[90m[39;49;00m |
