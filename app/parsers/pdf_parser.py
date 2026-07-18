from pathlib import Path

from pypdf import PdfReader


class PDFParser:
    def extract_text(self, file_path: str) -> str:
        reader = PdfReader(Path(file_path))

        pages: list[str] = []

        for page in reader.pages:
            text = page.extract_text()

            if text:
                pages.append(text.strip())

        return "\n\n".join(pages)