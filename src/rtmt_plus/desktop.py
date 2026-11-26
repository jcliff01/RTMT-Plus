"""Optional PySide6 desktop search interface."""
from __future__ import annotations
import sys

from . import rtmt
from .search import search

def main() -> int:
    try:
        from PySide6.QtCore import QSettings
        from PySide6.QtWidgets import (QApplication, QFileDialog, QHBoxLayout,
            QLabel, QLineEdit, QMainWindow, QMessageBox, QPushButton,
            QPlainTextEdit, QVBoxLayout, QWidget)
    except ImportError:
        print("Desktop dependencies missing. Install: pip install -e '.[desktop]'", file=sys.stderr)
        return 2

    class Window(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("RTMT Plus — Log Search Foundation")
            self.resize(1050, 700)
            self.folder = ""
            center = QWidget()
            layout = QVBoxLayout(center)
            top = QHBoxLayout()
            self.path_label = QLabel("Choose a log folder")
            browse = QPushButton("Browse folder")
            browse.clicked.connect(self.browse)
            top.addWidget(browse)
            top.addWidget(self.path_label, 1)
            layout.addLayout(top)
            rtmt_row = QHBoxLayout()
            pick_rtmt = QPushButton("RTMT folder…")
            pick_rtmt.clicked.connect(self.browse_rtmt)
            self.use_traces = QPushButton("Use RTMT traces")
            self.use_traces.clicked.connect(self.use_rtmt_traces)
            self.launch_button = QPushButton("Launch RTMT")
            self.launch_button.clicked.connect(self.launch_rtmt)
            self.rtmt_label = QLabel("No RTMT install selected")
            for widget in (pick_rtmt, self.use_traces, self.launch_button):
                rtmt_row.addWidget(widget)
            rtmt_row.addWidget(self.rtmt_label, 1)
            layout.addLayout(rtmt_row)
            row = QHBoxLayout()
            self.query = QLineEdit()
            self.query.setPlaceholderText("Search text (case-insensitive)")
            self.query.returnPressed.connect(self.run_search)
            button = QPushButton("Search")
            button.clicked.connect(self.run_search)
            row.addWidget(self.query, 1)
            row.addWidget(button)
            layout.addLayout(row)
            self.results = QPlainTextEdit()
            self.results.setReadOnly(True)
            layout.addWidget(self.results, 1)
            self.setCentralWidget(center)
            self.settings = QSettings("RTMT Plus", "RTMT Plus")
            self.install = None
            saved = self.settings.value("rtmt_home", "")
            if saved:
                self.set_rtmt(saved, quiet=True)
            self.refresh_rtmt_buttons()

        def refresh_rtmt_buttons(self):
            has = self.install is not None
            self.launch_button.setEnabled(has)
            self.use_traces.setEnabled(has and self.install.trace_download_path is not None)

        def set_rtmt(self, folder, quiet=False):
            try:
                self.install = rtmt.load_install(folder)
            except (OSError, ValueError) as exc:
                self.install = None
                if not quiet:
                    QMessageBox.warning(self, "RTMT Plus", str(exc))
            else:
                self.settings.setValue("rtmt_home", str(self.install.root))
                self.rtmt_label.setText(f"RTMT {self.install.version or '(unknown version)'} — {self.install.root}")
            self.refresh_rtmt_buttons()

        def browse_rtmt(self):
            folder = QFileDialog.getExistingDirectory(self, "Select Cisco RTMT install folder (contains JRtmt.jar)")
            if folder:
                self.set_rtmt(folder)

        def use_rtmt_traces(self):
            path = self.install.trace_download_path
            if not path.is_dir():
                QMessageBox.information(self, "RTMT Plus", f"RTMT's trace folder does not exist yet:\n{path}")
                return
            self.folder = str(path)
            self.path_label.setText(self.folder)

        def launch_rtmt(self):
            if not rtmt.java_supported(rtmt.find_java()):
                QMessageBox.warning(self, "RTMT Plus",
                    "RTMT 15 needs Java 8 (1.8.0_300 or newer) with JavaFX on your PATH. "
                    "It may not start.")
            try:
                rtmt.launch(self.install)
                self.statusBar().showMessage("RTMT started")
            except OSError as exc:
                QMessageBox.critical(self, "Could not start RTMT", str(exc))

        def describe(self, match):
            if match.cause is None:
                return ""
            text = self.install.describe(match.cause) if self.install else None
            return f" [cause {match.cause}{': ' + text if text else ''}]"

        def browse(self):
            folder = QFileDialog.getExistingDirectory(self, "Select CUCM log folder")
            if folder:
                self.folder = folder
                self.path_label.setText(folder)

        def run_search(self):
            if not self.folder or not self.query.text().strip():
                QMessageBox.information(self, "RTMT Plus", "Choose a folder and enter a search query.")
                return
            self.results.clear()
            try:
                matches = list(search([self.folder], self.query.text(), limit=1000))
                self.results.setPlainText("\n".join(
                    f"{m.path}:{m.line} [{m.timestamp or 'no timestamp'}] {m.text}{self.describe(m)}"
                    for m in matches
                ) or "No matches found.")
                self.statusBar().showMessage(f"{len(matches)} matches (max 1000)")
            except (OSError, ValueError) as exc:
                QMessageBox.critical(self, "Search failed", str(exc))

    app = QApplication(sys.argv)
    window = Window()
    window.show()
    return app.exec()

if __name__ == "__main__":
    raise SystemExit(main())
