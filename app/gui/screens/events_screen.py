from PySide6.QtWidgets import QLabel, QPushButton, QSplitter, QTableWidget, QTableWidgetItem, QTextEdit, QVBoxLayout, QWidget


class EventsScreen(QWidget):
    def __init__(self, on_refresh):
        super().__init__()
        layout = QVBoxLayout(self)
        refresh = QPushButton("Refresh events")
        refresh.clicked.connect(on_refresh)
        layout.addWidget(refresh)
        splitter = QSplitter()
        self.table = QTableWidget(0, 9)
        self.table.setHorizontalHeaderLabels(
            ["Title", "Datetime", "Source", "Type", "Location", "Qualifying", "Tags", "Transcript", "Related markets"]
        )
        self.detail = QTextEdit()
        self.detail.setReadOnly(True)
        splitter.addWidget(self.table)
        splitter.addWidget(self.detail)
        layout.addWidget(splitter)
        self.table.itemSelectionChanged.connect(self._on_select)
        self._details = []

    def set_rows(self, rows, details):
        self._details = details
        self.table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            for j, val in enumerate(row):
                self.table.setItem(i, j, QTableWidgetItem(str(val)))

    def _on_select(self):
        idx = self.table.currentRow()
        if 0 <= idx < len(self._details):
            self.detail.setText(self._details[idx])
