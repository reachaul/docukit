from pathlib import Path
from PIL import Image


def convert_image(source: str | Path, output_dir: str | Path, target_format: str) -> Path:
    source = Path(source)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    target_format = target_format.upper()
    if target_format not in {"JPG", "PNG"}:
        raise ValueError("Format gambar tujuan yang didukung: JPG dan PNG.")
    suffix = ".jpg" if target_format == "JPG" else ".png"
    target = output_dir / f"{source.stem}{suffix}"
    counter = 1
    while target.exists():
        target = output_dir / f"{source.stem}_{counter}{suffix}"
        counter += 1
    with Image.open(source) as image:
        if target_format == "JPG":
            if image.mode in ("RGBA", "LA") or (image.mode == "P" and "transparency" in image.info):
                background = Image.new("RGB", image.size, "white")
                rgba = image.convert("RGBA")
                background.paste(rgba, mask=rgba.getchannel("A"))
                background.save(target, "JPEG", quality=95, optimize=True)
            else:
                image.convert("RGB").save(target, "JPEG", quality=95, optimize=True)
        else:
            image.save(target, "PNG", optimize=True)
    return target
