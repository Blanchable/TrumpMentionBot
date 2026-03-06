from __future__ import annotations

import logging

from PySide6.QtCore import QObject, Signal


class LogBus(QObject):
    message = Signal(str, str)


class QtLogHandler(logging.Handler):
    def __init__(self, bus: LogBus):
        super().__init__()
        self.bus = bus

    def emit(self, record: logging.LogRecord) -> None:
        self.bus.message.emit(record.levelname, self.format(record))
