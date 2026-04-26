import logging
from typing import Dict, List
from collections import Counter

from app.src.clients.openai_client import Client
from app.src.milvus.milvus_interface import MilvusInterface
from pydantic import BaseModel

logger = logging.getLogger(__name__)
MODEL = "gpt-4o-mini"
CONTEXT_MAX_LEN = 70000
TOP_K = 40

PARTY_ALIAS_MAP: Dict[str, str] = {
    "ODS": "SPOLU",
    "TOP 09": "SPOLU",
    "KDU-ČSL": "SPOLU",
}

def normalize_party(party: str | None) -> str | None:
    if party is None:
        return None
    return PARTY_ALIAS_MAP.get(party.strip(), party)

class Queries(BaseModel):
    queries: List[str]

async def generate_multi_queries(query: str) -> Queries:
    """
    Generate multiple queries from the original query to improve search recall.
    :param query:
    :return:
    """
    system_prompt = """
    You are an expert political analyst and search engine optimization specialist. 
    Your task is to take a specific political claim or campaign promise and generate 5 different search queries to retrieve relevant evidence from official political program documents.
    
    Your goal is to overcome the limitations of distance-based vector search by providing variations that cover:
    1. Exact keywords from the original statement.
    2. Formal and legislative synonyms (e.g., using "remuneration" instead of "salary").
    3. Contextual themes (e.g., if the claim is about "TV fees," search for "public media funding").
    4. Specific numeric values or technical terms associated with the policy.
    
    Output Requirements:
    - Provide exactly 5 queries.
    - The queries must be in Czech (matching the language of the source documents).
    - Provide only the list of queries, one per line, without numbers or additional commentary.
    """
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Generate search queries for: {query}"}
    ]
    client = Client()
    queries = await client.get_structured_response_async(messages, schema=Queries, model=MODEL)
    return queries

async def search(collection_name: str, query: str, **kwargs) -> str:
    """
    Perform hybrid search on milvus collection

    Args:
        collection_name (str):   milvus collection name
        query (str):             search query

    Returns:
        List[Dict[str, Any]]:    list of relevant chunks
    """

    interface = kwargs.get("interface") or MilvusInterface()
    year = kwargs.get("year", None)
    party = normalize_party(kwargs.get("party", None))

    all_chunks = []
    logger.info(f"[MILVUS SEARCH] Generating multiple queries for: {query}")
    queries_obj = await generate_multi_queries(query)
    logger.info(f"[MILVUS SEARCH] Generated queries: {queries_obj.queries}")

    for q in queries_obj.queries:
        results = await interface.hybrid_search(
            collection_name=collection_name,
            query=q,
            party=party,
            year=year
        )
        if results and len(results) > 0:
            all_chunks.extend([hit['entity'] for hit in results[0]])

    chunk_counts = Counter(chunk['id'] for chunk in all_chunks)

    id_to_chunk = {chunk['id']: chunk for chunk in all_chunks}
    most_frequent_ids = [item[0] for item in chunk_counts.most_common(TOP_K)]

    final_selection = [id_to_chunk[cid] for cid in most_frequent_ids]

    if not final_selection:
        logger.warning(f"[MILVUS SEARCH] No results found for query: {query}")
        return "<context>\n</context>"

    logger.info(
        f"[MILVUS SEARCH] Collected {len(all_chunks)} total hits. Reduced to {len(final_selection)} unique high-confidence chunks.")

    context = "<context>\n"
    for idx, chunk in enumerate(final_selection):
        context += (
        f"<document>\n"
        f"<year>\n{chunk['year']}\n</year>\n"
        f"<party>\n{chunk['party']}\n</party>\n"
        f"<page_number>\n{chunk['page_number']}\n</page_number>\n"
        f"<metadata>\n{chunk['metadata']}\n</metadata>\n"
        f"<content>\n{chunk['content']}\n</content>\n"
        f"</document>\n")
        if idx == 0:
            logger.info(f"Most relevant chunk: {context}")
    context += "</context>\n"
    return context[:CONTEXT_MAX_LEN]

if __name__ == "__main__":
    async def main():
        query = "Financování televize a rozhlasu by už nemělo být plošnou zátěží pro peněženky občanů formou povinných plateb."
        queries = await generate_multi_queries(query)
        print(queries)
    import asyncio
    asyncio.run(main())