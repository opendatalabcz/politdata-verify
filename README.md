***
<img src="https://fit.cvut.cz/static/images/fit-cvut-logo-cs.svg" alt="logo FIT ČVUT" height="200">

Tento software vznikl za podpory **Fakulty informačních technologií ČVUT v Praze**.
Více informací naleznete na [fit.cvut.cz](https://fit.cvut.cz).
Otevřený repozitář naleznete na [https://github.com/opendatalabcz/politdata-verify](https://github.com/opendatalabcz/politdata-verify).

---

# politdata-verify

Systém pro automatické ověřování politických výroků vůči volebním programům českých politických subjektů.

Systém využívá architekturu **Retrieval-Augmented Generation (RAG)**: volební programy jsou indexovány do vektorové databáze pomocí hybridní reprezentace kombinující husté embeddingy (Jina AI) a řídkou reprezentaci BM25. Při ověřování výroku systém rozšiřuje dotaz pomocí LLM na několik variant, provede hybridní vyhledávání relevantních pasáží a výrok klasifikuje jako **SUPPORTED**, **CONTRADICTED** nebo **INSUFFICIENT** prostřednictvím modelu GPT-4o.

Součást bakalářské práce: *Ověřování politických výroků na základě parlamentních a předvolebních dat* (FIT ČVUT, 2026).

## Architektura

**Indexační fáze** (jednorázově před spuštěním):

```
PDF volebního programu
          │
          ▼
    Chunking (heading-aware)
          │
          ▼
  Embeddings (Jina AI) + BM25
          │
          ▼
       Milvus
```

**Ověřovací fáze** (při každém dotazu):

```
Vstupní výrok
     │
     ▼
Rozšíření dotazu (LLM, 5 variant)
     │
     ▼
Hybridní vyhledávání v Milvus (BM25 + dense embeddings)
     │
     ▼
Klasifikace výroku (GPT-4o) → SUPPORTED / CONTRADICTED / INSUFFICIENT
```

Systém se skládá z pěti Docker služeb:

| Služba       | Popis                                      |
|--------------|--------------------------------------------|
| `frontend`   | Webové rozhraní (React + nginx, port 80)   |
| `backend`    | REST API (FastAPI, port 8000)              |
| `standalone` | Vektorová databáze Milvus (port 19530)     |
| `etcd`       | Metadata store pro Milvus                  |
| `minio`      | Objektové úložiště pro Milvus              |

## Požadavky

- [Docker](https://www.docker.com/) a Docker Compose
- Python 3.12+ (pouze pro lokální vývoj bez Dockeru)
- API klíče: OpenAI, Jina AI

## Spuštění

1. Zkopírujte šablonu konfigurace a vyplňte hodnoty:

```bash
cp .env.example .env
```

Povinné proměnné v `.env`:

```
OPENAI_API_KEY=...       # klíč OpenAI API
JINA_API_KEY=...         # klíč Jina AI API
ADMIN_API_TOKEN=...      # libovolný tajný token pro REST API
ADMIN_PASSWORD=...       # heslo pro admin sekci v UI
JWT_SECRET=...           # náhodný řetězec pro podepisování JWT
VITE_API_KEY=...         # stejná hodnota jako ADMIN_API_TOKEN
```

2. Spusťte celý systém:

```bash
docker-compose up --build -d
```

Po spuštění jsou dostupné:
- Webové rozhraní: [http://localhost](http://localhost)
- API dokumentace (Swagger): [http://localhost:8000/docs](http://localhost:8000/docs)

## Indexace volebních programů

Před prvním použitím je nutné naindexovat volební programy do vektorové databáze. Indexaci a správu dokumentů lze provést přes **admin sekci webového rozhraní** (vyžaduje `ADMIN_PASSWORD`) nebo přes interaktivní API dokumentaci na [http://localhost:8000/docs](http://localhost:8000/docs).

## Ověření výroku

Po naindexování programů lze výroky ověřovat přes **webové rozhraní** nebo REST API. Výsledkem je verdikt `SUPPORTED` / `CONTRADICTED` / `INSUFFICIENT` spolu s relevantními pasážemi z volebního programu, na jejichž základě byl verdikt vyvozen.

## Vývojové prostředí

Pro lokální vývoj bez Dockeru slouží skript `dev.sh`, který spustí Milvus stack přes Docker Compose, backend přes `uvicorn --reload` a frontend přes Vite dev server. Frontend v tomto režimu vyžaduje soubor `fe/.env.local`:

```
VITE_API_KEY=...   # stejná hodnota jako ADMIN_API_TOKEN v .env
```

## Struktura projektu

```
app/        backendová aplikace (Python 3.12, FastAPI)
fe/         frontendová aplikace (React, TypeScript, Vite)
testing/    testovací dataset a automatizované testy
```

## Omezení

- Znalostní báze je statická — pro ověřování vůči novým dokumentům je nutná jejich ruční indexace.
- Systém závisí na externích API (OpenAI, Jina AI) — bez platných klíčů nefunguje.
- Evaluace byla provedena na ručně sestaveném datasetu 60 výroků; výsledky je třeba interpretovat s ohledem na jeho omezený rozsah.

## Autor

Petr Herčko — [FIT ČVUT](https://fit.cvut.cz), 2026
