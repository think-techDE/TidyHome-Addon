import os
import sys
import tempfile
import unittest
from pathlib import Path


APP_DIR = Path(__file__).resolve().parents[1] / "tidyhome" / "app"
sys.path.insert(0, str(APP_DIR))
os.environ.setdefault("DATA_DIR", tempfile.mkdtemp(prefix="tidyhome-test-"))

from models import Project, Step, Task  # noqa: E402
import storage  # noqa: E402


class ScoreTests(unittest.TestCase):
    def setUp(self):
        storage._db.drop_tables()

    def test_task_done_writes_labeled_score_event(self):
        task = storage.create_task(
            Task(
                name="Biomuell",
                room="Kueche",
                interval_days=7,
                assigned_to=["Danny"],
                points=6,
            )
        )

        storage.mark_done(task.id, done_by="Danny")

        events = storage.get_recent_score_events("Danny")
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["label"], "Biomuell")
        self.assertEqual(events[0]["points"], 6)
        self.assertEqual(events[0]["type"], "task")

    def test_project_step_score_event_includes_project_context(self):
        project = storage.create_project(
            Project(name="Keller aufraeumen", room="Keller", assigned_to="Danny")
        )
        step = storage.add_step(
            Step(
                project_id=project.id,
                name="Kartons sortieren",
                assigned_to="Danny",
                points=4,
            )
        )

        storage.complete_step(step.id, done_by="Danny")

        events = storage.get_recent_score_events("Danny")
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["label"], "Keller aufraeumen: Kartons sortieren")
        self.assertEqual(events[0]["points"], 4)
        self.assertEqual(events[0]["type"], "project")

    def test_achievements_and_history_use_score_log(self):
        task = storage.create_task(
            Task(
                name="Biomuell",
                room="Kueche",
                interval_days=7,
                assigned_to=["Danny"],
                points=10,
            )
        )

        storage.mark_done(task.id, done_by="Danny")

        achievements = storage.get_person_achievements("Danny")
        history = storage.get_person_score_history("Danny")

        unlocked = {a["id"] for a in achievements if a["unlocked"]}
        self.assertIn("first_task", unlocked)
        self.assertIn("points_100", {a["id"] for a in achievements})
        self.assertEqual(history["weeks"][-1]["points"], 10)
        self.assertEqual(history["months"][-1]["points"], 10)


if __name__ == "__main__":
    unittest.main()
