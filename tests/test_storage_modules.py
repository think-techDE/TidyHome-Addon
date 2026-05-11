import os
import sys
import tempfile
import unittest
from pathlib import Path


APP_DIR = Path(__file__).resolve().parents[1] / "tidyhome" / "app"
sys.path.insert(0, str(APP_DIR))
os.environ.setdefault("DATA_DIR", tempfile.mkdtemp(prefix="tidyhome-test-"))

from models import Comment, Project, Step, Task  # noqa: E402
import storage  # noqa: E402
import storage_people  # noqa: E402
import storage_projects  # noqa: E402
import storage_tasks  # noqa: E402


class StorageModuleTests(unittest.TestCase):
    def setUp(self):
        storage._db.drop_tables()

    def test_storage_facade_keeps_models_and_core_functions(self):
        self.assertIs(storage.Task, Task)
        self.assertIs(storage.Project, Project)
        self.assertIs(storage.Step, Step)
        self.assertIs(storage.Comment, Comment)

        for name in [
            "list_tasks", "mark_done", "list_projects", "complete_step",
            "get_person_settings", "get_person_achievements", "add_photo",
        ]:
            self.assertTrue(callable(getattr(storage, name)))

    def test_task_module_handles_templates_pause_history_and_scores(self):
        template = storage_tasks.save_task_template(
            "Muell Vorlage", "Biomuell", "Kueche", 7, ["Ben"],
            points=6, important=True, onetime=False, effort="low",
        )
        created = storage_tasks.create_task_from_template(
            template["id"], assigned_to=["Marina"], start_date="2026-05-10"
        )

        self.assertIsNotNone(created)
        self.assertEqual(created.assigned_to, ["Marina"])
        self.assertEqual(storage.get_task(created.id).name, "Biomuell")

        paused = storage_tasks.pause_task(created.id, True, "2099-01-01", "Urlaub")
        self.assertTrue(paused.is_paused())
        storage_tasks.snooze_task(created.id, "2099-01-02")
        done = storage_tasks.mark_done(created.id, done_by="Marina", done_at="2026-05-10")

        self.assertFalse(done.is_paused())
        self.assertEqual(storage_tasks.list_task_history()[0].id, created.id)
        events = storage_people.get_recent_score_events("Marina")
        self.assertEqual(events[0]["label"], "Biomuell")
        self.assertEqual(events[0]["points"], 6)

    def test_project_module_completes_steps_and_project_scores(self):
        project = storage_projects.create_project(
            Project(name="Keller", room="Keller", assigned_to="Ben")
        )
        step = storage_projects.add_step(
            Step(project_id=project.id, name="Kartons", assigned_to="Ben", points=4)
        )

        completed = storage_projects.complete_step(step.id, done_by="Ben")
        updated_project = storage_projects.get_project(project.id)

        self.assertTrue(completed.completed)
        self.assertTrue(updated_project.completed)
        self.assertEqual(storage_projects.project_export_rows()[0]["steps_done"], 1)
        events = storage_people.get_recent_score_events("Ben")
        self.assertEqual(events[0]["type"], "project")
        self.assertEqual(events[0]["label"], "Keller: Kartons")

    def test_people_module_handles_roles_filtering_and_history(self):
        storage_people.save_person_settings(
            "Ben", [], "08:00", True, role="child", can_see_children=True
        )
        storage_people.save_person_settings(
            "Marina", [], "08:00", True, role="child"
        )
        tasks = [
            Task(name="A", room="Kueche", interval_days=1, assigned_to=["Ben"]),
            Task(name="B", room="Bad", interval_days=1, assigned_to=["Marina"]),
            Task(name="C", room="Buero", interval_days=1, assigned_to=["Admin"]),
        ]

        visible = storage_people.filter_tasks_by_role(tasks, "Ben", set())

        self.assertEqual({t.name for t in visible}, {"A"})
        self.assertEqual(storage_people.list_people_by_role("child"), {"Ben", "Marina"})

        storage_people._add_score("Ben", 5, label="A", source_id="task-1")
        stats = storage_people.get_person_stats("Ben")
        history = storage_people.get_person_score_history("Ben")

        self.assertEqual(stats["total_points"], 5)
        self.assertEqual(history["weeks"][-1]["points"], 5)


if __name__ == "__main__":
    unittest.main()
