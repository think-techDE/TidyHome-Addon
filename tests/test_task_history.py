import os
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path


APP_DIR = Path(__file__).resolve().parents[1] / "tidyhome" / "app"
sys.path.insert(0, str(APP_DIR))
os.environ.setdefault("DATA_DIR", tempfile.mkdtemp(prefix="tidyhome-test-"))

from models import Task  # noqa: E402
import storage  # noqa: E402


class TaskHistoryTests(unittest.TestCase):
    def setUp(self):
        storage._db.drop_tables()

    def test_onetime_task_is_archived_and_can_be_reactivated(self):
        task = storage.create_task(
            Task(
                name="Fenster putzen",
                room="Wohnzimmer",
                interval_days=0,
                assigned_to=["Danny"],
                onetime=True,
            )
        )

        done = storage.mark_done(task.id, done_by="Danny")

        self.assertFalse(done.active)
        self.assertEqual([t.id for t in storage.list_task_history()], [task.id])

        active = storage.reactivate_task(task.id)

        self.assertTrue(active.active)
        self.assertIsNone(active.last_done)
        self.assertIsNone(active.snooze_until)
        self.assertEqual(active.start_date, date.today().isoformat())

    def test_history_includes_completed_recurring_tasks(self):
        task = storage.create_task(
            Task(
                name="Biomuell",
                room="Kueche",
                interval_days=7,
                assigned_to=["Danny"],
            )
        )

        storage.mark_done(task.id, done_by="Danny")

        history = storage.list_task_history()
        self.assertEqual([t.id for t in history], [task.id])
        self.assertTrue(history[0].active)


if __name__ == "__main__":
    unittest.main()
