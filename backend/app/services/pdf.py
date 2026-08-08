import io
import logging
import re
from dataclasses import dataclass

from pypdf import PdfReader

logger = logging.getLogger(__name__)


@dataclass
class PageText:
    page_number: int
    text: str


@dataclass
class PdfMetadata:
    page_count: int
    author: str | None
    pages: list[PageText]


def _clean_page(text: str) -> str:
    text = text.replace("\x00", " ").replace("\r", "\n")
    lines = [re.sub(r"\s+", " ", line).strip() for line in text.splitlines()]
    lines = [line for line in lines if line]
    if len(lines) >= 4:
        counts: dict[str, int] = {}
        for line in lines:
            counts[line] = counts.get(line, 0) + 1
        repeated = {line for line, count in counts.items() if count >= 2 and len(line) < 180}
        lines = [line for line in lines if line not in repeated]
    return "\n".join(lines).strip()


def extract_pdf(content: bytes) -> PdfMetadata:
    try:
        reader = PdfReader(io.BytesIO(content))
        pages = [PageText(index + 1, _clean_page(page.extract_text() or "")) for index, page in enumerate(reader.pages)]
        if not any(page.text for page in pages):
            raise ValueError("This PDF contains no extractable text. It may be scanned; OCR is required before ingestion.")
        metadata = reader.metadata or {}
        author = metadata.get("/Author") if metadata else None
        return PdfMetadata(len(reader.pages), str(author) if author else None, pages)
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("PDF extraction failed")
        raise ValueError(f"Unable to read PDF: {exc}") from exc


def split_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> list[str]:
    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")
    separators = ["\n\n", "\n", ". ", " ", ""]

    def recursive(value: str, limit: int) -> list[str]:
        if len(value) <= limit:
            return [value.strip()] if value.strip() else []
        for separator in separators:
            if separator and separator in value:
                pieces = value.split(separator)
                result: list[str] = []
                current = ""
                for piece in pieces:
                    candidate = f"{current}{separator}{piece}" if current else piece
                    if len(candidate) <= limit:
                        current = candidate
                    else:
                        if current.strip():
                            result.extend(recursive(current.strip(), limit))
                        current = piece
                if current.strip():
                    result.extend(recursive(current.strip(), limit))
                return result
        return [value[index:index + limit].strip() for index in range(0, len(value), limit)]

    # Build slightly smaller base pieces, then prepend the previous tail. This
    # preserves overlap without ever returning a chunk larger than chunk_size.
    base_limit = chunk_size - overlap - 1 if overlap else chunk_size
    chunks = recursive(text, max(1, base_limit))
    if overlap and len(chunks) > 1:
        result = [chunks[0]]
        for chunk in chunks[1:]:
            prefix = result[-1][-overlap:]
            result.append(f"{prefix} {chunk}".strip())
        return result
    return chunks
