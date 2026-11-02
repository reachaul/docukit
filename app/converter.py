from pathlib import Path
from markitdown import MarkItDown


class DocumentConverter:
    """
    Convert documents to Markdown using MarkItDown.
    For scanned PDFs with little/no extractable text, use Tesseract OCR.
    """

    MIN_PDF_TEXT_LENGTH = 80
    OCR_LANGUAGES = "ind+eng"
    OCR_DPI = 300

    def __init__(self):
        self.engine = MarkItDown()

    def convert(self, file_path, output_dir):
        source = Path(file_path)
        output = Path(output_dir)

        if not source.exists():
            raise FileNotFoundError(source)

        output.mkdir(parents=True, exist_ok=True)

        # Keep MarkItDown as the primary conversion engine.
        result = self.engine.convert(str(source))
        markdown_text = result.text_content or ""

        # OCR fallback is currently intended for scanned PDF documents.
        if source.suffix.lower() == ".pdf":
            if len(markdown_text.strip()) < self.MIN_PDF_TEXT_LENGTH:
                markdown_text = self._ocr_scanned_pdf(source)

        output_file = self._unique_output_path(output, source.stem)
        output_file.write_text(markdown_text, encoding="utf-8")

        return output_file

    @staticmethod
    def _unique_output_path(output_dir, stem):
        output_file = output_dir / f"{stem}.md"
        counter = 1

        while output_file.exists():
            output_file = output_dir / f"{stem}_{counter}.md"
            counter += 1

        return output_file

    def _ocr_scanned_pdf(self, pdf_path):
        """
        Render each PDF page and recognize text using Tesseract.
        Requires: pymupdf, pillow, pytesseract and the Tesseract program.
        """
        try:
            import pymupdf
            import pytesseract
            from PIL import Image
        except ImportError as error:
            raise RuntimeError(
                "PDF ini tampaknya berupa hasil scan dan membutuhkan OCR. "
                "Dependensi belum lengkap. Jalankan: "
                "pip install PyMuPDF Pillow pytesseract"
            ) from error

        try:
            document = pymupdf.open(str(pdf_path))
        except Exception as error:
            raise RuntimeError(f"Tidak dapat membuka PDF untuk OCR: {error}") from error

        pages = []

        try:
            for page_number, page in enumerate(document, start=1):
                matrix = pymupdf.Matrix(self.OCR_DPI / 72, self.OCR_DPI / 72)
                pixmap = page.get_pixmap(matrix=matrix, alpha=False)

                image = Image.frombytes(
                    "RGB",
                    [pixmap.width, pixmap.height],
                    pixmap.samples,
                )

                try:
                    text = pytesseract.image_to_string(
                        image,
                        lang=self.OCR_LANGUAGES,
                        config="--psm 3",
                    )
                except pytesseract.TesseractNotFoundError as error:
                    raise RuntimeError(
                        "Program Tesseract OCR belum ditemukan. "
                        "Instal Tesseract OCR untuk Windows dan pastikan "
                        "tesseract.exe tersedia di PATH."
                    ) from error
                except pytesseract.TesseractError as error:
                    raise RuntimeError(
                        "OCR gagal. Pastikan data bahasa Tesseract "
                        "'ind' dan 'eng' sudah terpasang. Detail: "
                        f"{error}"
                    ) from error

                clean_text = text.strip()
                pages.append(
                    f"## Halaman {page_number}\n\n"
                    f"{clean_text if clean_text else '_Tidak ada teks yang terdeteksi._'}"
                )

        finally:
            document.close()

        return (
            f"# {pdf_path.stem}\n\n"
            f"> Dokumen diproses menggunakan OCR ({self.OCR_LANGUAGES}). "
            "Hasil pengenalan teks mungkin memerlukan pemeriksaan ulang.\n\n"
            + "\n\n---\n\n".join(pages)
        )
