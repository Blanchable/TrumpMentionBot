from __future__ import annotations

import logging
import sys

from PySide6.QtWidgets import QApplication

from app.bootstrap import bootstrap_app
from app.gui.app_window import AppWindow
from app.gui.log_bus import LogBus, QtLogHandler
from app.gui.theme import DARK_QSS


def main() -> int:
    settings = bootstrap_app()
    app = QApplication(sys.argv)
    app.setStyleSheet(DARK_QSS)

    bus = LogBus()
    handler = QtLogHandler(bus)
    handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s"))
    logging.getLogger().addHandler(handler)

    window = AppWindow(settings)
    bus.message.connect(window.append_log)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
