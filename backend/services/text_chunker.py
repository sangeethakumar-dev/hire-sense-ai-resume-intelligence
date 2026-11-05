
import re


def chunk_text(
    text: str,
    chunk_size: int = 180,
    overlap: int = 30
) -> list[str]:
    """
    Split extracted text into overlapping word-based chunks.
    """

    if not text or not text.strip():
        raise ValueError("Input text cannot be empty.")

    if chunk_size <= 0:
        raise ValueError("Chunk size must be greater than zero.")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("Overlap must be smaller than chunk size.")

    # Clean unnecessary whitespace
    text = re.sub(r"\s+", " ", text).strip()

    words = text.split()

    chunks = []
    start = 0

    while start < len(words):

        end = start + chunk_size

        chunk = " ".join(words[start:end])

        if chunk.strip():
            chunks.append(chunk)

        if end >= len(words):
            break

        start = end - overlap

    return chunks
