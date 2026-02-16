"""
file to classify political statements
"""
from app.src.clients.openai_client import Client
from app.src.milvus.search import search
from app.src.political_statements.models import ClassifiedStatement

MODEL = "gpt-5-mini"  # Use a more cost-effective model for classification tasks

async def classify_statement(query: str, collection_name: str, **kwargs) -> ClassifiedStatement:
    """
    Classify a political statement into predefined categories.

    Args:
        query (str): The political statement to classify.
        collection_name (str): The name of the Milvus collection to search for context.
        **kwargs: Additional keyword arguments, such as 'party' and 'year'.

    Returns:
        ClassifiedStatement: The classified statement with verdict, rationale, evidence, and confidence.
    """
    party = kwargs.get("party", None)
    year = kwargs.get("year", None)
    interface = kwargs.get("interface", None)
    context = await search(collection_name, query, party=party, year=year, interface=interface)
    ### FACT-CHECKING PROMPT ###
    system_prompt = """
            You are a context-STRICT fact checker.

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

    CLASSIFICATION (choose exactly one):
    - "SUPPORTED" — the claim is clearly confirmed by the context.
    - "CONTRADICTED" — the claim is clearly denied or opposed by the context.
    - "INSUFFICIENT" — the context does not contain enough information to decide.

    OUTPUT FORMAT (JSON only, no explanation outside JSON):
    {
      "verdict": "SUPPORTED" | "CONTRADICTED" | "INSUFFICIENT",
      "rationale": "brief reasoning in English (max 3 sentences, no outside knowledge)",
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
    - If a claim contains multiple sub-claims, evaluate each and select the strictest applicable verdict (e.g., one contradictory sub-claim ⇒ CONTRADICTED).
    - Produce the final answer in English.
            """
    messages = [
        {"role": "system", "content": system_prompt},
        {
            "role": "user",
            "content": f"{context}, <query>{query}</query>",
        },
    ]
    client = Client()
    answer = client.get_structured_response(messages, schema=ClassifiedStatement, model=MODEL)
    return answer