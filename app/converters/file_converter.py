from pathlib import Path
from app.pdf_toolkit import operations as pdf
from app.converters.image_converter import convert_image


SUPPORTED = {
    "PDF": ["Markdown (MD)", "JPG", "PNG"],
    "Image (JPG/PNG/WEBP)": ["PDF", "JPG", "PNG"],
    "Word (DOCX)": ["Markdown (MD)"],
    "Excel (XLSX)": ["Markdown (MD)"],
    "PowerPoint (PPTX)": ["Markdown (MD)"],
    "HTML": ["Markdown (MD)"],
    "CSV": ["Markdown (MD)"],
    "TXT": ["Markdown (MD)"],
}

EXTENSIONS = {
    "PDF": {".pdf"},
    "Image (JPG/PNG/WEBP)": {".jpg", ".jpeg", ".png", ".webp"},
    "Word (DOCX)": {".docx"},
    "Excel (XLSX)": {".xlsx"},
    "PowerPoint (PPTX)": {".pptx"},
    "HTML": {".html", ".htm"},
    "CSV": {".csv"},
    "TXT": {".txt"},
}


def convert_files(files, source_format, target_format, output_dir):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    if target_format not in SUPPORTED.get(source_format, []):
        raise ValueError(f"Konversi {source_format} ke {target_format} belum didukung.")

    results = []
    if target_format == "Markdown (MD)":
        from app.converters.markitdown_converter import MarkItDownConverter
        engine = MarkItDownConverter()
        for file in files:
            results.append(engine.convert_to_markdown(file, output_dir))
        return results

    if source_format == "PDF" and target_format in {"JPG", "PNG"}:
        for file in files:
            results.extend(pdf.pdf_to_images(file, output_dir, target_format))
        return results

    if source_format == "Image (JPG/PNG/WEBP)" and target_format == "PDF":
        for file in files:
            source = Path(file)
            target = _unique_path(output_dir, source.stem, ".pdf")
            pdf.images_to_pdf([source], str(target))
            results.append(target)
        return results

    if source_format == "Image (JPG/PNG/WEBP)" and target_format in {"JPG", "PNG"}:
        for file in files:
            results.append(convert_image(file, output_dir, target_format))
        return results

    raise ValueError("Kombinasi format belum tersedia.")


def _unique_path(folder, stem, suffix):
    target = folder / f"{stem}{suffix}"
    index = 1
    while target.exists():
        target = folder / f"{stem}_{index}{suffix}"
        index += 1
    return target
