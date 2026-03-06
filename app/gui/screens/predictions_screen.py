from PySide6.QtWidgets import QComboBox, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget


class PredictionsScreen(QWidget):
    def __init__(self, on_recompute):
        super().__init__()
        layout = QVBoxLayout(self)
        row = QHBoxLayout()
        self.filter = QComboBox()
        self.filter.addItems(["all", "positive edge", "negative edge"])
        btn = QPushButton("Recompute model")
        btn.clicked.connect(on_recompute)
        row.addWidget(self.filter)
        row.addWidget(btn)
        layout.addLayout(row)
        self.table = QTableWidget(0, 11)
        self.table.setHorizontalHeaderLabels(
            [
                "Outcome",
                "Threshold",
                "Market prob",
                "Model prob",
                "Edge",
                "Confidence",
                "Event",
                "Match hist",
                "Recent",
                "Topic",
                "Reason",
            ]
        )
        layout.addWidget(self.table)

    def set_rows(self, rows):
        self.table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            for j, val in enumerate(row):
                self.table.setItem(i, j, QTableWidgetItem(str(val)))
