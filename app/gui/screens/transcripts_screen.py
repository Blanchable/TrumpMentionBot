from PySide6.QtWidgets import QHBoxLayout, QPushButton, QSplitter, QTableWidget, QTableWidgetItem, QTextEdit, QVBoxLayout, QWidget


class TranscriptsScreen(QWidget):
    def __init__(self, on_refresh):
        super().__init__()
        layout = QVBoxLayout(self)
        row = QHBoxLayout()
        btn = QPushButton("Refresh transcripts")
        btn.clicked.connect(on_refresh)
        row.addWidget(btn)
        layout.addLayout(row)
        splitter = QSplitter()
        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels(
            ["Event", "Source", "Status", "Length", "Quality", "Timestamped", "Last fetched"]
        )
        self.preview = QTextEdit()
        self.preview.setReadOnly(True)
        splitter.addWidget(self.table)
        splitter.addWidget(self.preview)
        layout.addWidget(splitter)
        self.table.itemSelectionChanged.connect(self._on_select)
        self._texts = []

    def set_rows(self, rows, texts):
        self._texts = texts
        self.table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            for j, val in enumerate(row):
                self.table.setItem(i, j, QTableWidgetItem(str(val)))

    def _on_select(self):
        idx = self.table.currentRow()
        if 0 <= idx < len(self._texts):
            self.preview.setText(self._texts[idx])
