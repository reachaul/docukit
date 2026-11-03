# DocuKit

**Your Documents. Your Device. Your Privacy.**

DocuKit is a privacy-focused desktop document toolkit for Windows. It brings common document conversion and PDF management tasks into one simple application, with core processing performed locally on your device.

**Version:** 1.1.0  
**Platform:** Windows 10/11 (64-bit)  
**Developer:** by reachaul  
**Copyright:** © 2026

---

## What's New in v1.1.0

### Markdown export

DocuKit now supports converting Markdown (`.md` and `.markdown`) files into:

- **PDF** (`.pdf`)
- **Microsoft Word** (`.docx`)
- **HTML** (`.html`)
- **Plain Text** (`.txt`)

This complements the existing document-to-Markdown workflow. Markdown export is available from the **File Converter** page: select **Markdown (MD)** as the source format, choose an output format, add one or more files, select an output folder, and convert.

> Markdown export availability depends on the v1.1.0 application build and its installed dependencies. Test the conversion workflow before distributing a packaged build.

---

## Features

### File Converter

Convert supported source files to Markdown, and export Markdown files to other formats.

**To Markdown:**
- PDF
- Word (`.docx`)
- Excel (`.xlsx`)
- PowerPoint (`.pptx`)
- HTML
- CSV
- TXT
- Supported images and other formats handled by the installed MarkItDown converters

**From Markdown:**
- Markdown to PDF
- Markdown to Word (`.docx`)
- Markdown to HTML
- Markdown to TXT

**Additional conversion tools:**
- PDF to JPG
- PDF to PNG
- Images (JPG/PNG/WEBP) to PDF
- Image format conversion to JPG or PNG

The available conversions are shown dynamically in the File Converter interface.

### PDF Toolkit

- Merge PDF files
- Split PDF files
- Extract selected pages
- Remove selected pages
- Rotate pages
- Reorder pages
- Compress PDF files

### OCR Tools

The OCR workspace is part of the application interface. Local OCR functionality requires a compatible Tesseract OCR installation and language data. Check the current application build for the tools enabled in that release.

### PDF Editor

The PDF Editor workspace is reserved for features planned for future releases. Not all editing tools are currently implemented.

---

## Privacy and Offline Use

DocuKit is designed around local document processing. Core PDF operations and supported local conversions are performed on the user's computer.

Some optional conversion integrations or services may require internet access or external credentials if configured. OCR also requires a local Tesseract installation. Do not treat every optional integration as offline-capable.

Your documents are not intentionally uploaded to a DocuKit cloud service.

---

## Installation

### Windows release

1. Download the Windows x64 ZIP package from the [GitHub Releases](https://github.com/reachaul/docukit/releases) page.
2. Extract the ZIP file to a folder of your choice.
3. Open the extracted `DocuKit` folder.
4. Run `DocuKit.exe`.

Keep the extracted application folder structure intact. Do not move the EXE out of its accompanying `_internal` folder.

### Run from source

Requirements:
- Windows 10/11, 64-bit
- Python version compatible with the dependencies listed in the project requirements

Clone the repository:

```powershell
git clone https://github.com/reachaul/docukit.git
cd docukit
```

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install the base dependencies:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Install the converter dependencies:

```powershell
python -m pip install -r requirements-converter.txt
```

For Markdown export, install the additional dependencies:

```powershell
python -m pip install Markdown python-docx
```

Run the application:

```powershell
python launcher.py
```

If PowerShell blocks activation, run this command in the current terminal and activate again:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

---

## Build the Windows Application

Install build dependencies:

```powershell
python -m pip install -r requirements-build.txt
```

Build with PyInstaller:

```powershell
python -m PyInstaller --clean --noconfirm DocuKit.spec
```

The packaged application will be created in:

```text
dist\DocuKit\
```

Run `dist\DocuKit\DocuKit.exe` to test the build. Distribute the complete `DocuKit` folder as a ZIP archive; do not distribute the EXE by itself.

---

## Project Structure

```text
docukit/
├── app/
│   ├── converters/
│   ├── interface.py
│   └── main.py
├── assets/
│   └── fonts/
├── launcher.py
├── DocuKit.spec
├── requirements.txt
├── requirements-converter.txt
├── requirements-build.txt
├── README.md
└── LICENSE
```

The exact project structure may evolve between releases.

---

## Known Limitations

- Conversion fidelity depends on the source document structure and the selected output format.
- Complex layouts, embedded objects, advanced tables, and some styling may not be reproduced exactly when converting between formats.
- OCR requires Tesseract OCR to be installed separately, with the required language data.
- Some workspaces or tools may be placeholders until a future release.
- The packaged application should be tested on a clean Windows environment before broad distribution.

---

## Roadmap

Potential areas for future development:

- Expand PDF editing capabilities.
- Improve OCR workflow and language selection.
- Improve conversion fidelity for tables, images, and complex layouts.
- Reduce packaged application size through modular dependencies.
- Add more document formats and batch-processing improvements.

---

## Contributing

Suggestions, bug reports, and contributions are welcome.

Please include the following when reporting an issue:
- DocuKit version
- Windows version
- Source and target file formats
- Steps to reproduce the issue
- Error message or screenshot, if available

---

## License

See the [LICENSE](LICENSE) file for license details.

---

**DocuKit**  
*Your Documents. Your Device. Your Privacy.*  
**by reachaul**
