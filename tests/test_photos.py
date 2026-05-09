import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path


APP_DIR = Path(__file__).resolve().parents[1] / "tidyhome" / "app"
sys.path.insert(0, str(APP_DIR))
os.environ.setdefault("DATA_DIR", tempfile.mkdtemp(prefix="tidyhome-test-"))

import storage  # noqa: E402
import render  # noqa: E402


class PhotoTests(unittest.TestCase):
    def setUp(self):
        storage._db.drop_tables()
        self.photo_dir = tempfile.mkdtemp(prefix="tidyhome-photos-")
        self.old_photo_dir = storage.PHOTO_DIR
        storage.PHOTO_DIR = self.photo_dir

    def tearDown(self):
        storage.PHOTO_DIR = self.old_photo_dir
        shutil.rmtree(self.photo_dir, ignore_errors=True)

    def test_add_photo_persists_file_and_metadata(self):
        photo = storage.add_photo(
            "task", "task-1", "after", "done.png", "image/png",
            b"image-bytes", author="Danny"
        )

        self.assertIsNotNone(photo)
        self.assertEqual(photo["entity_type"], "task")
        self.assertEqual(photo["entity_id"], "task-1")
        self.assertEqual(photo["photo_type"], "after")
        self.assertTrue(photo["filename"].endswith(".png"))
        self.assertTrue(os.path.exists(os.path.join(self.photo_dir, photo["filename"])))
        self.assertEqual(storage.list_photos("task", "task-1")[0]["author"], "Danny")

    def test_delete_photo_removes_file_and_record(self):
        photo = storage.add_photo(
            "project", "project-1", "before", "before.jpg", "image/jpeg",
            b"image-bytes"
        )

        self.assertTrue(storage.delete_photo(photo["id"], "project", "project-1"))

        self.assertFalse(os.path.exists(os.path.join(self.photo_dir, photo["filename"])))
        self.assertEqual(storage.list_photos("project", "project-1"), [])

    def test_delete_photo_rejects_wrong_entity(self):
        photo = storage.add_photo(
            "step", "step-1", "before", "before.jpg", "image/jpeg",
            b"image-bytes"
        )

        self.assertFalse(storage.delete_photo(photo["id"], "task", "task-1"))
        self.assertTrue(os.path.exists(os.path.join(self.photo_dir, photo["filename"])))
        self.assertEqual(len(storage.list_photos("step", "step-1")), 1)

    def test_add_photo_rejects_non_image_content_type(self):
        photo = storage.add_photo(
            "task", "task-1", "before", "notes.txt", "text/plain",
            b"not-an-image"
        )

        self.assertIsNone(photo)
        self.assertEqual(os.listdir(self.photo_dir), [])

    def test_photos_card_offers_live_camera_and_file_fallback(self):
        html = render.photos_card("task", "task-1", "tasks/task-1/photos", "Ben")

        self.assertIn("camera-start", html)
        self.assertIn("Kamera öffnen", html)
        self.assertIn("camera-preview", html)
        self.assertIn("photo-file-input", html)
        self.assertIn('accept="image/*,android/force-camera-workaround"', html)
        self.assertIn('capture="environment"', html)
        self.assertIn("nativen Kamera-/Dateidialog", html)


if __name__ == "__main__":
    unittest.main()
