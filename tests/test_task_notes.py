import os
import sys
import tempfile
import unittest
from pathlib import Path


APP_DIR = Path(__file__).resolve().parents[1] / "tidyhome" / "app"
sys.path.insert(0, str(APP_DIR))
os.environ.setdefault("DATA_DIR", tempfile.mkdtemp(prefix="tidyhome-test-"))

from models import Task  # noqa: E402
from routes.tasks import _save_initial_task_note  # noqa: E402
import storage  # noqa: E402


class TaskNoteTests(unittest.TestCase):
    def setUp(self):
        storage._db.drop_tables()

    def test_initial_task_note_is_saved_as_comment(self):
        task = storage.create_task(
            Task(
                name="Biomuell",
                room="Kueche",
                interval_days=0,
                assigned_to=["Danny"],
                onetime=True,
            )
        )

        saved = _save_initial_task_note(task, "Bitte vor der Arbeit rausstellen", author="Danny")

        comments = storage.list_comments("task", task.id)
        self.assertTrue(saved)
        self.assertEqual(len(comments), 1)
        self.assertEqual(comments[0].text, "Bitte vor der Arbeit rausstellen")
        self.assertEqual(comments[0].author, "Danny")

    def test_empty_initial_task_note_is_ignored(self):
        task = storage.create_task(
            Task(
                name="Biomuell",
                room="Kueche",
                interval_days=0,
                assigned_to=["Danny"],
                onetime=True,
            )
        )

        saved = _save_initial_task_note(task, "   ", author="Danny")

        self.assertFalse(saved)
        self.assertEqual(storage.list_comments("task", task.id), [])


if __name__ == "__main__":
    unittest.main()
