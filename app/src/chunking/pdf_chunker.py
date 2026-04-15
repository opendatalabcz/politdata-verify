"""
pdf chunker module
"""
import uuid
from typing import List
import tiktoken
from pydantic import HttpUrl

from app.src.chunking.enrichment import ContextEnricher
from app.src.chunking.models import Chunk
from app.src.chunking.utils import extract_spans_with_sizes, detect_headings, group_blocks, download_pdf_to_tmp
from app.src.embeddings.jina_client import JinaEmbedder
from app.src.milvus.milvus_interface import MilvusInterface

tokenizer = tiktoken.get_encoding("cl100k_base")  # Jina/OpenAI compatible

def chunk_heading_aware(blocks, max_tokens=400, overlap_tokens=80) -> List[dict]:
    """
    Chunks text based on pre-grouped blocks from utils.py.
    Each block in 'blocks' is considered a semantic unit (Heading + Body).
    We treat these as hard boundaries (we do not merge separate blocks),
    but we split them internally if they exceed max_tokens.
    """
    chunks = []

    def token_len(text):
        return len(tokenizer.encode(text))

    for blk in blocks:
        block_text = blk["text"].strip()
        pages = blk.get("pages", [])
        start_page = pages[0] if pages else None

        if token_len(block_text) <= max_tokens:
            if block_text:
                chunks.append({
                    "text": block_text,
                    "page": start_page
                })
        else:
            words = block_text.split()
            current_chunk_words = []
            current_len = 0

            for word in words:
                word_len = token_len(word + " ")

                if current_len + word_len > max_tokens:
                    chunk_text = " ".join(current_chunk_words)
                    chunks.append({
                        "text": chunk_text,
                        "page": start_page
                    })

                    overlap_count = max(1, int(len(current_chunk_words) * (overlap_tokens / max_tokens)))
                    current_chunk_words = current_chunk_words[-overlap_count:]
                    current_len = token_len(" ".join(current_chunk_words) + " ")

                current_chunk_words.append(word)
                current_len += word_len

            if current_chunk_words:
                chunks.append({
                    "text": " ".join(current_chunk_words),
                    "page": start_page
                })

    return chunks

async def pdf_chunker(url: HttpUrl, document_name: str, party: str, year: int) -> List[Chunk]:
    """
    Chunk a PDF into text chunks.
    :param url:
    :return:
    """
    embedder = JinaEmbedder()
    tmp_path = await download_pdf_to_tmp(HttpUrl(url))
    spans = extract_spans_with_sizes(tmp_path)

    # Extract global context using LLM for embedding enrichment
    enricher = ContextEnricher()
    raw_text = " ".join([s["text"] for s in spans])
    global_ctx = enricher.extract_context(raw_text)
    context_prefix = global_ctx.to_context_string()
    print(f"Detected: {context_prefix}")

    spans = detect_headings(spans)
    blocks = group_blocks(spans)
    chunks = chunk_heading_aware(blocks)

    # Generate embeddings for each chunk with context prefix
    texts = [chunk["text"] for chunk in chunks]
    texts_to_embed = [context_prefix + t for t in texts]
    embeddings = await embedder.get_embeddings_batch_jina(texts_to_embed, "retrieval.passage")
    final_chunks = [
        Chunk(
            id = uuid.uuid4(),
            doc_name = document_name,
            party = party,
            page_number = chunk["page"],
            year = year,
            content=chunk["text"],
            dense_vector=embeddings[i],
            summary=context_prefix,
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
        name = "Volební program 2025"
        party = "Starostové a nezávislí"
        year = 2025
        url_auto = "https://36beec02.delivery.rocketcdn.me/wp-content/uploads/Volebni_program-2025_MOTORISTE-SOBE.pdf"
        url_spd = "https://spd.cz/wp-content/uploads/2025/09/Program-SPD-pro-volby-do-Poslanecke-snemovny-2025.pdf"
        url_pirati = "https://majak.pirati.cz/documents/506/PROGRAM_PIRATU_2025.pdf"
        url = "https://www.starostove.cz/files/dobry-program-starostove.pdf"  # Replace with your PDF path
        chunks = await pdf_chunker(url, name, party, year)
        for i, chunk in enumerate(chunks):
            print(f"--- Chunk {i+1} ---")
            print(chunk.content)
            print()
        # tmp_path = await download_pdf_to_tmp(HttpUrl(url))
        # enricher = ContextEnricher()
        # spans = extract_spans_with_sizes(tmp_path)
        # raw_text = " ".join([s["text"] for s in spans])
        # global_ctx = enricher.extract_context(raw_text)
        # context_prefix = global_ctx.to_context_string()
        # print(f"Detected: {context_prefix}")


        interface = MilvusInterface()
        collection_name= "test_collection"
        await interface.insert_chunks(collection_name, chunks)
        # await interface.drop_collection(collection_name)
        # query = "Jaké jsou priority v dopravě?"
        # result = await interface.hybrid_search(collection_name, query)
        # for res in result:
        #     print(res)


    asyncio.run(main())

