"""
utils
"""
import httpx
import tempfile
import os
import fitz  # PyMuPDF
import numpy as np

from pydantic import HttpUrl

async def download_pdf_to_tmp(url: HttpUrl) -> str:
    """Download a PDF from URL to a temporary file and return its path."""
    async with httpx.AsyncClient(follow_redirects=True, timeout=60.0) as client:
        resp = await client.get(str(url))
        resp.raise_for_status()

    if not resp.content.startswith(b"%PDF"):
        raise ValueError("Downloaded file is not a valid PDF")

    fd, tmp_path = tempfile.mkstemp(suffix=".pdf")
    os.close(fd)
    with open(tmp_path, "wb") as f:
        f.write(resp.content)
    return tmp_path

def extract_spans_with_sizes(pdf_path):
    doc = fitz.open(pdf_path)
    spans = []

    for page_num, page in enumerate(doc, start=1):
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    spans.append({
                        "text": span["text"],
                        "size": span["size"],        # REAL font size
                        "bbox": span["bbox"],
                        "page": page_num
                    })
    spans.sort(key=lambda s: (s["page"], s["bbox"][1], s["bbox"][0]))
    return spans

def detect_headings(spans):
    sizes = [s["size"] for s in spans]
    median = np.median(sizes)
    threshold = median * 1.3          # 30% larger than typical text

    for s in spans:
        s["is_heading"] = s["size"] >= threshold

    return spans

def group_blocks(spans):
    blocks = []
    current = {"text": "", "is_heading": False, "page": None}

    for s in spans:
        if current["text"] == "":
            current["page"] = s["page"]
            current["is_heading"] = s["is_heading"]

        # If heading changes, start new block
        if s["is_heading"] != current["is_heading"]:
            blocks.append(current)
            current = {"text": "", "is_heading": s["is_heading"], "page": s["page"]}

        current["text"] += s["text"] + " "

    if current["text"]:
        blocks.append(current)

    return blocks

if __name__ == "__main__":
    import asyncio

    async def main():
        url = "https://majak.pirati.cz/documents/506/PROGRAM_PIRATU_2025.pdf"  # Replace with a valid PDF URL
        tmp_path = await download_pdf_to_tmp(HttpUrl(url))
        spans = extract_spans_with_sizes(tmp_path)
        spans = detect_headings(spans)
        for span in spans:
            if span["is_heading"]:
                print(f"Heading (size {span['size']}): {span['text']}")
            else:
                print(f"Text (size {span['size']}): {span['text']}")
        blocks = group_blocks(spans)
        for block in blocks:
            heading_flag = "Heading" if block["is_heading"] else "Text"
            print(f"\n[{heading_flag} - Page {block['page']}]:\n{block['text']}")

        os.remove(tmp_path)

    asyncio.run(main())