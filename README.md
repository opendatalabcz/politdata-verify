***
<img src="https://fit.cvut.cz/static/images/fit-cvut-logo-cs.svg" alt="logo FIT ČVUT" height="200">

Tento software vznikl za podpory **Fakulty informačních technologií ČVUT v Praze**.
Více informací naleznete na [fit.cvut.cz](https://fit.cvut.cz).
Otevřený repozitář naleznete na [https://github.com/opendatalabcz/politdata-verify](https://github.com/opendatalabcz/politdata-verify).

---

# politdata-verify

Systém pro automatické ověřování politických výroků vůči volebním programům českých politických subjektů. Využívá architekturu Retrieval-Augmented Generation (RAG) s hybridním vyhledáváním (husté embeddingy + BM25) a klasifikaci výroků pomocí velkého jazykového modelu.

Součást bakalářské práce: *Ověřování politických výroků na základě parlamentních a předvolebních dat* (FIT ČVUT, 2026).

## Požadavky

- [Docker](https://www.docker.com/) a Docker Compose
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
docker-compose up --build
```

Po spuštění jsou dostupné:
- Webové rozhraní: [http://localhost:5173](http://localhost:5173)
- REST API: [http://localhost:8000](http://localhost:8000)
- API dokumentace (Swagger): [http://localhost:8000/docs](http://localhost:8000/docs)

## Struktura projektu

```
app/        backendová aplikace (Python, FastAPI)
fe/         frontendová aplikace (React, TypeScript, Vite)
testing/    testovací dataset a automatizované testy
```

## Testování

```bash
cd testing
pytest
```

## Autor

Petr Herčko — [FIT ČVUT](https://fit.cvut.cz), 2026
