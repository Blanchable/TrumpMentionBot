from __future__ import annotations

import json
import logging
import os
from datetime import datetime

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QListWidget, QListWidgetItem, QMainWindow, QMessageBox, QSplitter, QStackedWidget
from sqlalchemy import select

from app.config import AppSettings
from app.constants import DEFAULT_WINDOW_HEIGHT, DEFAULT_WINDOW_WIDTH
from app.db.models import Event, Outcome, Prediction, TranscriptMatch
from app.db.repository import Repository
from app.gui.screens.dashboard_screen import DashboardScreen
from app.gui.screens.events_screen import EventsScreen
from app.gui.screens.logs_screen import LogsScreen
from app.gui.screens.markets_screen import MarketsScreen
from app.gui.screens.matcher_screen import MatcherScreen
from app.gui.screens.predictions_screen import PredictionsScreen
from app.gui.screens.settings_screen import SettingsScreen
from app.gui.screens.transcripts_screen import TranscriptsScreen
from app.paths import LOGS_DIR
from app.services.event_service import EventService
from app.services.market_service import MarketService
from app.services.matcher_service import MatcherService
from app.services.prediction_service import PredictionService
from app.services.transcript_service import TranscriptService

log = logging.getLogger(__name__)


class AppWindow(QMainWindow):
    def __init__(self, settings: AppSettings):
        super().__init__()
        self.settings = settings
        self.market_service = MarketService(settings.request_timeout_seconds)
        self.event_service = EventService(settings.request_timeout_seconds)
        self.transcript_service = TranscriptService(settings.request_timeout_seconds)
        self.matcher_service = MatcherService()
        self.prediction_service = PredictionService()

        self.setWindowTitle("Trump Mentions Engine")
        self.resize(DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT)

        splitter = QSplitter()
        self.nav = QListWidget()
        self.nav.setFixedWidth(220)
        self.stack = QStackedWidget()
        splitter.addWidget(self.nav)
        splitter.addWidget(self.stack)
        self.setCentralWidget(splitter)

        self.dashboard = DashboardScreen(self._dashboard_action)
        self.markets = MarketsScreen(lambda: self.refresh_markets())
        self.events = EventsScreen(lambda: self.refresh_events())
        self.transcripts = TranscriptsScreen(lambda: self.refresh_transcripts())
        self.predictions = PredictionsScreen(lambda: self.recompute_model())
        self.matcher = MatcherScreen()
        self.logs = LogsScreen(self.open_logs_folder)
        self.settings_screen = SettingsScreen(self.save_settings, self.test_connectivity)

        screens = [
            ("Dashboard", self.dashboard),
            ("Markets", self.markets),
            ("Events", self.events),
            ("Transcripts", self.transcripts),
            ("Model / Predictions", self.predictions),
            ("Rules / Matcher", self.matcher),
            ("Logs", self.logs),
            ("Settings", self.settings_screen),
        ]
        for name, widget in screens:
            self.nav.addItem(QListWidgetItem(name))
            self.stack.addWidget(widget)
        self.nav.currentRowChanged.connect(self.stack.setCurrentIndex)
        self.nav.setCurrentRow(0)

        self.settings_screen.load_settings(settings)
        self.refresh_all_views()

    def append_log(self, level: str, text: str):
        self.logs.append(level, text)

    def _dashboard_action(self, key: str):
        if key == "markets":
            self.refresh_markets()
        elif key == "events":
            self.refresh_events()
        elif key == "transcripts":
            self.refresh_transcripts()
        elif key == "model":
            self.recompute_model()
        elif key == "full":
            self.full_sync()

    def refresh_markets(self):
        n = self.market_service.sync()
        log.info("Markets refreshed: %s", n)
        self.refresh_all_views()

    def refresh_events(self):
        n = self.event_service.sync()
        log.info("Events refreshed: %s", n)
        self.refresh_all_views()

    def refresh_transcripts(self):
        n = self.transcript_service.sync()
        log.info("Transcripts refreshed: %s", n)
        self.refresh_all_views()

    def recompute_model(self):
        self.matcher_service.run_all()
        n = self.prediction_service.recompute()
        log.info("Predictions recomputed: %s", n)
        self.refresh_all_views()

    def full_sync(self):
        self.refresh_markets()
        self.refresh_events()
        self.refresh_transcripts()
        self.recompute_model()

    def refresh_all_views(self):
        market_rows = self.market_service.list_outcomes()
        self.markets.set_rows(
            [
                [
                    m.title,
                    m.slug,
                    o.canonical_term,
                    o.threshold_type,
                    f"{o.yes_price:.3f}",
                    f"{o.no_price:.3f}",
                    f"{o.implied_probability:.3f}",
                    o.notes_json,
                    m.scope_type,
                    m.resolution_end_at,
                    o.last_seen_at,
                ]
                for m, o in market_rows
            ]
        )

        events = self.event_service.list_events()
        self.events.set_rows(
            [
                [e.title, e.event_datetime, e.source_provider, e.event_type, e.location, e.likely_qualifying, e.topic_tags_json, "n/a", 0]
                for e in events
            ],
            [f"Summary: {e.title}\nSource: {e.source_url}\nEntities: {e.entity_tags_json}" for e in events],
        )

        transcripts = self.transcript_service.list_transcripts()
        self.transcripts.set_rows(
            [
                [e.title, t.source_provider, t.fetch_status, len(t.cleaned_text), t.quality_score, t.is_timestamped, t.fetched_at]
                for t, e in transcripts
            ],
            [t.original_text for t, _ in transcripts],
        )

        preds = self.prediction_service.list_predictions()
        pred_rows = []
        for p, o in preds:
            comp = json.loads(p.component_scores_json or "{}")
            pred_rows.append(
                [
                    o.canonical_term,
                    o.threshold_value,
                    round(p.market_probability, 3),
                    round(p.model_probability, 3),
                    round(p.edge, 3),
                    round(p.confidence_score, 3),
                    "n/a",
                    round(comp.get("baseline_frequency_score", 0), 3),
                    round(comp.get("recent_frequency_score", 0), 3),
                    round(comp.get("topic_entity_relevance_score", 0), 3),
                    p.reason_summary,
                ]
            )
        self.predictions.set_rows(pred_rows)

        with Repository() as repo:
            matches = repo.session.execute(select(TranscriptMatch, Outcome).join(Outcome, Outcome.id == TranscriptMatch.outcome_id)).all()
        self.matcher.set_rows(
            [
                [
                    o.canonical_term,
                    o.threshold_value,
                    o.alias_json,
                    m.raw_count,
                    m.adjusted_count,
                    m.matched_spans_json[:80],
                    m.notes_json,
                ]
                for m, o in matches
            ]
        )

        last = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        positive = len([1 for p, _ in preds if p.edge > 0.05])
        negative = len([1 for p, _ in preds if p.edge < -0.05])
        self.dashboard.update_summary(
            f"Active markets: {len(market_rows)} | Events: {len(events)} | Transcripts: {len(transcripts)} | "
            f"Last refresh: {last} | +Edge: {positive} | -Edge: {negative}"
        )
        self.dashboard.set_rows(pred_rows[:15])

    def open_logs_folder(self):
        os.startfile(str(LOGS_DIR)) if hasattr(os, "startfile") else QMessageBox.information(self, "Logs", str(LOGS_DIR))

    def save_settings(self, settings: AppSettings):
        with Repository() as repo:
            repo.save_settings(settings)
        self.settings = settings
        QMessageBox.information(self, "Settings", "Saved settings")

    def test_connectivity(self):
        try:
            m = self.market_service.provider.fetch()
            e = self.event_service.provider.fetch()
            QMessageBox.information(self, "Connectivity", f"Markets rows: {len(m)} | Event rows: {len(e)}")
        except Exception as exc:
            QMessageBox.warning(self, "Connectivity", str(exc))
