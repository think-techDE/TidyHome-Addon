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
from routes.dashboard import due_today_or_overdue  # noqa: E402


class DashboardTests(unittest.TestCase):
    def test_due_today_or_overdue_excludes_future_tasks(self):
        today = date.today()
        overdue = Task(
            name="Alt",
            room="Kueche",
            interval_days=7,
            assigned_to=["Danny"],
            start_date=(today - timedelta(days=1)).isoformat(),
        )
        due_today = Task(
            name="Heute",
            room="Kueche",
            interval_days=7,
            assigned_to=["Danny"],
            start_date=today.isoformat(),
        )
        future = Task(
            name="Spaeter",
            room="Kueche",
            interval_days=7,
            assigned_to=["Danny"],
            start_date=(today + timedelta(days=1)).isoformat(),
        )

        result = due_today_or_overdue([future, due_today, overdue])

        self.assertEqual([t.name for t in result], ["Alt", "Heute"])


if __name__ == "__main__":
    unittest.main()
