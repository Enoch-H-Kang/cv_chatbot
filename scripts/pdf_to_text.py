#!/usr/bin/env python3
"""
pdf_to_text.py — convert a folder of PDF papers into the .txt files this
chatbot indexes.

The RAG pipeline only reads .txt files from src/data/. This script turns your
PDFs into that format. It tries the `pypdf` library first (pure Python, no
system dependency); if a PDF is scanned (image-only), it will warn you.

Usage:
    pip install pypdf
    python scripts/pdf_to_text.py path/to/pdfs/ src/data/

If a paper is a scanned image, run OCR instead, e.g. with `ocrmypdf`:
    ocrmypdf input.pdf output.pdf && pdftotext output.pdf src/data/paper.txt
"""

import sys
import re
from pathlib import Path

try:
    from pypdf import PdfReader
except ImportError:
    print("Missing dependency. Install it with:  pip install pypdf")
    sys.exit(1)


def slugify(name: str) -> str:
    """Make a filesystem-friendly stem from a PDF filename."""
    stem = Path(name).stem.lower()
    stem = re.sub(r"[^a-z0-9]+", "_", stem).strip("_")
    return stem or "paper"


def convert(pdf_path: Path, out_dir: Path) -> None:
    reader = PdfReader(str(pdf_path))
    pages = []
    for page in reader.pages:
        text = page.extract_text() or ""
        pages.append(text)
    full_text = "\n\n".join(pages).strip()

    if len(full_text) < 100:
        print(f"  ⚠️  '{pdf_path.name}' yielded almost no text. "
              f"It may be a scanned image — run OCR first.")

    out_path = out_dir / f"{slugify(pdf_path.name)}.txt"
    out_path.write_text(full_text, encoding="utf-8")
    print(f"  ✅ {pdf_path.name}  ->  {out_path}  ({len(full_text):,} chars)")


def main() -> None:
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)

    in_dir = Path(sys.argv[1])
    out_dir = Path(sys.argv[2])
    out_dir.mkdir(parents=True, exist_ok=True)

    pdfs = sorted(in_dir.glob("*.pdf"))
    if not pdfs:
        print(f"No PDFs found in {in_dir}")
        sys.exit(1)

    print(f"Converting {len(pdfs)} PDF(s) from {in_dir} into {out_dir}:")
    for pdf in pdfs:
        try:
            convert(pdf, out_dir)
        except Exception as e:  # noqa: BLE001
            print(f"  ❌ Failed on {pdf.name}: {e}")

    print("\nDone. Review the .txt files, then commit them to src/data/.")


if __name__ == "__main__":
    main()
