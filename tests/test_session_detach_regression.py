from app.db.migrations import bootstrap_database
from datetime import datetime

from app.db.repository import Repository
from app.services.event_service import EventService


def test_event_service_returns_objects_with_accessible_attributes_after_session_close():
    bootstrap_database()
    with Repository() as repo:
        repo.upsert_event(
            {
                "external_id": "detached_regression_event",
                "title": "Trump Test Event",
                "event_datetime": datetime.utcnow(),
                "location": "NY",
                "source_provider": "test",
                "source_url": "https://example.com/event",
                "event_type": "speech",
                "topic_tags_json": "[]",
                "entity_tags_json": "[]",
                "likely_qualifying": True,
                "source_confidence": 1.0,
                "raw_payload_json": "{}",
            }
        )

    events = EventService().list_events()

    titles = [e.title for e in events]
    assert "Trump Test Event" in titles
