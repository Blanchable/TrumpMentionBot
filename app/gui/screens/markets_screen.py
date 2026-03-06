from PySide6.QtWidgets import QComboBox, QHBoxLayout, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget


class MarketsScreen(QWidget):
    def __init__(self, on_refresh):
        super().__init__()
        layout = QVBoxLayout(self)
        controls = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search market title")
        self.threshold_filter = QComboBox()
        self.threshold_filter.addItems(["all", "single", "at_least"])
        refresh = QPushButton("Refresh markets")
        refresh.clicked.connect(on_refresh)
        controls.addWidget(self.search)
        controls.addWidget(self.threshold_filter)
        controls.addWidget(refresh)
        layout.addLayout(controls)
        self.table = QTableWidget(0, 11)
        self.table.setHorizontalHeaderLabels(
            [
                "Market title",
                "Market slug",
                "Outcome term",
                "Threshold type",
                "YES",
                "NO",
                "Implied",
                "Rule notes",
                "Event scope",
                "Resolution end",
                "Last seen",
            ]
        )
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)

    def set_rows(self, rows):
        self.table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            for j, val in enumerate(row):
                self.table.setItem(i, j, QTableWidgetItem(str(val)))
