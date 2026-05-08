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

from models import Project, Step, Task  # noqa: E402
import reminders  # noqa: E402


class ReminderTests(unittest.TestCase):
    def test_task_recipients_exclude_sender_and_deduplicate(self):
        task = Task(
            name="Kueche aufraeumen",
            room="Kueche",
            interval_days=7,
            assigned_to=["Danny", "Petra", "Petra", "Mia"],
        )

        self.assertEqual(
            reminders.task_reminder_recipients(task, "Danny"),
            ["Petra", "Mia"],
        )

    def test_task_recipients_empty_when_sender_is_only_assignee(self):
        task = Task(
            name="Bad putzen",
            room="Bad",
            interval_days=7,
            assigned_to=["Danny"],
        )

        self.assertEqual(reminders.task_reminder_recipients(task, "Danny"), [])

    def test_task_reminder_sends_notification_and_writes_success_note(self):
        task = Task(
            name="Kueche aufraeumen",
            room="Kueche",
            interval_days=7,
            assigned_to=["Danny", "Petra"],
        )

        with (
            patch.object(reminders, "is_vacation_mode_active", return_value=False),
            patch.object(reminders, "_notify_services", return_value=["notify.mobile_petra"]),
            patch.object(reminders, "send_notification", new=AsyncMock(return_value=True)) as send,
            patch.object(reminders, "add_comment") as add_comment,
        ):
            sent = asyncio.run(
                reminders.send_task_reminder(
                    task, "Petra", "Bitte kurz erledigen", sender="Danny"
                )
            )

        self.assertTrue(sent)
        send.assert_awaited_once()
        add_comment.assert_called_once_with(
            "task",
            task.id,
            "Danny hat Petra erinnert: Bitte kurz erledigen",
            author="Danny",
        )

    def test_task_reminder_vacation_mode_skips_notification_and_writes_fallback_note(self):
        task = Task(
            name="Bad putzen",
            room="Bad",
            interval_days=7,
            assigned_to=["Danny", "Petra"],
        )

        with (
            patch.object(reminders, "is_vacation_mode_active", return_value=True),
            patch.object(reminders, "_notify_services", return_value=["notify.mobile_petra"]),
            patch.object(reminders, "send_notification", new=AsyncMock(return_value=True)) as send,
            patch.object(reminders, "add_comment") as add_comment,
        ):
            sent = asyncio.run(
                reminders.send_task_reminder(
                    task, "Petra", "Bitte kurz erledigen", sender="Danny"
                )
            )

        self.assertFalse(sent)
        send.assert_not_awaited()
        note = add_comment.call_args.args[2]
        self.assertIn("Danny wollte Petra erinnern", note)
        self.assertIn("kein aktives Gerät oder Versand fehlgeschlagen", note)

    def test_project_step_reminder_uses_project_comment(self):
        project = Project(name="Keller sortieren", room="Keller", assigned_to="Danny")
        step = Step(project_id=project.id, name="Kartons sortieren", assigned_to="Petra")

        with (
            patch.object(reminders, "is_vacation_mode_active", return_value=False),
            patch.object(reminders, "_notify_services", return_value=["notify.mobile_petra"]),
            patch.object(reminders, "send_notification", new=AsyncMock(return_value=True)),
            patch.object(reminders, "add_comment") as add_comment,
        ):
            sent = asyncio.run(
                reminders.send_project_step_reminder(
                    project, step, "Petra", "Bitte Schritt ansehen", sender="Danny"
                )
            )

        self.assertTrue(sent)
        add_comment.assert_called_once_with(
            "project",
            project.id,
            'Danny hat Petra an Schritt "Kartons sortieren" erinnert: Bitte Schritt ansehen',
            author="Danny",
        )


if __name__ == "__main__":
    unittest.main()
