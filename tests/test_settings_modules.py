import os
import sys
import tempfile
import unittest
from pathlib import Path


APP_DIR = Path(__file__).resolve().parents[1] / "tidyhome" / "app"
sys.path.insert(0, str(APP_DIR))
os.environ.setdefault("DATA_DIR", tempfile.mkdtemp(prefix="tidyhome-test-"))

from settings_admin_ui import admin_page_content  # noqa: E402
from settings_exports import _csv_response, json_backup_response  # noqa: E402
from settings_ui import _person_settings_card  # noqa: E402
import storage  # noqa: E402


class SettingsModuleTests(unittest.TestCase):
    def setUp(self):
        storage._db.drop_tables()

    def test_csv_response_uses_semicolon_and_attachment_header(self):
        response = _csv_response("rows.csv", [{"name": "Ben", "points": 5}])

        body = response.body.decode("utf-8")
        self.assertIn("name;points", body)
        self.assertIn("Ben;5", body)
        self.assertEqual(response.headers["content-disposition"], 'attachment; filename="rows.csv"')

    def test_json_backup_response_uses_json_attachment(self):
        response = json_backup_response({"tables": {"tasks": []}}, "backup.json")

        self.assertIn('"tables"', response.body.decode("utf-8"))
        self.assertEqual(response.media_type, "application/json; charset=utf-8")
        self.assertEqual(response.headers["content-disposition"], 'attachment; filename="backup.json"')

    def test_person_settings_card_renders_profile_sections(self):
        storage.save_person_settings("Ben", ["notify.mobile_app_ben"], "08:00", True)

        html = _person_settings_card("Ben", ["Kueche"], {"Ben"}, base="/")

        self.assertIn("person-settings-card", html)
        self.assertIn('name="notify_time"', html)
        self.assertIn('name="weekly_goal"', html)
        self.assertIn('name="vacation_enabled"', html)

    def test_admin_page_content_renders_admin_sections(self):
        html = admin_page_content(
            base="/",
            admins={"Ben"},
            persons=["Ben"],
            areas=["Kueche"],
            available_svcs=["notify.mobile_app_ben"],
        )

        self.assertIn("admin-rights", html)
        self.assertIn("admin-data", html)
        self.assertIn("admin-room-icons", html)
        self.assertIn("admin-people", html)

    def test_admin_page_content_interpolates_status_hints(self):
        html = admin_page_content(
            base="/",
            admins=set(),
            persons=["Ben"],
            areas=["Kueche"],
            saved="1",
        )

        self.assertIn("admin-devices", html)
        self.assertNotIn('{tr("settings.saved")}', html)
        self.assertNotIn('{tr("settings.no_admins_hint")}', html)


if __name__ == "__main__":
    unittest.main()
