# DocuKit

**Your documents. Your device. Your privacy.**

DocuKit is a local-first Windows desktop document toolkit built with Python and PySide6. Made with care — **by reachaul**.

- **Version:** 1.0.0
- **Production year:** 2026
- **Platform:** Windows 10/11 (source build)
- **Processing:** Local on your computer; documents are not uploaded to a cloud service by this application.

**GitHub repository:** https://github.com/reachaul/docukit

> Repository URL is the intended project address; it becomes active after you create the repository on GitHub and push this source.

## Features available in v1.0.0

### File Converter
- PDF to JPG / PNG
- JPG, PNG and WEBP to PDF
- JPG, PNG and WEBP image conversion to JPG / PNG
- PDF, DOCX, XLSX, PPTX, HTML, CSV and TXT to Markdown using the optional MarkItDown engine

### PDF Toolkit
- Merge, split, extract pages, remove pages, rotate pages and reorder pages
- PDF structural optimization and embedded raster image recompression

### Planned / not yet available
- OCR Tools interface and preprocessing
- PDF Editor tools
- PDF to Word / Excel / PowerPoint
- Office documents to PDF

Do not interpret placeholder navigation items as implemented features.

## Requirements

- Python 3.15 (the development environment used for this project; other versions have not been certified)
- Windows 10/11

## Setup

```powershell
py -3.15 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Optional Markdown conversion engine:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-converter.txt
```

Optional OCR Python bridge (Tesseract OCR must also be installed separately; OCR UI is not yet available in this release):

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-ocr.txt
```

## Run from source

```powershell
.\.venv\Scripts\python.exe -m app.main
```

## Build executable

Install the build and converter dependencies first:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-converter.txt
.\.venv\Scripts\python.exe -m pip install -r requirements-build.txt
```

Then build on Windows:

```powershell
.\.venv\Scripts\pyinstaller.exe --clean --noconfirm DocuKit.spec
```

The output is created under `dist/DocuKit/`. Test it on a Windows machine without the development environment before publishing a binary release.

## Fonts and licenses

DocuKit bundles Poppins SemiBold and DM Sans Regular/Medium under the SIL Open Font License. License texts are included in `assets/fonts/`.

## Privacy

File processing is designed to run locally. Optional engines and their dependencies must be installed by the user.

## Credits

**by reachaul** · © 2026 · Version 1.0.0 · [GitHub](https://github.com/reachaul/docukit)
