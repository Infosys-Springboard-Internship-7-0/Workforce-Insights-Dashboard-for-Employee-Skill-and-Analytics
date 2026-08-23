from io import BytesIO
from pathlib import Path
import pandas as pd
import fitz
from docx import Document as DocxDocument


def extract_document(file_bytes: bytes, filename: str) -> list[tuple[str, int | None]]:
    suffix = Path(filename).suffix.lower()

    if suffix == ".pdf":
        pdf = fitz.open(stream=file_bytes, filetype="pdf")
        return [
            (page.get_text("text"), index + 1)
            for index, page in enumerate(pdf)
            if page.get_text("text").strip()
        ]

    if suffix == ".docx":
        doc = DocxDocument(BytesIO(file_bytes))
        text = "\n".join(p.text for p in doc.paragraphs if p.text.strip())
        return [(text, None)]

    if suffix == ".txt":
        return [(file_bytes.decode("utf-8", errors="ignore"), None)]

    if suffix == ".csv":
        df = pd.read_csv(BytesIO(file_bytes))
        return [(df.to_csv(index=False), None)]

    raise ValueError("Supported formats: PDF, DOCX, TXT, CSV")
