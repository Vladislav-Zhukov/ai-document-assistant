from io import BytesIO

from docx import Document as DocxDocument
from pypdf import PdfReader


class DocumentParser:
    def parse(self, file_bytes: bytes, filename: str) -> str:
        filename_lower = filename.lower()

        if filename_lower.endswith(".pdf"):
            return self._parse_pdf(file_bytes)

        if filename_lower.endswith(".docx"):
            return self._parse_docx(file_bytes)

        if filename_lower.endswith(".txt"):
            return self._parse_txt(file_bytes)

        raise ValueError("Unsupported file type")

    def _parse_pdf(self, file_bytes: bytes) -> str:
        reader = PdfReader(BytesIO(file_bytes))
        pages_text = []

        for page in reader.pages:
            text = page.extract_text() or ""
            pages_text.append(text)

        return "\n".join(pages_text)

    def _parse_docx(self, file_bytes: bytes) -> str:
        document = DocxDocument(BytesIO(file_bytes))
        paragraphs = [p.text for p in document.paragraphs if p.text.strip()]
        return "\n".join(paragraphs)

    def _parse_txt(self, file_bytes: bytes) -> str:
        return file_bytes.decode("utf-8", errors="ignore")