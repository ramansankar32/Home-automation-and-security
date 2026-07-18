import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import src.database as database

# Redirect DB to a temp file so tests don't touch real data
database.DB_PATH = tempfile.mktemp(suffix=".db")

from src.automation import AutomationEngine  # noqa: E402


def test_engine_initial_state():
    engine = AutomationEngine(poll_interval=100)
    assert engine.is_armed() is False


def test_arm_disarm():
    engine = AutomationEngine(poll_interval=100)
    engine.arm()
    assert engine.is_armed() is True
    engine.disarm()
    assert engine.is_armed() is False


def test_lights_toggle():
    engine = AutomationEngine(poll_interval=100)
    engine.set_lights(True)
    assert database.get_state("lights") == "on"
    engine.set_lights(False)
    assert database.get_state("lights") == "off"


def test_event_logging():
    database.log_event("test", "sample_event", "hello", "info")
    events = database.recent_events(limit=5)
    assert any(e["event_type"] == "sample_event" for e in events)


if __name__ == "__main__":
    test_engine_initial_state()
    test_arm_disarm()
    test_lights_toggle()
    test_event_logging()
    print("All tests passed.")
