"""
utils
"""
import httpx
import tempfile
import os
import fitz  # PyMuPDF
import numpy as np
import tiktoken

from pydantic import HttpUrl
PAGE_WIDTH_THRESHOLD = 800
COLUMN_BUCKET_WIDTH = 200

MARGIN_TOP = 0.05
MARGIN_BOTTOM = 0.05
MARGIN_LEFT = 0.05
MARGIN_RIGHT = 0.05

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


def sort_spans_layout(spans):
    return sorted(
        spans,
        key=lambda b: (int(b["bbox"][0] / COLUMN_BUCKET_WIDTH), b["bbox"][1], b["bbox"][0])
    )

def extract_spans_with_sizes(pdf_path):
    doc = fitz.open(pdf_path)
    all_spans = []

    for page_num, page in enumerate(doc, start=1):
        height = page.rect.height
        width = page.rect.width
        is_double_page = width > PAGE_WIDTH_THRESHOLD

        zones = []
        if is_double_page:
            zones.append({"rect": fitz.Rect(0, 0, width / 2, height), "page_offset": 0})
            zones.append({"rect": fitz.Rect(width / 2, 0, width, height), "page_offset": 1})
        else:
            zones.append({"rect": page.rect, "page_offset": 0})

        for zone in zones:
            z_rect = zone["rect"]
            z_width = z_rect.width
            z_height = z_rect.height

            # margins
            limit_top = z_rect.y0 + (z_height * MARGIN_TOP)
            limit_bottom = z_rect.y0 + (z_height * (1 - MARGIN_BOTTOM))
            limit_left = z_rect.x0 + (z_width * MARGIN_LEFT)
            limit_right = z_rect.x0 + (z_width * (1 - MARGIN_RIGHT))

            page_dict = page.get_text("dict", clip=z_rect)

            raw_spans = []

            for block in page_dict.get("blocks", []):
                if block["type"] != 0:  # text block
                    continue

                for line in block["lines"]:
                    for span in line["spans"]:
                        x0, y0, x1, y1 = span["bbox"]
                        text = span["text"]

                        # Crop
                        if y1 < limit_top: continue
                        if y0 > limit_bottom: continue
                        if x1 < limit_left: continue
                        if x0 > limit_right: continue
                        if not text.strip(): continue
                        if text.strip().isdigit(): continue

                        raw_spans.append({
                            "text": text.strip(),
                            "size": span["size"],
                            "bbox": span["bbox"],
                            "page": page_num + zone["page_offset"],
                            "line_start": x0 <= limit_left + 5  # small tolerance
                        })

            sorted_spans = sort_spans_layout(raw_spans)
            all_spans.extend(sorted_spans)

    return all_spans

def detect_headings(spans):
    sizes = [s["size"] for s in spans]
    median = np.median(sizes)
    threshold = median * 1.2

    for s in spans:
        s["is_heading"] = s["size"] >= threshold

    return spans

def group_blocks(spans):
    blocks = []
    current_block = None
    heading = False
    for span in spans:
        if current_block is None:
            current_block = {
                "text": span["text"],
                "pages": [span["page"]]
            }
        else:
            if not heading:
                if span["is_heading"]:
                    # Start new heading block
                    blocks.append(current_block)
                    current_block = {
                        "text": span["text"],
                        "pages": [span["page"]]
                    }
                    heading = True
                else:
                    current_block["text"] += "\n" + span["text"]
                    if span["page"] not in current_block["pages"]:
                        current_block["pages"].append(span["page"])
            else:
                if span["is_heading"]:
                    # Continue current heading block
                    current_block["text"] += "\n" + span["text"]
                    if span["page"] not in current_block["pages"]:
                        current_block["pages"].append(span["page"])
                else:
                    current_block["text"] += "\n" + span["text"]
                    if span["page"] not in current_block["pages"]:
                        current_block["pages"].append(span["page"])
                    heading = False
    if current_block is not None:
        blocks.append(current_block)
    return blocks

def get_stats(path):
    doc = fitz.open(path)
    tokenizer = tiktoken.get_encoding("cl100k_base")  # GPT-4o encoding

    total_chars = 0
    total_tokens = 0
    num_pages = len(doc)

    for page in doc:
        text = page.get_text()
        total_chars += len(text)
        total_tokens += len(tokenizer.encode(text))

    return {
        "pages": num_pages,
        "characters": total_chars,
        "tokens": total_tokens,
    }

if __name__ == "__main__":
    import asyncio

    async def main():
        urls = {
            "SPD": "https://spd.cz/wp-content/uploads/2025/09/Program-SPD-pro-volby-do-Poslanecke-snemovny-2025.pdf",
            "ANO": "https://www.anobudelip.cz/file/edee/ke-stazeni/volebni-program-2025.pdf",
            "Auto": "https://36beec02.delivery.rocketcdn.me/wp-content/uploads/Volebni_program-2025_MOTORISTE-SOBE.pdf",
            "STAN": "https://www.starostove.cz/files/dobry-program-starostove.pdf",
            "Pirati": "https://majak.pirati.cz/documents/506/PROGRAM_PIRATU_2025.pdf",
            "Spolu": "https://spolu25.cz/pdf/SPOLU-program-2025.pdf"
        }
        tmp_path = await download_pdf_to_tmp(HttpUrl(urls["SPD"]))
        data = get_stats(tmp_path)
        print(data)

        from pypdf import PdfReader
        import io
        import requests

        for party, url in urls.items():
            response = requests.get(url)
            with io.BytesIO(response.content) as f:
                reader = PdfReader(f)
                meta = reader.metadata
                print(f"\n--- {party} ---")
                print("Vytvořeno:", meta.creation_date)
                print("Upraveno:", meta.modification_date)
        # spans = extract_spans_with_sizes(tmp_path)
        # spans = detect_headings(spans)
        # for span in spans:
        #     if span["is_heading"]:
        #         print(f"Heading (size {span['size']}): {span['text']}")
        #     else:
        #         print(f"Text (size {span['size']}): {span['text']}")
        # blocks = group_blocks(spans)
        # for block in blocks:
        #     print(f"Block (pages {block['pages']}): {block['text']}")
        #

        # spans = extract_spans_with_sizes(tmp_path)
        # spans = detect_headings(spans)
        # for span in spans:
        #     if span["is_heading"]:
        #         print(f"Heading (size {span['size']}): {span['text']}")
        #     else:
        #         print(f"Text (size {span['size']}): {span['text']}")
        # blocks = group_blocks(spans)
        # for block in blocks:
        #     heading_flag = "Heading" if block["is_heading"] else "Text"
        #     print(f"\n[{heading_flag} - Page {block['page']}]:\n{block['text']}")

        os.remove(tmp_path)

    asyncio.run(main())