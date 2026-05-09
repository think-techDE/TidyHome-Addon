import asyncio
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch


APP_DIR = Path(__file__).resolve().parents[1] / "tidyhome" / "app"
sys.path.insert(0, str(APP_DIR))
os.environ.setdefault("DATA_DIR", tempfile.mkdtemp(prefix="tidyhome-test-"))

from routes.settings import _person_settings_card  # noqa: E402
from routes.tasks import _task_form  # noqa: E402
import storage  # noqa: E402


class DummyRequest:
    headers = {}
    query_params = {}


class UiFormTests(unittest.TestCase):
    def setUp(self):
        storage._db.drop_tables()

    def test_task_form_prioritizes_important_marker(self):
        with patch("routes.tasks.get_areas", AsyncMock(return_value=["Kueche"])), \
             patch("routes.tasks.get_persons", AsyncMock(return_value=["Ben"])):
            response = asyncio.run(
                _task_form(DummyRequest(), "Neue Aufgabe", "tasks", "Anlegen", person="Ben")
            )

        html = response.body.decode("utf-8")

        self.assertIn('task-form-section-title">Aufgabe', html)
        self.assertIn("task-priority-card", html)
        self.assertLess(html.index("Als wichtig markieren"), html.index("Planung"))
        self.assertLess(html.index("Als wichtig markieren"), html.index("Raum"))

    def test_person_settings_card_uses_compact_sections(self):
        storage.save_person_settings(
            person="Ben",
            services=["notify.mobile_app_ben"],
            notify_time="08:00",
            enabled=True,
        )

        html = _person_settings_card(
            "Ben",
            ["Kueche", "Bad"],
            {"Ben"},
            base="/",
            show_admin_fields=True,
        )

        self.assertIn("person-settings-card", html)
        self.assertIn('settings-block-title">Benachrichtigung', html)
        self.assertIn('settings-block-title">Motivation', html)
        self.assertIn('settings-block-title">Rolle und Sicht', html)


if __name__ == "__main__":
    unittest.main()
