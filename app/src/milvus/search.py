from typing import Dict, List
from collections import Counter

from app.src.clients.openai_client import Client
from app.src.milvus.milvus_interface import MilvusInterface
from pydantic import BaseModel

MODEL = "gpt-5-mini"
CONTEXT_MAX_LEN = 70000
TOP_K = 20

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
    queries = client.get_structured_response(messages, schema=Queries, model=MODEL)
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

    interface = kwargs.get("interface", MilvusInterface())
    year = kwargs.get("year", None)
    party = kwargs.get("party", None)

    all_chunks = []
    queries_obj = await generate_multi_queries(query)

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
        print(f"[MILVUS SEARCH] No results found for query: {query}")
        return "<context>\n</context>"

    print(
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
            print(f"Most relevant chunk: {context}")
    context += "</context>\n"
    return context[:CONTEXT_MAX_LEN]