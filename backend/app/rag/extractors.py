"""
Text extraction for uploaded documents: PDF, DOCX, TXT, CSV.

CSV files are flattened into readable "row text" (one line per row, with
column headers) so they're embeddable/searchable like any other document,
in addition to being served as structured table data by the Data Viewer.
"""

from pathlib import Path


class ExtractionError(Exception):
    """Raised when a document's text cannot be extracted."""


def extract_pdf(path: Path) -> str:
    from pypdf import PdfReader

    try:
        reader = PdfReader(str(path))
    except Exception as exc:
        raise ExtractionError(f"Could not open PDF '{path.name}': {exc}") from exc

    pages = [page.extract_text() or "" for page in reader.pages]
    text = "\n\n".join(p for p in pages if p.strip())
    if not text.strip():
        raise ExtractionError(f"PDF '{path.name}' has no extractable text (possibly scanned/image-only).")
    return text


def extract_docx(path: Path) -> str:
    import docx

    try:
        document = docx.Document(str(path))
    except Exception as exc:
        raise ExtractionError(f"Could not open DOCX '{path.name}': {exc}") from exc

    paragraphs = [p.text for p in document.paragraphs if p.text.strip()]
    if not paragraphs:
        raise ExtractionError(f"DOCX '{path.name}' has no extractable text.")
    return "\n".join(paragraphs)


def extract_txt(path: Path) -> str:
    try:
        text = path.read_text(encoding="utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise ExtractionError(f"TXT '{path.name}' is not valid UTF-8: {exc}") from exc
    if not text.strip():
        raise ExtractionError(f"TXT '{path.name}' is empty.")
    return text


def extract_csv(path: Path) -> str:
    import pandas as pd

    try:
        df = pd.read_csv(path)
    except Exception as exc:
        raise ExtractionError(f"Could not parse CSV '{path.name}': {exc}") from exc

    if df.empty:
        raise ExtractionError(f"CSV '{path.name}' has no rows.")

    columns = ", ".join(df.columns.astype(str))
    lines = [f"Columns: {columns}"]
    for _, row in df.iterrows():
        row_text = "; ".join(f"{col}: {row[col]}" for col in df.columns)
        lines.append(row_text)
    return "\n".join(lines)


_EXTRACTORS = {".pdf": extract_pdf, ".docx": extract_docx, ".txt": extract_txt, ".csv": extract_csv}


def extract_text(path: Path) -> str:
    suffix = path.suffix.lower()
    extractor = _EXTRACTORS.get(suffix)
    if extractor is None:
        raise ExtractionError(f"Unsupported file type '{suffix}'. Supported: PDF, DOCX, TXT, CSV.")
    return extractor(path)
