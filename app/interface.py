from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton,
    QStackedWidget, QFrame, QGridLayout, QFileDialog, QLineEdit, QComboBox,
    QFormLayout, QGroupBox, QMessageBox, QListWidget, QListWidgetItem,
    QSpinBox, QAbstractItemView, QDialog
)
from PySide6.QtGui import QFontDatabase, QColor, QDesktopServices
from PySide6.QtCore import QUrl

from app.pdf_toolkit import operations as pdf
from app.converters.file_converter import SUPPORTED, EXTENSIONS, convert_files

STYLE = """
QMainWindow,QWidget#root{background:#171B1A;color:#F0F3F2;font-family:'DM Sans','Segoe UI';font-size:10.5pt}
QLabel{background:transparent} QLabel#muted{color:#A0ADA7} QLabel#title{font-family:'Poppins','DM Sans','Segoe UI';font-size:27px;font-weight:700;color:#FFFFFF}
QFrame#sidebar{background:#202925;border-right:1px solid #303D36}
QLabel#brand{font-family:'Poppins','DM Sans','Segoe UI';font-size:18px;font-weight:700;color:#FFFFFF}
QPushButton{background:#29342F;color:#F0F3F2;border:1px solid #3A4840;border-radius:10px;padding:10px 14px}
QPushButton:hover{background:#35443C;border-color:#58C99A}
QPushButton:checked{background:#29483A;border-color:#55C995}
QPushButton#nav{text-align:left;padding:12px;border:0;background:transparent;border-radius:10px}
QPushButton#nav:checked{background:#2B4036;border:1px solid #4A8267}
QPushButton#primary{background:#32B982;border-color:#32B982;color:#10251B;font-weight:700;padding:13px}
QPushButton#primary:hover{background:#51D49B;border-color:#51D49B}
QPushButton#tool{text-align:left;padding:17px;min-height:92px;font-weight:600;font-size:12pt;background:#222B27;border:1px solid #35443C}
QPushButton#tool:hover{background:#2A3730;border-color:#62C99A}
QFrame#card,QGroupBox{background:#222B27;border:1px solid #35443C;border-radius:12px}
QLineEdit,QComboBox,QSpinBox,QListWidget{background:#1B2320;color:#F0F3F2;border:1px solid #3B4942;border-radius:9px;padding:10px}
QComboBox::drop-down{border:0;width:28px}
QListWidget::item{padding:9px;border-bottom:1px solid #303D36}
QGroupBox{margin-top:12px;padding-top:12px}
QGroupBox::title{subcontrol-origin:margin;left:14px;padding:0 5px;color:#AFC2B8}
"""
APP_NAME = "DocuKit"
APP_VERSION = "1.0.0"
PRODUCTION_YEAR = "2026"
# Set this after creating the public GitHub repository.
GITHUB_REPO_URL = "https://github.com/reachaul/docukit"
OUTPUT_DEFAULT = Path.home() / "Documents" / APP_NAME


class DropArea(QFrame):
    def __init__(self, callback, label="Drop files here"):
        super().__init__()
        self.callback = callback
        self.setAcceptDrops(True)
        self.setObjectName("dropArea")
        self.setMinimumHeight(116)
        self.setStyleSheet("QFrame#dropArea{border:2px dashed #4A9D79;border-radius:14px;background:#202D27;} QFrame#dropArea:hover{background:#263A30;border-color:#65D6A2;}")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        title = QLabel("↓  Drag & drop files here")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-family:'DM Sans';font-size:17px;color:#6BE0AE;font-weight:700")
        subtitle = QLabel(label)
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet("color:#929D97")
        layout.addWidget(title)
        layout.addWidget(subtitle)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        paths = [url.toLocalFile() for url in event.mimeData().urls() if url.isLocalFile()]
        if paths:
            self.callback(paths)
        event.acceptProposedAction()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self._load_local_fonts()
        self.setWindowTitle(f"{APP_NAME} · v{APP_VERSION}")
        self.resize(1240, 820)
        self.setMinimumSize(980, 680)
        OUTPUT_DEFAULT.mkdir(parents=True, exist_ok=True)
        self.output = OUTPUT_DEFAULT
        self.stack = QStackedWidget()
        self.nav = []
        root = QWidget()
        root.setObjectName("root")
        self.setCentralWidget(root)
        layout = QHBoxLayout(root)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(245)
        side_layout = QVBoxLayout(sidebar)
        side_layout.setContentsMargins(16, 24, 16, 16)
        brand = QLabel(APP_NAME)
        brand.setObjectName("brand")
        side_layout.addWidget(brand)
        subtitle = QLabel("LOCAL DOCUMENT TOOLKIT")
        subtitle.setObjectName("muted")
        side_layout.addWidget(subtitle)
        side_layout.addSpacing(24)

        pages = [
            ("Home", self.home),
            ("File Converter", self.file_converter),
            ("PDF Toolkit", self.pdf_toolkit),
            ("OCR Tools", self.ocr),
            ("PDF Editor", self.editor),
            ("Settings", self.settings),
        ]
        for name, builder in pages:
            page_index = self.stack.addWidget(builder())
            button = QPushButton(name)
            button.setObjectName("nav")
            button.setCheckable(True)
            button.clicked.connect(lambda checked=False, n=page_index: self.go(n))
            side_layout.addWidget(button)
            self.nav.append(button)
        side_layout.addStretch()
        credit = QLabel("by reachaul")
        credit.setObjectName("developerCredit")
        credit.setStyleSheet("font-family:'Poppins','DM Sans','Segoe UI';font-size:13px;font-weight:700;color:#F0F3F2")
        side_layout.addWidget(credit)
        release = QLabel(f"© {PRODUCTION_YEAR}  ·  VERSION {APP_VERSION}")
        release.setObjectName("muted")
        release.setStyleSheet("font-size:9pt;color:#A0ADA7")
        side_layout.addWidget(release)
        github = QPushButton("GitHub Repository ↗" if GITHUB_REPO_URL else "GitHub Repository · Coming soon")
        github.setObjectName("nav")
        github.setEnabled(bool(GITHUB_REPO_URL))
        if GITHUB_REPO_URL:
            github.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(GITHUB_REPO_URL)))
        side_layout.addWidget(github)
        layout.addWidget(sidebar)
        layout.addWidget(self.stack, 1)
        self.setStyleSheet(STYLE)
        self.go(0)

    def _load_local_fonts(self):
        """Load bundled fonts when present; otherwise use system fallbacks."""
        font_dir = Path(__file__).resolve().parent.parent / "assets" / "fonts"
        if font_dir.exists():
            for font_file in sorted(font_dir.glob("*.ttf")):
                QFontDatabase.addApplicationFont(str(font_file))

    def page(self, title, description):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(34, 28, 34, 24)
        layout.setSpacing(14)
        heading = QLabel(title)
        heading.setObjectName("title")
        layout.addWidget(heading)
        desc = QLabel(description)
        desc.setObjectName("muted")
        desc.setWordWrap(True)
        layout.addWidget(desc)
        return widget, layout

    def go(self, index):
        self.stack.setCurrentIndex(index)
        for i, button in enumerate(self.nav):
            button.setChecked(i == index)

    def card(self, title, description, layout, callback=None):
        button = QPushButton(f"{title}\n{description}")
        button.setObjectName("tool")
        button.setMinimumHeight(88)
        button.setMinimumWidth(0)
        button.setStyleSheet("QPushButton{text-align:left;white-space:normal}")
        if callback:
            button.clicked.connect(callback)
        layout.addWidget(button)
        return button

    def home(self):
        widget, layout = self.page(
            f"Welcome to {APP_NAME}",
            "Your documents stay on your computer. Choose a workspace.",
        )
        home_cards = [
            ("File Converter", "Convert documents between supported formats.", lambda: self.go(1), "#3285E8"),
            ("PDF Toolkit", "Merge, split, organize, compress and manage PDF files.", lambda: self.go(2), "#F04452"),
            ("OCR Tools", "Extract text from scanned documents with local OCR.", lambda: self.go(3), "#A78BFA"),
        ]
        for title, description, action, accent in home_cards:
            button = self.card(title, description, layout, action)
            button.setStyleSheet(f"QPushButton#tool{{border-left:4px solid {accent};}} QPushButton#tool:hover{{border-color:{accent};background:#2A3730;}}")
        layout.addStretch()
        return widget

    def file_converter(self):
        widget, layout = self.page(
            "File Converter",
            "Choose a source format and a target format. Only available local conversions are shown.",
        )
        format_box = QGroupBox("Conversion format")
        form = QFormLayout(format_box)
        self.src = QComboBox()
        self.src.addItems(list(SUPPORTED.keys()))
        self._color_format_items(self.src)
        self.dst = QComboBox()
        self.src.currentTextChanged.connect(self.update_target_formats)
        form.addRow("From", self.src)
        form.addRow("To", self.dst)
        layout.addWidget(format_box)

        file_header = QHBoxLayout()
        file_title = QLabel("Selected files")
        file_title.setStyleSheet("font-weight:600")
        self.file_count = QLabel("0 files")
        self.file_count.setObjectName("muted")
        file_header.addWidget(file_title)
        file_header.addStretch()
        file_header.addWidget(self.file_count)
        layout.addLayout(file_header)

        self.conv_files = []
        self.conv_list = QListWidget()
        self.conv_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.conv_list.setMinimumHeight(76)
        self.conv_list.setMaximumHeight(145)
        layout.addWidget(self.conv_list)
        file_row = QHBoxLayout()
        self.drop = DropArea(self.add_conversion_files, "PDF, DOCX, XLSX, PPTX, images and supported documents")
        file_row.addWidget(self.drop, 3)
        browse = QPushButton("Browse files")
        browse.setMinimumHeight(104)
        browse.clicked.connect(self.browse_conversion)
        file_row.addWidget(browse, 1)
        layout.addLayout(file_row)

        remove_row = QHBoxLayout()
        remove_button = QPushButton("Remove selected")
        remove_button.clicked.connect(self.remove_selected_conversion_files)
        clear_button = QPushButton("Clear all")
        clear_button.clicked.connect(self.clear_conversion_files)
        remove_row.addWidget(remove_button)
        remove_row.addWidget(clear_button)
        remove_row.addStretch()
        layout.addLayout(remove_row)

        output_row = QHBoxLayout()
        self.conv_out = QLineEdit(str(self.output))
        output_button = QPushButton("Output folder")
        output_button.clicked.connect(lambda: self.pick_folder(self.conv_out))
        output_row.addWidget(self.conv_out, 1)
        output_row.addWidget(output_button)
        layout.addLayout(output_row)

        run = QPushButton("✦  Convert files")
        run.setObjectName("primary")
        run.clicked.connect(self.convert_action)
        run.setMinimumHeight(48)
        layout.addWidget(run)
        self.conv_status = QLabel("Ready. Choose formats and add files.")
        self.conv_status.setObjectName("muted")
        self.conv_status.setWordWrap(True)
        layout.addWidget(self.conv_status)
        layout.addStretch()
        self.update_target_formats(self.src.currentText())
        return widget

    def update_target_formats(self, source_format):
        if not hasattr(self, "dst"):
            return
        current = self.dst.currentText()
        self.dst.blockSignals(True)
        self.dst.clear()
        self.dst.addItems(SUPPORTED.get(source_format, []))
        self._color_format_items(self.dst)
        if current in SUPPORTED.get(source_format, []):
            self.dst.setCurrentText(current)
        self.dst.blockSignals(False)
        self.conv_status.setText(f"Available targets for {source_format}: {', '.join(SUPPORTED.get(source_format, []))}")

    @staticmethod
    def _color_format_items(combo):
        palette = {
            "PDF": "#F04452", "Markdown (MD)": "#A78BFA", "JPG": "#E8B94E",
            "PNG": "#35B9CF", "WEBP": "#DC75AD", "Image (JPG/PNG/WEBP)": "#E8B94E",
            "Word (DOCX)": "#3285E8", "Excel (XLSX)": "#20A66A",
            "PowerPoint (PPTX)": "#E87942", "HTML": "#E56B35",
            "CSV": "#21A6A1", "TXT": "#A0AAB3"
        }
        for index in range(combo.count()):
            color = palette.get(combo.itemText(index))
            if color:
                combo.setItemData(index, QColor(color), Qt.ForegroundRole)

    def add_conversion_files(self, paths):
        accepted = EXTENSIONS[self.src.currentText()]
        added = 0
        rejected = []
        for raw_path in paths:
            path = Path(raw_path)
            if not path.is_file():
                continue
            if path.suffix.lower() not in accepted:
                rejected.append(path.name)
                continue
            if str(path) in self.conv_files:
                continue
            self.conv_files.append(str(path))
            size = path.stat().st_size
            item = QListWidgetItem(f"{path.name}     ·     {self._format_size(size)}")
            item.setData(Qt.UserRole, str(path))
            self.conv_list.addItem(item)
            added += 1
        self.update_file_count()
        if rejected:
            QMessageBox.warning(
                self, "Unsupported file type",
                "These files do not match the selected source format:\n" + "\n".join(rejected[:10]),
            )
        if added:
            self.conv_status.setText(f"Added {added} file(s). Ready to convert.")

    @staticmethod
    def _format_size(size):
        if size < 1024:
            return f"{size} B"
        if size < 1024 * 1024:
            return f"{size / 1024:.1f} KB"
        return f"{size / (1024 * 1024):.2f} MB"

    def update_file_count(self):
        self.file_count.setText(f"{len(self.conv_files)} file(s)")

    def remove_selected_conversion_files(self):
        selected = {item.data(Qt.UserRole) for item in self.conv_list.selectedItems()}
        self.conv_files = [path for path in self.conv_files if path not in selected]
        for item in self.conv_list.selectedItems():
            self.conv_list.takeItem(self.conv_list.row(item))
        self.update_file_count()

    def clear_conversion_files(self):
        self.conv_files.clear()
        self.conv_list.clear()
        self.update_file_count()
        self.conv_status.setText("File list cleared.")

    def browse_conversion(self):
        extensions = " ".join(f"*{ext}" for ext in sorted(EXTENSIONS[self.src.currentText()]))
        files, _ = QFileDialog.getOpenFileNames(self, "Select files", "", f"Supported files ({extensions})")
        if files:
            self.add_conversion_files(files)

    def convert_action(self):
        if not self.conv_files:
            QMessageBox.information(self, "No files", "Add files using drag & drop or Browse files first.")
            return
        source_format = self.src.currentText()
        target_format = self.dst.currentText()
        try:
            output = Path(self.conv_out.text()).expanduser()
            if not str(self.conv_out.text()).strip():
                raise ValueError("Pilih folder output terlebih dahulu.")
            self.conv_status.setText("Converting files locally. Please wait...")
            from PySide6.QtWidgets import QApplication
            QApplication.processEvents()
            results = convert_files(self.conv_files, source_format, target_format, output)
            self.conv_status.setText(f"Completed: {len(results)} output file(s). Saved to {output}")
            QMessageBox.information(self, "Conversion completed", "Output files:\n" + "\n".join(str(p) for p in results))
        except Exception as error:
            self.conv_status.setText("Conversion failed. See the error message for details.")
            QMessageBox.critical(self, "Conversion failed", str(error))

    def pdf_toolkit(self):
        widget, layout = self.page("PDF Toolkit", "Choose a PDF operation. Conversion to other formats belongs in File Converter.")
        grid_widget = QWidget()
        grid = QGridLayout(grid_widget)
        grid.setSpacing(12)
        tasks = [
            ("Merge PDF", "Combine multiple PDFs", "merge"),
            ("Split PDF", "Split into separate files", "split"),
            ("Extract Pages", "Save chosen pages", "extract"),
            ("Remove Pages", "Delete chosen pages", "remove"),
            ("Rotate Pages", "Rotate chosen pages", "rotate"),
            ("Reorder Pages", "Change page order", "reorder"),
            ("Compress PDF", "Reduce PDF file size", "compress"),
        ]
        task_colors = ["#F04452", "#E87942", "#3285E8", "#DC75AD", "#21A6A1", "#A78BFA", "#20A66A"]
        for index, (title, description, key) in enumerate(tasks):
            button = QPushButton(f"{title}\n{description}")
            button.setObjectName("tool")
            accent = task_colors[index % len(task_colors)]
            button.setStyleSheet(f"QPushButton#tool{{border-left:4px solid {accent};}} QPushButton#tool:hover{{border-color:{accent};background:#2A3730;}}")
            button.clicked.connect(lambda checked=False, task=key: self.open_pdf_task(task))
            grid.addWidget(button, index // 3, index % 3)
        layout.addWidget(grid_widget)
        layout.addStretch()
        return widget

    def open_pdf_task(self, key):
        names = {"merge": "Merge PDF", "split": "Split PDF", "extract": "Extract Pages", "remove": "Remove Pages", "rotate": "Rotate Pages", "reorder": "Reorder Pages", "compress": "Compress PDF"}
        dialog = QDialog(self)
        dialog.setWindowTitle(names[key])
        dialog.resize(760, 640)
        dialog.setMinimumSize(680, 560)
        dialog.setWindowModality(Qt.WindowModal)
        layout = QVBoxLayout(dialog)
        heading = QLabel(names[key])
        heading.setObjectName("title")
        layout.addWidget(heading)
        files = []
        listing = QListWidget()
        listing.setMinimumHeight(110)
        layout.addWidget(listing)

        def add(paths):
            for raw in paths:
                path = Path(raw)
                if path.is_file() and path.suffix.lower() == ".pdf" and str(path) not in files:
                    files.append(str(path))
                    listing.addItem(path.name)

        file_row = QHBoxLayout()
        drop = DropArea(add, "Drop PDF files here")
        file_row.addWidget(drop, 3)
        browse = QPushButton("Browse PDF files")
        browse.setMinimumHeight(104)
        browse.clicked.connect(lambda: self._browse_pdf(add, key))
        file_row.addWidget(browse, 1)
        layout.addLayout(file_row)

        page_input = QLineEdit()
        page_input.setPlaceholderText("Pages, e.g. 1,3,5-7")
        if key in ("extract", "remove", "rotate", "reorder"):
            layout.addWidget(QLabel("Page selection / order"))
            layout.addWidget(page_input)
        rotation = QComboBox()
        rotation.addItems(["90", "180", "270"])
        if key == "rotate":
            layout.addWidget(QLabel("Rotation (degrees clockwise)"))
            layout.addWidget(rotation)
        count = QSpinBox()
        count.setRange(1, 999)
        count.setValue(1)
        if key == "split":
            layout.addWidget(QLabel("Pages per output file"))
            layout.addWidget(count)

        output = QLineEdit(str(self.output))
        out_row = QHBoxLayout()
        out_row.addWidget(output, 1)
        choose_output = QPushButton("Output folder")
        choose_output.clicked.connect(lambda: self.pick_folder(output))
        out_row.addWidget(choose_output)
        layout.addLayout(out_row)
        filename = QLineEdit("output")
        if key not in ("split",):
            filename.setPlaceholderText("Output filename (without extension)")
            layout.addWidget(filename)
        run = QPushButton(names[key])
        run.setObjectName("primary")
        layout.addWidget(run)
        status = QLabel("Ready.")
        status.setObjectName("muted")
        layout.addWidget(status)

        def execute():
            try:
                if not files:
                    raise ValueError("Pilih file PDF terlebih dahulu.")
                destination = Path(output.text()).expanduser()
                destination.mkdir(parents=True, exist_ok=True)
                target = destination / ((filename.text().strip() or "output") + ".pdf")
                if key == "merge":
                    if len(files) < 2:
                        raise ValueError("Pilih minimal dua PDF.")
                    result = pdf.merge(files, str(target))
                elif key == "split":
                    result = pdf.split(files[0], destination, count.value())
                elif key == "extract":
                    result = pdf.extract(files[0], page_input.text(), str(target))
                elif key == "remove":
                    result = pdf.remove(files[0], page_input.text(), str(target))
                elif key == "rotate":
                    result = pdf.rotate(files[0], int(rotation.currentText()), str(target), page_input.text() or None)
                elif key == "reorder":
                    result = pdf.reorder(files[0], page_input.text(), str(target))
                else:
                    result = pdf.compress(files[0], str(target))
                status.setText("Completed.")
                QMessageBox.information(dialog, "Completed", f"Output saved:\n{result}")
            except Exception as error:
                status.setText("Operation failed.")
                QMessageBox.critical(dialog, "Operation failed", str(error))

        run.clicked.connect(execute)
        dialog.show()
        self._active_dialog = dialog

    def _browse_pdf(self, callback, key):
        if key == "merge":
            files, _ = QFileDialog.getOpenFileNames(self, "Select PDF files", "", "PDF files (*.pdf)")
            callback(files)
        else:
            file, _ = QFileDialog.getOpenFileName(self, "Select PDF", "", "PDF files (*.pdf)")
            callback([file] if file else [])

    def ocr(self):
        widget, layout = self.page("OCR Tools", "OCR uses your local Tesseract installation. Advanced preprocessing is planned.")
        self.card_info(layout, "Scanned PDF to Markdown", "OCR engine is optional and requires Tesseract plus Indonesian/English language data.")
        layout.addStretch()
        return widget

    def editor(self):
        widget, layout = self.page("PDF Editor", "PDF editing tools will be added in a later release.")
        self.card_info(layout, "Planned tools", "Watermark · Page numbers · Crop · Metadata · Password tools")
        layout.addStretch()
        return widget

    def settings(self):
        widget, layout = self.page("Settings", "Local application preferences.")
        self.card_info(layout, "Privacy", "Documents are processed on this computer. No cloud upload is configured.")
        layout.addStretch()
        return widget

    def card_info(self, layout, title, description):
        frame = QFrame()
        frame.setObjectName("card")
        box = QVBoxLayout(frame)
        heading = QLabel(title)
        heading.setStyleSheet("font-size:15px;font-weight:600")
        box.addWidget(heading)
        detail = QLabel(description)
        detail.setObjectName("muted")
        detail.setWordWrap(True)
        box.addWidget(detail)
        layout.addWidget(frame)

    def pick_folder(self, edit):
        folder = QFileDialog.getExistingDirectory(self, "Choose output folder", edit.text())
        if folder:
            edit.setText(folder)
