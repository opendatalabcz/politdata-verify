"""
Fact-checking pipeline: retrieves context from Milvus and classifies a statement via GPT-4o.
"""
from app.src.clients.openai_client import Client
from app.src.milvus.search import search
from app.src.political_statements.models import ClassifiedStatement, ClassifiedStatementWithContext

MODEL = "gpt-4o"
### FACT-CHECKING PROMPT ###
SYSTEM_PROMPT = """
    You are a fact checker verifying political claims against party program documents.

    INPUT:
    1) <context> … </context> — zero or more <document> blocks, each containing:
       <year>…</year>, <party>…</party>, <page_number>…</page_number>,
       <metadata>…</metadata>, <content>…</content>
    2) <claim>…</claim> — a short statement to verify.

    RULES:
    - Verify the claim EXCLUSIVELY using the text inside <content> of the provided documents.
    - Do NOT use outside knowledge, assumptions, or the web.
    - When citing evidence, use this exact inline citation format:
      [party: {party}, year: {year}, page: {page_number}]
    - If the context does not provide enough information, do NOT guess.

    BEFORE CLASSIFYING, answer these two questions internally:
    1. Is the topic of the claim mentioned anywhere in the context?
    2. If yes — does the context support or oppose the claim?
    Only return INSUFFICIENT if the answer to question 1 is "no" or "barely".

    CLASSIFICATION (choose exactly one):
    - "SUPPORTED" — the core intent of the claim is confirmed by the context, even if the exact
      wording differs or minor details are unspecified. If the context confirms the main policy
      action but omits a qualifying detail, return SUPPORTED and note the missing detail in rationale.
    - "CONTRADICTED" — the context contains an explicit statement that directly opposes or denies
      the claim. ABSENCE OF INFORMATION IS NEVER CONTRADICTION — if the topic is simply not
      mentioned, use INSUFFICIENT instead.
    - "INSUFFICIENT" — the topic of the claim is not mentioned or barely touched upon in the
      context, making it impossible to decide. Do NOT use this if the topic is present but
      described in different words or at a different level of detail.

    OUTPUT FORMAT (JSON only, no explanation outside JSON):
    {
      "verdict": "SUPPORTED" | "CONTRADICTED" | "INSUFFICIENT",
      "rationale": "brief reasoning in Czech (max 3 sentences, no outside knowledge)",
      "evidence": [
        {
          "quote": "short relevant quote from the content",
          "citation": "[party: {party}, year: {year}, page: {page_number}]"
        }
      ],
      "confidence": float 0.0–1.0
    }

    NOTES:
    - Use short but precise quotes.
    - TERMINOLOGY: Be flexible with synonyms (e.g., 'remuneration' vs 'salary', 'housing support'
      vs 'affordable housing fund'). If the meaning is identical or closely equivalent, mark as SUPPORTED.
    - PARTIAL MATCH: If context confirms the core claim but lacks one specific detail, prefer
      SUPPORTED over INSUFFICIENT — mention the unconfirmed detail in rationale.
    - OVER-INFERENCE: Do not assume that cutting budget A means you cannot fund project B unless
      explicitly stated.
    - Produce the final answer in Czech.
    """



async def classify_with_context(
    client,
    speaker,
    statement,
    semaphore,
    collection_name,
    milvus_interface,
    year
) -> ClassifiedStatementWithContext:
    """classify a statement and attach speaker context; semaphore limits concurrent OpenAI calls."""
    async with semaphore:
        verdict = await classify_statement(
            query=statement,
            collection_name=collection_name,
            client=client,
            interface=milvus_interface,
            party=speaker.party,
            year=year
        )

    return ClassifiedStatementWithContext(
        speaker=speaker,
        statement=statement,
        verdict=verdict.verdict,
        rationale=verdict.rationale,
        evidence=verdict.evidence,
        confidence=verdict.confidence
    )


async def classify_statement(query: str, collection_name: str, client: Client, **kwargs) -> ClassifiedStatement:
    """Retrieve relevant context from Milvus and classify the statement."""
    party = kwargs.get("party", None)
    year = kwargs.get("year", None)
    interface = kwargs.get("interface", None)
    context = await search(collection_name, query, party=party, year=year, interface=interface)
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": f"{context}, <query>{query}</query>",
        },
    ]
    answer = await client.get_structured_response_async(messages, schema=ClassifiedStatement, model=MODEL, temperature=0.0)
    return answer