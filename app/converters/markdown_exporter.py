from __future__ import annotations

from html import escape
from html.parser import HTMLParser
from pathlib import Path
import re

import markdown


def _unique_path(folder: Path, stem: str, suffix: str) -> Path:
    target = folder / f"{stem}{suffix}"
    index = 1
    while target.exists():
        target = folder / f"{stem}_{index}{suffix}"
        index += 1
    return target


def _read_markdown(source: Path) -> str:
    if not source.is_file():
        raise FileNotFoundError(source)
    return source.read_text(encoding="utf-8-sig")


def _render_html(markdown_text: str, title: str) -> str:
    body = markdown.markdown(
        markdown_text,
        extensions=["tables", "fenced_code", "sane_lists"],
        output_format="html5",
    )
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(title)}</title>
<style>
body {{ max-width: 900px; margin: 40px auto; padding: 0 28px;
       color: #202824; font: 11pt/1.65 'Segoe UI', Arial, sans-serif; }}
h1,h2,h3,h4 {{ color: #183b2d; line-height: 1.25; }}
h1 {{ border-bottom: 2px solid #32b982; padding-bottom: 10px; }}
pre {{ background: #f2f5f3; padding: 14px; border-radius: 7px;
       white-space: pre-wrap; overflow-wrap: anywhere; }}
code {{ font-family: Consolas, monospace; }}
blockquote {{ border-left: 4px solid #32b982; margin-left: 0;
              padding: 4px 16px; color: #52645a; }}
table {{ border-collapse: collapse; width: 100%; }}
th,td {{ border: 1px solid #ccd5cf; padding: 7px; text-align: left; }}
img {{ max-width: 100%; }}
a {{ color: #16764d; }}
</style>
</head>
<body>{body}</body>
</html>"""


class _PlainTextExtractor(HTMLParser):
    BLOCKS = {"p", "div", "h1", "h2", "h3", "h4", "h5", "h6",
              "li", "tr", "blockquote", "pre", "br"}

    def __init__(self):
        super().__init__()
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag in self.BLOCKS:
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in self.BLOCKS:
            self.parts.append("\n")

    def handle_data(self, data):
        self.parts.append(data)

    def text(self):
        raw = "".join(self.parts)
        lines = [re.sub(r"[ \t]+", " ", line).strip() for line in raw.splitlines()]
        return "\n".join(line for line in lines if line).strip() + "\n"


class _DocxWriter(HTMLParser):
    """Small HTML-to-DOCX writer for Markdown headings, paragraphs and lists."""

    def __init__(self, document):
        super().__init__()
        self.document = document
        self.paragraph = None
        self.bold = False
        self.italic = False
        self.code = False
        self.list_stack = []
        self.in_pre = False
        self.pre_text = []

    def _new_paragraph(self, style=None):
        self.paragraph = self.document.add_paragraph(style=style)

    def handle_starttag(self, tag, attrs):
        if tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            self._new_paragraph(f"Heading {min(int(tag[1]), 3)}")
        elif tag == "p":
            self._new_paragraph()
        elif tag in {"ul", "ol"}:
            self.list_stack.append("bullet" if tag == "ul" else "number")
        elif tag == "li":
            style = "List Bullet" if self.list_stack and self.list_stack[-1] == "bullet" else "List Number"
            self._new_paragraph(style)
        elif tag == "strong" or tag == "b":
            self.bold = True
        elif tag in {"em", "i"}:
            self.italic = True
        elif tag == "code":
            self.code = True
        elif tag == "pre":
            self.in_pre = True
            self.pre_text = []
        elif tag == "br" and self.paragraph is not None:
            self.paragraph.add_run().add_break()

    def handle_endtag(self, tag):
        if tag in {"ul", "ol"} and self.list_stack:
            self.list_stack.pop()
        elif tag in {"strong", "b"}:
            self.bold = False
        elif tag in {"em", "i"}:
            self.italic = False
        elif tag == "code":
            self.code = False
        elif tag == "pre":
            text = "".join(self.pre_text).rstrip()
            p = self.document.add_paragraph()
            run = p.add_run(text)
            run.font.name = "Consolas"
            self.in_pre = False
        elif tag in {"p", "li", "h1", "h2", "h3", "h4", "h5", "h6"}:
            self.paragraph = None

    def handle_data(self, data):
        if self.in_pre:
            self.pre_text.append(data)
            return
        if self.paragraph is None:
            if not data.strip():
                return
            self._new_paragraph()
        run = self.paragraph.add_run(data)
        run.bold = self.bold
        run.italic = self.italic
        if self.code:
            run.font.name = "Consolas"


def _to_docx(html: str, destination: Path):
    try:
        from docx import Document
    except ImportError as exc:
        raise RuntimeError(
            "Ekspor Word membutuhkan python-docx. Jalankan: "
            "python -m pip install python-docx"
        ) from exc

    document = Document()
    parser = _DocxWriter(document)
    parser.feed(html)
    document.save(str(destination))


def _to_pdf(html: str, destination: Path):
    # Qt's HTML document renderer is already part of the application's PySide6 stack.
    from PySide6.QtGui import QTextDocument
    from PySide6.QtPrintSupport import QPrinter

    printer = QPrinter(QPrinter.HighResolution)
    printer.setOutputFormat(QPrinter.PdfFormat)
    printer.setOutputFileName(str(destination))
    document = QTextDocument()
    document.setHtml(html)
    document.print(printer)


def convert_markdown_files(files, target_format: str, output_dir):
    output = Path(output_dir).expanduser()
    output.mkdir(parents=True, exist_ok=True)

    suffixes = {
        "PDF": ".pdf",
        "Word (DOCX)": ".docx",
        "HTML": ".html",
        "TXT": ".txt",
    }
    if target_format not in suffixes:
        raise ValueError(f"Ekspor Markdown ke {target_format} belum didukung.")

    results = []
    for raw_file in files:
        source = Path(raw_file)
        markdown_text = _read_markdown(source)
        html = _render_html(markdown_text, source.stem)
        target = _unique_path(output, source.stem, suffixes[target_format])

        if target_format == "HTML":
            target.write_text(html, encoding="utf-8")
        elif target_format == "TXT":
            parser = _PlainTextExtractor()
            parser.feed(markdown.markdown(
                markdown_text,
                extensions=["tables", "fenced_code", "sane_lists"],
            ))
            target.write_text(parser.text(), encoding="utf-8")
        elif target_format == "Word (DOCX)":
            _to_docx(html, target)
        elif target_format == "PDF":
            _to_pdf(html, target)

        results.append(target)

    return results
