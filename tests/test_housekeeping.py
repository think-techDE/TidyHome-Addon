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

from render import render  # noqa: E402
from routes.dashboard import dashboard  # noqa: E402
from routes.housekeeping import housekeeping_dashboard, housekeeping_log  # noqa: E402
import storage  # noqa: E402


class DummyRequest:
    query_params = {}

    def __init__(self, person: str):
        self.headers = {"X-Remote-User-Display-Name": person}


def save_person(person: str, role: str):
    storage.save_person_settings(
        person=person,
        services=[],
        notify_time="08:00",
        enabled=False,
        role=role,
    )


class HousekeepingTests(unittest.TestCase):
    def setUp(self):
        storage._db.drop_tables()

    def test_housekeeping_summary_calculates_hours_and_costs(self):
        save_person("Marina", "housekeeper")
        storage.save_housekeeper_wage("Marina", "15,50")

        entry = storage.add_housekeeping_entry(
            "Marina",
            "2026-05-09",
            "09:00",
            "12:30",
            break_minutes=30,
            note="Kueche",
            created_by="Ben",
        )

        summary = storage.get_housekeeping_month_summary(month="2026-05")

        self.assertIsNotNone(entry)
        self.assertEqual(summary["total_hours"], 3.0)
        self.assertEqual(summary["total_cost"], 46.5)
        self.assertEqual(summary["people"][0]["hourly_wage"], 15.5)

    def test_housekeeping_entry_can_be_corrected_and_deleted(self):
        save_person("Marina", "housekeeper")
        entry = storage.add_housekeeping_entry(
            "Marina", "2026-05-09", "09:00", "11:00", break_minutes=0
        )

        corrected = storage.update_housekeeping_entry(
            entry["id"], "Marina", "2026-05-09", "09:00", "12:00", break_minutes=15
        )

        self.assertEqual(storage.housekeeping_entry_hours(corrected), 2.75)
        self.assertTrue(storage.delete_housekeeping_entry(entry["id"]))
        self.assertEqual(storage.list_housekeeping_entries("Marina", "2026-05"), [])

    def test_parent_dashboard_renders_housekeeper_management(self):
        save_person("Ben", "parent")
        save_person("Marina", "housekeeper")
        storage.save_housekeeper_wage("Marina", 18)

        response = asyncio.run(
            housekeeping_dashboard(DummyRequest("Ben"), month="2026-05")
        )
        html = response.body.decode("utf-8")

        self.assertIn("Arbeitszeiten", html)
        self.assertIn("Marina", html)
        self.assertIn("Stundenlohn", html)
        self.assertIn("Arbeitszeit erfassen", html)

    def test_housekeeper_log_renders_personal_earnings(self):
        save_person("Marina", "housekeeper")
        storage.save_housekeeper_wage("Marina", 20)
        storage.add_housekeeping_entry(
            "Marina", "2026-05-09", "10:00", "12:00", created_by="Marina"
        )

        response = asyncio.run(
            housekeeping_log(DummyRequest("Marina"), month="2026-05")
        )
        html = response.body.decode("utf-8")

        self.assertIn("Arbeitszeit eintragen", html)
        self.assertIn("40,00", html)
        self.assertIn("Erarbeitet", html)

    def test_admin_menu_links_to_housekeeping_area(self):
        save_person("Ben", "parent")
        storage.save_admins(["Ben"])

        html = render("", DummyRequest("Ben"), person="Ben").body.decode("utf-8")

        self.assertIn("Haushaltshilfen", html)
        self.assertIn('href="/housekeeping"', html)
        self.assertIn("Arbeitszeiten verwalten", html)

    def test_admin_viewing_housekeeper_sees_management_not_personal_work_card(self):
        save_person("Ben", "parent")
        save_person("Marina", "housekeeper")
        storage.save_admins(["Ben"])

        with patch("routes.dashboard.get_areas", AsyncMock(return_value=[])):
            response = asyncio.run(dashboard(DummyRequest("Ben"), p="Marina"))

        html = response.body.decode("utf-8")

        self.assertIn("Haushaltshilfen", html)
        self.assertIn("Arbeitszeiten verwalten", html)
        self.assertNotIn("Arbeitszeit diesen Monat", html)


if __name__ == "__main__":
    unittest.main()
