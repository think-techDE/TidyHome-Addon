import os
import sys
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path


APP_DIR = Path(__file__).resolve().parents[1] / "tidyhome" / "app"
sys.path.insert(0, str(APP_DIR))
os.environ.setdefault("DATA_DIR", tempfile.mkdtemp(prefix="tidyhome-test-"))

from models import Task  # noqa: E402
import storage  # noqa: E402


class PlanningFeatureTests(unittest.TestCase):
    def setUp(self):
        storage._db.drop_tables()

    def test_paused_tasks_stay_visible_but_do_not_count_as_overdue(self):
        task = storage.create_task(
            Task(
                name="Bad putzen",
                room="Bad",
                interval_days=7,
                assigned_to=["Ben"],
                start_date=(date.today() - timedelta(days=2)).isoformat(),
            )
        )

        paused = storage.pause_task(task.id, paused=True, reason="saisonal")

        self.assertTrue(paused.is_paused())
        self.assertEqual([t.id for t in storage.list_tasks()], [task.id])
        self.assertEqual(storage.list_tasks(overdue_only=True), [])

    def test_task_template_creates_task_with_defaults(self):
        template = storage.save_task_template(
            name="Auto",
            task_name="Auto saugen",
            room="Garage",
            interval_days=30,
            assigned_to=["Ben"],
            points=7,
            important=True,
            onetime=False,
            effort="medium",
        )

        task = storage.create_task_from_template(template["id"])

        self.assertIsNotNone(task)
        self.assertEqual(task.name, "Auto saugen")
        self.assertEqual(task.room, "Garage")
        self.assertEqual(task.assigned_to, ["Ben"])
        self.assertEqual(task.points, 7)
        self.assertTrue(task.important)
        self.assertFalse(task.onetime)
        self.assertEqual(task.effort, "medium")

    def test_backup_export_and_diagnostics_report_issues(self):
        storage.create_task(
            Task(
                name="Unbekannt",
                room="Alter Raum",
                interval_days=7,
                assigned_to=["Ghost"],
            )
        )

        backup = storage.export_backup_data()
        diagnostics = storage.diagnose_data(["Ben"], ["Kueche"])

        self.assertIn("tasks", backup["tables"])
        self.assertGreaterEqual(diagnostics["counts"]["issues"], 2)
        issue_types = {issue["type"] for issue in diagnostics["issues"]}
        self.assertIn("task_room", issue_types)
        self.assertIn("task_person", issue_types)


if __name__ == "__main__":
    unittest.main()
