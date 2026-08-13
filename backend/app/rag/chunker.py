"""Simple, dependency-light recursive chunker (paragraph -> line -> word boundaries)."""

from app.core.config import get_settings


def _split_on_separator(text: str, separator: str, chunk_size: int) -> list[str]:
    if separator:
        pieces = text.split(separator)
    else:
        pieces = list(text)

    chunks, current = [], ""
    for piece in pieces:
        candidate = current + (separator if current else "") + piece
        if len(candidate) <= chunk_size:
            current = candidate
        else:
            if current:
                chunks.append(current)
            current = piece
    if current:
        chunks.append(current)
    return chunks


def chunk_text(text: str, chunk_size: int | None = None, chunk_overlap: int | None = None) -> list[str]:
    """
    Recursively split `text` trying paragraph, then line, then word
    boundaries, so no chunk exceeds `chunk_size` characters. Adds
    `chunk_overlap` characters of trailing context from the previous chunk
    to each subsequent chunk to preserve context across chunk boundaries.
    """
    settings = get_settings()
    chunk_size = chunk_size or settings.chunk_size
    chunk_overlap = chunk_overlap or settings.chunk_overlap

    text = text.strip()
    if not text:
        return []
    if len(text) <= chunk_size:
        return [text]

    for separator in ["\n\n", "\n", ". ", " "]:
        pieces = _split_on_separator(text, separator, chunk_size)
        if all(len(p) <= chunk_size for p in pieces):
            break
    else:
        pieces = [text[i : i + chunk_size] for i in range(0, len(text), chunk_size)]

    # Apply overlap: prepend the tail of the previous chunk to the next one.
    overlapped: list[str] = []
    for i, piece in enumerate(pieces):
        piece = piece.strip()
        if not piece:
            continue
        if i > 0 and chunk_overlap > 0 and overlapped:
            tail = overlapped[-1][-chunk_overlap:]
            piece = f"{tail} {piece}"
        overlapped.append(piece)

    return overlapped
