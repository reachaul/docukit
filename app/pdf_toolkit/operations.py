from pathlib import Path
from io import BytesIO

from pypdf import PdfReader, PdfWriter
import pymupdf
from PIL import Image


def _pages(spec, total):
    selected = set()
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            a, b = map(int, part.split("-", 1))
            if a < 1 or b < a or b > total:
                raise ValueError(f"Rentang halaman tidak valid: {part}")
            selected.update(range(a - 1, b))
        else:
            n = int(part)
            if n < 1 or n > total:
                raise ValueError(f"Halaman di luar batas: {n}")
            selected.add(n - 1)
    return sorted(selected)


def merge(files, output):
    writer = PdfWriter()
    for file in files:
        reader = PdfReader(file)
        for page in reader.pages:
            writer.add_page(page)
    with open(output, "wb") as handle:
        writer.write(handle)
    return Path(output)


def split(source, output_dir, pages_per_file=1):
    reader = PdfReader(source)
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    made = []
    for start in range(0, len(reader.pages), pages_per_file):
        writer = PdfWriter()
        for page in reader.pages[start:start + pages_per_file]:
            writer.add_page(page)
        dest = out / f"{Path(source).stem}_part_{start // pages_per_file + 1}.pdf"
        with open(dest, "wb") as handle:
            writer.write(handle)
        made.append(dest)
    return made


def extract(source, spec, output):
    reader = PdfReader(source)
    ids = _pages(spec, len(reader.pages))
    if not ids:
        raise ValueError("Pilih halaman yang akan diekstrak.")
    writer = PdfWriter()
    for index in ids:
        writer.add_page(reader.pages[index])
    with open(output, "wb") as handle:
        writer.write(handle)
    return Path(output)


def remove(source, spec, output):
    reader = PdfReader(source)
    ids = set(_pages(spec, len(reader.pages)))
    if len(ids) == len(reader.pages):
        raise ValueError("Tidak dapat menghapus semua halaman.")
    writer = PdfWriter()
    for index, page in enumerate(reader.pages):
        if index not in ids:
            writer.add_page(page)
    with open(output, "wb") as handle:
        writer.write(handle)
    return Path(output)


def rotate(source, degrees, output, spec=None):
    reader = PdfReader(source)
    ids = set(_pages(spec, len(reader.pages))) if spec else set(range(len(reader.pages)))
    writer = PdfWriter()
    for index, page in enumerate(reader.pages):
        if index in ids:
            page.rotate(degrees)
        writer.add_page(page)
    with open(output, "wb") as handle:
        writer.write(handle)
    return Path(output)


def reorder(source, spec, output):
    reader = PdfReader(source)
    ids = _pages(spec, len(reader.pages))
    if len(ids) != len(reader.pages) or set(ids) != set(range(len(reader.pages))):
        raise ValueError("Masukkan urutan lengkap semua halaman, misalnya 3,1,2.")
    writer = PdfWriter()
    for index in ids:
        writer.add_page(reader.pages[index])
    with open(output, "wb") as handle:
        writer.write(handle)
    return Path(output)


def _compressed_image_bytes(image_bytes, max_dimension=1600, quality=68):
    """Return a smaller JPEG representation, or None when no safe saving is found."""
    try:
        with Image.open(BytesIO(image_bytes)) as image:
            # Do not flatten transparent images or unusual multi-frame images.
            if image.mode in ("RGBA", "LA", "P") and "transparency" in image.info:
                return None
            if getattr(image, "n_frames", 1) > 1:
                return None
            image = image.copy()
            image.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)
            if image.mode == "L":
                converted = image
            else:
                converted = image.convert("RGB")
            buffer = BytesIO()
            converted.save(buffer, format="JPEG", quality=quality, optimize=True, progressive=True)
            candidate = buffer.getvalue()
            # Never replace an image with a larger encoded version.
            if len(candidate) < len(image_bytes) * 0.97:
                return candidate
    except Exception:
        return None
    return None


def compress(source, output):
    """Optimize PDF structure and recompress embedded raster images.

    Vector text and drawings remain vector-based. Raster images are downsampled
    to at most 1600 px on their longest side and JPEG-encoded at quality 68
    when that produces a smaller stream. Transparent/mask images are preserved.
    """
    source_path = Path(source)
    output_path = Path(output)
    if source_path.resolve() == output_path.resolve():
        raise ValueError("Pilih nama atau folder output yang berbeda dari file sumber.")

    doc = pymupdf.open(source_path)
    replaced = set()
    try:
        for page in doc:
            for image_info in page.get_images(full=True):
                xref = image_info[0]
                smask = image_info[1]
                width = image_info[2]
                height = image_info[3]
                bits_per_component = image_info[4]
                if not xref or xref in replaced or smask or bits_per_component != 8:
                    continue
                if max(width, height) <= 500 and width * height <= 250_000:
                    continue
                try:
                    extracted = doc.extract_image(xref)
                    original = extracted.get("image", b"")
                    if not original:
                        continue
                    candidate = _compressed_image_bytes(original)
                    if candidate:
                        page.replace_image(xref, stream=candidate)
                        replaced.add(xref)
                except Exception:
                    # An unsupported image should not prevent PDF optimization.
                    continue

        output_path.parent.mkdir(parents=True, exist_ok=True)
        doc.save(
            str(output_path),
            garbage=4,
            clean=True,
            deflate=True,
            deflate_images=True,
            deflate_fonts=True,
        )
    finally:
        doc.close()

    return output_path


def pdf_to_images(source, output_dir, fmt="PNG", dpi=150):
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    doc = pymupdf.open(source)
    made = []
    try:
        for index, page in enumerate(doc, 1):
            pix = page.get_pixmap(matrix=pymupdf.Matrix(dpi / 72, dpi / 72), alpha=False)
            ext = fmt.lower()
            dest = out / f"{Path(source).stem}_page_{index}.{ext}"
            pix.save(dest)
            made.append(dest)
    finally:
        doc.close()
    return made


def images_to_pdf(images, output):
    doc = pymupdf.open()
    try:
        for image in images:
            img = Image.open(image).convert("RGB")
            temp = Path(output).with_name("_temp_image.pdf")
            img.save(temp, "PDF")
            part = pymupdf.open(temp)
            doc.insert_pdf(part)
            part.close()
            temp.unlink(missing_ok=True)
        doc.save(output)
    finally:
        doc.close()
    return Path(output)
