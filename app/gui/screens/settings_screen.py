from PySide6.QtWidgets import QCheckBox, QFormLayout, QLineEdit, QPushButton, QSpinBox, QVBoxLayout, QWidget

from app.config import AppSettings


class SettingsScreen(QWidget):
    def __init__(self, on_save, on_test):
        super().__init__()
        self.on_save = on_save
        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.data_dir = QLineEdit()
        self.logs_dir = QLineEdit()
        self.markets_refresh = QSpinBox(); self.markets_refresh.setMaximum(10000)
        self.events_refresh = QSpinBox(); self.events_refresh.setMaximum(10000)
        self.background = QCheckBox("Enable background sync")
        self.demo = QCheckBox("Use demo fallback")
        form.addRow("Data dir", self.data_dir)
        form.addRow("Logs dir", self.logs_dir)
        form.addRow("Markets refresh minutes", self.markets_refresh)
        form.addRow("Events refresh minutes", self.events_refresh)
        form.addRow("", self.background)
        form.addRow("", self.demo)
        layout.addLayout(form)
        save = QPushButton("Save settings")
        save.clicked.connect(self._save)
        test = QPushButton("Test connectivity")
        test.clicked.connect(on_test)
        layout.addWidget(save)
        layout.addWidget(test)

    def load_settings(self, s: AppSettings):
        self.data_dir.setText(s.data_dir)
        self.logs_dir.setText(s.logs_dir)
        self.markets_refresh.setValue(s.markets_refresh_minutes)
        self.events_refresh.setValue(s.events_refresh_minutes)
        self.background.setChecked(s.enable_background_sync)
        self.demo.setChecked(s.use_demo_fallback_data_if_live_fetch_fails)

    def _save(self):
        s = AppSettings(
            data_dir=self.data_dir.text(),
            logs_dir=self.logs_dir.text(),
            markets_refresh_minutes=self.markets_refresh.value(),
            events_refresh_minutes=self.events_refresh.value(),
            enable_background_sync=self.background.isChecked(),
            use_demo_fallback_data_if_live_fetch_fails=self.demo.isChecked(),
        )
        self.on_save(s)
