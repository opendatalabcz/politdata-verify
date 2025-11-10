"""
pdf chunker module
"""
import uuid
from typing import List
import tiktoken
from pydantic import HttpUrl

from src.chunking.models import Chunk
from src.chunking.utils import extract_spans_with_sizes, detect_headings, group_blocks, download_pdf_to_tmp
from src.embeddings.jina_client import JinaEmbedder
from src.milvus.milvus_interface import MilvusInterface

tokenizer = tiktoken.get_encoding("cl100k_base")  # Jina/OpenAI compatible

# TODO: improve chunking strategy
def chunk_heading_aware(blocks, max_tokens=400, overlap_tokens=40) -> List[dict]:
    chunks = []
    current_text = ""
    start_page = None

    def token_len(text):
        return len(tokenizer.encode(text))

    for blk in blocks:
        block_text = blk["text"].strip()
        page = blk.get("page")

        # Heading -> start new chunk
        if blk["is_heading"]:
            if current_text.strip():
                chunks.append({
                    "text": current_text.strip(),
                    "page": start_page
                })
            current_text = block_text + "\n"
            start_page = page
            continue

        # Check token limit
        if token_len(current_text + block_text) > max_tokens:
            chunks.append({
                "text": current_text.strip(),
                "page": start_page
            })

            overlap_text = current_text.split()[-overlap_tokens:]
            current_text = " ".join(overlap_text) + "\n"

            start_page = page

        if start_page is None:
            start_page = page

        current_text += block_text + "\n"

    if current_text.strip():
        chunks.append({
            "text": current_text.strip(),
            "page": start_page
        })

    return chunks

# TODO: change the function format
async def pdf_chunker(url: HttpUrl, document_name: str, party: str, year: int) -> List[Chunk]:
    """
    Chunk a PDF into text chunks.
    :param url:
    :return:
    """
    embedder = JinaEmbedder()
    tmp_path = await download_pdf_to_tmp(HttpUrl(url))
    spans = extract_spans_with_sizes(tmp_path)
    spans = detect_headings(spans)
    blocks = group_blocks(spans)
    chunks = chunk_heading_aware(blocks)
    texts = [chunk["text"] for chunk in chunks]
    embeddings = await embedder.get_embeddings_batch_jina(texts, "retrieval.passage")
    final_chunks = [
        Chunk(
            id = uuid.uuid4(),
            doc_name = document_name,
            party = party,
            page_number = chunk["page"],
            year = year,
            content=chunk["text"],
            dense_vector=embeddings[i],
            metadata={
                "source_url": str(url),
            }
        )
        for i, chunk in enumerate(chunks)
    ]

    return final_chunks


if __name__ == "__main__":
    import asyncio

    async def main():
        # name = "Volební program 2025"
        # party = "ANO 2011"
        # year = 2025
        # url = "https://www.anobudelip.cz/file/edee/ke-stazeni/volebni-program-2025.pdf"  # Replace with your PDF path
        # chunks = await pdf_chunker(url, name, party, year)
        # for i, chunk in enumerate(chunks):
        #     print(f"--- Chunk {i+1} ---")
        #     print(chunk.content)
        #     print()
        #
        interface = MilvusInterface()
        collection_name= "test_collection"
        # await interface.insert_chunks(collection_name, chunks)
        query = "Jaké jsou priority v dopravě?"
        result = await interface.hybrid_search(collection_name, query)
        for res in result:
            print(res)


    asyncio.run(main())

