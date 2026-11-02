from pathlib import Path


class MarkItDownConverter:
    """Convert supported office and document formats to Markdown locally."""

    def __init__(self):
        try:
            from markitdown import MarkItDown
        except ImportError as exc:
            raise RuntimeError(
                "Engine MarkItDown belum terpasang. Jalankan: "
                ".venv\\Scripts\\python.exe -m pip install -r requirements-converter.txt"
            ) from exc
        self.engine = MarkItDown()

    def convert_to_markdown(self, source, output_dir):
        source = Path(source)
        output_dir = Path(output_dir)
        if not source.is_file():
            raise FileNotFoundError(source)
        output_dir.mkdir(parents=True, exist_ok=True)
        result = self.engine.convert(str(source))
        content = result.text_content or ""
        if not content.strip():
            raise RuntimeError(f"Tidak ada teks yang berhasil diekstrak dari {source.name}.")
        target = self._unique_path(output_dir, source.stem, ".md")
        target.write_text(content, encoding="utf-8")
        return target

    @staticmethod
    def _unique_path(folder, stem, suffix):
        target = folder / f"{stem}{suffix}"
        index = 1
        while target.exists():
            target = folder / f"{stem}_{index}{suffix}"
            index += 1
        return target
