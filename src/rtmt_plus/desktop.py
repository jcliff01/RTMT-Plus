"""Optional PySide6 desktop search interface."""
from __future__ import annotations
import os
import sys

from .search import search

def main() -> int:
    try:
        from PySide6.QtCore import Qt
        from PySide6.QtGui import QFontDatabase
        from PySide6.QtWidgets import (QApplication, QFileDialog, QHBoxLayout,
            QLabel, QLineEdit, QMainWindow, QMessageBox, QPushButton,
            QPlainTextEdit, QVBoxLayout, QWidget)
    except ImportError:
        print('The desktop window needs PySide6. Install it with: python -m pip install "PySide6>=6.6"', file=sys.stderr)
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
            # One match per line, in a fixed-width font, so columns line up and lines don't wrap.
            self.results.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
            self.results.setFont(QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont))
            layout.addWidget(self.results, 1)
            self.setCentralWidget(center)

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
                    f"{os.path.relpath(m.path, self.folder)}:{m.line}  {m.text}"
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
