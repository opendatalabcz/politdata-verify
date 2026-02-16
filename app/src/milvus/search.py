from typing import Dict, List

from app.src.milvus.milvus_interface import MilvusInterface
CONTEXT_MAX_LEN = 70000

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

    # search Milvus
    results = await interface.hybrid_search(
        collection_name=collection_name,
        query=query,
        party=party,
        year=year
    )
    extracted_entities = [result['entity'] for result in results[0]]

    if len(extracted_entities) == 0:
        print(f"[MILVUS SEARCH] No results found in collection {collection_name} for query: {query}")
    else:
        print(f"[MILVUS SEARCH] Found {len(extracted_entities)} results in collection {collection_name} for query: {query}")

    context = "<context>\n"
    for idx, chunk in enumerate(extracted_entities):
        print(f"RANK {idx + 1} | Page: {chunk['page_number']} | Content: {chunk['content'][:100]}...")
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