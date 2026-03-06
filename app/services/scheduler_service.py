from __future__ import annotations

from PySide6.QtCore import QObject, QTimer, Signal


class SchedulerService(QObject):
    tick = Signal(str)

    def __init__(self):
        super().__init__()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._on_timer)
        self.enabled = False

    def start(self, minutes: int) -> None:
        self.enabled = True
        self.timer.start(max(1, minutes) * 60_000)

    def stop(self) -> None:
        self.enabled = False
        self.timer.stop()

    def _on_timer(self) -> None:
        self.tick.emit("scheduled_full_sync")
