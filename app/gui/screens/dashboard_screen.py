from PySide6.QtWidgets import QLabel, QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QHBoxLayout


class DashboardScreen(QWidget):
    def __init__(self, on_action):
        super().__init__()
        layout = QVBoxLayout(self)
        self.summary = QLabel("No data yet")
        layout.addWidget(self.summary)
        row = QHBoxLayout()
        for label, key in [
            ("Refresh markets", "markets"),
            ("Refresh events", "events"),
            ("Refresh transcripts", "transcripts"),
            ("Recompute model", "model"),
            ("Full sync", "full"),
        ]:
            btn = QPushButton(label)
            btn.clicked.connect(lambda _=False, k=key: on_action(k))
            row.addWidget(btn)
        layout.addLayout(row)
        self.table = QTableWidget(0, 9)
        self.table.setHorizontalHeaderLabels(
            ["Market", "Outcome", "Threshold", "Market Prob", "Model Prob", "Edge", "Confidence", "Event", "Updated"]
        )
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)

    def update_summary(self, text: str):
        self.summary.setText(text)

    def set_rows(self, rows: list[list[str]]):
        self.table.setRowCount(len(rows))
        for r, row in enumerate(rows):
            for c, value in enumerate(row):
                self.table.setItem(r, c, QTableWidgetItem(str(value)))
