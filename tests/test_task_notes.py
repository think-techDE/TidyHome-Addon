import os
import asyncio
import shutil
import sys
import tempfile
import unittest
from pathlib import Path


APP_DIR = Path(__file__).resolve().parents[1] / "tidyhome" / "app"
sys.path.insert(0, str(APP_DIR))
os.environ.setdefault("DATA_DIR", tempfile.mkdtemp(prefix="tidyhome-test-"))

from models import Task  # noqa: E402
from routes.tasks import _save_initial_task_note, _save_initial_task_photo  # noqa: E402
import storage  # noqa: E402


class FakeUpload:
    filename = "before.jpg"
    content_type = "image/jpeg"

    async def read(self):
        return b"image-bytes"


class TaskNoteTests(unittest.TestCase):
    def setUp(self):
        storage._db.drop_tables()
        self.photo_dir = tempfile.mkdtemp(prefix="tidyhome-photos-")
        self.old_photo_dir = storage.PHOTO_DIR
        storage.PHOTO_DIR = self.photo_dir

    def tearDown(self):
        storage.PHOTO_DIR = self.old_photo_dir
        shutil.rmtree(self.photo_dir, ignore_errors=True)

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

    def test_initial_task_photo_is_saved_as_before_photo(self):
        task = storage.create_task(
            Task(
                name="Keller aufraeumen",
                room="Keller",
                interval_days=0,
                assigned_to=["Danny"],
                onetime=True,
            )
        )

        saved = asyncio.run(
            _save_initial_task_photo(task, author="Danny", photo_camera=FakeUpload())
        )

        photos = storage.list_photos("task", task.id)
        self.assertTrue(saved)
        self.assertEqual(len(photos), 1)
        self.assertEqual(photos[0]["photo_type"], "before")
        self.assertEqual(photos[0]["author"], "Danny")


if __name__ == "__main__":
    unittest.main()
