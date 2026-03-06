from PySide6.QtWidgets import QCheckBox, QHBoxLayout, QPushButton, QTextEdit, QVBoxLayout, QWidget


class LogsScreen(QWidget):
    def __init__(self, open_logs_folder):
        super().__init__()
        layout = QVBoxLayout(self)
        row = QHBoxLayout()
        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self._clear)
        open_btn = QPushButton("Open logs folder")
        open_btn.clicked.connect(open_logs_folder)
        self.auto_scroll = QCheckBox("Auto scroll")
        self.auto_scroll.setChecked(True)
        row.addWidget(clear_btn)
        row.addWidget(open_btn)
        row.addWidget(self.auto_scroll)
        layout.addLayout(row)
        self.console = QTextEdit()
        self.console.setReadOnly(True)
        layout.addWidget(self.console)

    def append(self, level: str, text: str):
        self.console.append(f"[{level}] {text}")
        if self.auto_scroll.isChecked():
            self.console.ensureCursorVisible()

    def _clear(self):
        self.console.clear()
