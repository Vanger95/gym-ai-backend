from pathlib import Path


class TXTParser:
    def extract_text(self, file_path: str) -> str:
        return Path(file_path).read_text(
            encoding="utf-8",
            errors="ignore",
        )