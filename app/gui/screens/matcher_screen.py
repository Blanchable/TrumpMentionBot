from PySide6.QtWidgets import QTableWidget, QTableWidgetItem, QTextEdit, QVBoxLayout, QWidget


class MatcherScreen(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels(["Outcome", "Threshold", "Aliases", "Raw", "Adjusted", "Spans", "Notes"])
        self.detail = QTextEdit()
        self.detail.setReadOnly(True)
        layout.addWidget(self.table)
        layout.addWidget(self.detail)

    def set_rows(self, rows):
        self.table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            for j, v in enumerate(row):
                self.table.setItem(i, j, QTableWidgetItem(str(v)))
