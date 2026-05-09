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
from routes.housekeeping import (housekeeping_dashboard, housekeeping_entry_create,
                                 housekeeping_export_csv, housekeeping_export_pdf,
                                 housekeeping_log, housekeeping_status_save,
                                 housekeeping_wage_update)  # noqa: E402
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
        storage.save_housekeeper_wage("Marina", "15,50", valid_from="2026-01-01")

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

    def test_housekeeping_summary_uses_wage_valid_on_work_date(self):
        save_person("Marina", "housekeeper")
        storage.save_housekeeper_wage(
            "Marina", "15,00", valid_from="2026-01-01", valid_to="2026-05-31"
        )
        storage.save_housekeeper_wage("Marina", "20,00", valid_from="2026-06-01")
        storage.add_housekeeping_entry(
            "Marina", "2026-05-20", "10:00", "12:00", created_by="Ben"
        )
        storage.add_housekeeping_entry(
            "Marina", "2026-06-20", "10:00", "12:00", created_by="Ben"
        )

        may = storage.get_housekeeping_month_summary("Marina", "2026-05")
        june = storage.get_housekeeping_month_summary("Marina", "2026-06")

        self.assertEqual(may["total_cost"], 30.0)
        self.assertEqual(june["total_cost"], 40.0)
        self.assertEqual(storage.get_housekeeper_wage("Marina", "2026-05-20"), 15.0)
        self.assertEqual(storage.get_housekeeper_wage("Marina", "2026-06-20"), 20.0)

    def test_housekeeper_wage_history_can_be_corrected(self):
        save_person("Ben", "parent")
        save_person("Marina", "housekeeper")
        wage = storage.save_housekeeper_wage(
            "Marina", "15,00", valid_from="2026-01-01", valid_to="2026-05-31"
        )

        response = asyncio.run(housekeeping_wage_update(
            wage["id"],
            DummyRequest("Ben"),
            person="Marina",
            hourly_wage="16,50",
            valid_from="2026-02-01",
            valid_to="2026-06-30",
            month="2026-05",
            return_p="Ben",
        ))

        self.assertEqual(response.status_code, 303)
        self.assertEqual(storage.get_housekeeper_wage("Marina", "2026-02-15"), 16.5)
        self.assertEqual(storage.list_housekeeper_wages("Marina")[0]["valid_to"], "2026-06-30")

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
        storage.save_housekeeper_wage("Marina", 18, valid_from="2026-01-01")

        response = asyncio.run(
            housekeeping_dashboard(DummyRequest("Ben"), month="2026-05")
        )
        html = response.body.decode("utf-8")

        self.assertIn("Arbeitszeiten", html)
        self.assertIn("Marina", html)
        self.assertIn("housekeeping-foldout", html)
        self.assertIn("housekeeping-subdetails", html)
        self.assertIn("billing-status-form", html)
        self.assertIn("CSV", html)
        self.assertIn("PDF", html)
        self.assertIn("Stundenlohn", html)
        self.assertIn("Stundensatz und Historie", html)
        self.assertIn("Gültig ab", html)
        self.assertIn("Stundensatz hinzufügen", html)
        self.assertIn("ab 01.01.2026", html)
        self.assertIn("Arbeitszeit erfassen", html)

    def test_housekeeper_log_renders_personal_earnings(self):
        save_person("Marina", "housekeeper")
        storage.save_housekeeper_wage("Marina", 20, valid_from="2026-01-01")
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

    def test_billing_status_and_exports(self):
        save_person("Ben", "parent")
        save_person("Marina", "housekeeper")
        storage.save_housekeeper_wage("Marina", 20, valid_from="2026-01-01")
        storage.add_housekeeping_entry(
            "Marina", "2026-05-09", "10:00", "12:00", created_by="Marina"
        )

        status_response = asyncio.run(housekeeping_status_save(
            DummyRequest("Ben"),
            person="Marina",
            month="2026-05",
            status="reviewed",
            return_p="Ben",
        ))
        csv_response = asyncio.run(housekeeping_export_csv(
            DummyRequest("Ben"), person="Marina", month="2026-05"
        ))
        pdf_response = asyncio.run(housekeeping_export_pdf(
            DummyRequest("Ben"), person="Marina", month="2026-05"
        ))

        self.assertEqual(status_response.status_code, 303)
        self.assertEqual(storage.get_housekeeping_billing("Marina", "2026-05")["status"], "reviewed")
        self.assertIn("Marina;2026-05", csv_response.body.decode("utf-8"))
        self.assertEqual(pdf_response.media_type, "application/pdf")
        self.assertTrue(pdf_response.body.startswith(b"%PDF-1.4"))

    def test_paid_month_is_read_only_for_housekeeper(self):
        save_person("Marina", "housekeeper")
        storage.save_housekeeper_wage("Marina", 20, valid_from="2026-01-01")
        storage.set_housekeeping_billing_status("Marina", "2026-05", "paid", updated_by="Ben")

        response = asyncio.run(
            housekeeping_log(DummyRequest("Marina"), month="2026-05")
        )
        html = response.body.decode("utf-8")

        self.assertIn("nur noch lesend", html)
        self.assertNotIn("Arbeitszeit speichern", html)
        with self.assertRaises(Exception):
            asyncio.run(housekeeping_entry_create(
                DummyRequest("Marina"),
                person="Marina",
                work_date="2026-05-10",
                start_time="10:00",
                end_time="11:00",
                return_p="Marina",
            ))

    def test_admin_menu_links_to_housekeeping_area(self):
        save_person("Ben", "parent")
        storage.save_admins(["Ben"])

        html = render("", DummyRequest("Ben"), person="Ben").body.decode("utf-8")

        self.assertIn("Haushaltshilfen", html)
        self.assertIn('href="/housekeeping"', html)
        self.assertIn("Arbeitszeiten verwalten", html)

    def test_admin_viewing_housekeeper_sees_no_housekeeping_home_card(self):
        save_person("Ben", "parent")
        save_person("Marina", "housekeeper")
        storage.save_admins(["Ben"])

        with patch("routes.dashboard.get_areas", AsyncMock(return_value=[])):
            response = asyncio.run(dashboard(DummyRequest("Ben"), p="Marina"))

        html = response.body.decode("utf-8")

        self.assertNotIn("housekeeping-home-card", html)
        self.assertNotIn("Gesamtkosten diesen Monat", html)
        self.assertNotIn("Arbeitszeit diesen Monat", html)


if __name__ == "__main__":
    unittest.main()
