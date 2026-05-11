import os
import sys
import tempfile
import unittest
from pathlib import Path


APP_DIR = Path(__file__).resolve().parents[1] / "tidyhome" / "app"
sys.path.insert(0, str(APP_DIR))
os.environ.setdefault("DATA_DIR", tempfile.mkdtemp(prefix="tidyhome-test-"))

from access import (can_create_housekeeping_entry, can_group_tasks_by_person,
                    can_manage_housekeeping, can_view_project, is_housekeeper,
                    task_group_people, visible_project_steps,
                    visible_projects_for_person, visible_tasks_for_person)
from models import Project, Step, Task  # noqa: E402
import storage  # noqa: E402


def save_person(person: str, role: str = "member", can_see_children: bool = False):
    storage.save_person_settings(
        person=person,
        services=[],
        notify_time="08:00",
        enabled=True,
        role=role,
        can_see_children=can_see_children,
    )


class AccessTests(unittest.TestCase):
    def setUp(self):
        storage._db.drop_tables()

    def test_task_visibility_keeps_standard_views_personal(self):
        storage.save_admins(["Admin"])
        save_person("Admin", "parent")
        save_person("Parent", "parent")
        save_person("Kid", "child")
        save_person("Member", "member")
        tasks = [
            Task(name="Admin", room="Kueche", interval_days=1, assigned_to=["Admin"]),
            Task(name="Parent", room="Kueche", interval_days=1, assigned_to=["Parent"]),
            Task(name="Kid", room="Kueche", interval_days=1, assigned_to=["Kid"]),
            Task(name="Member", room="Kueche", interval_days=1, assigned_to=["Member"]),
        ]

        self.assertEqual(
            {task.name for task in visible_tasks_for_person(tasks, "Admin", {"Admin"})},
            {"Admin"},
        )
        self.assertEqual(
            {task.name for task in visible_tasks_for_person(tasks, "Parent", {"Admin"})},
            {"Parent"},
        )

    def test_managed_task_visibility_supports_admins_and_parents(self):
        storage.save_admins(["Admin"])
        save_person("Admin", "parent")
        save_person("Parent", "parent")
        save_person("Kid", "child")
        save_person("Member", "member")
        tasks = [
            Task(name="Admin", room="Kueche", interval_days=1, assigned_to=["Admin"]),
            Task(name="Parent", room="Kueche", interval_days=1, assigned_to=["Parent"]),
            Task(name="Kid", room="Kueche", interval_days=1, assigned_to=["Kid"]),
            Task(name="Member", room="Kueche", interval_days=1, assigned_to=["Member"]),
        ]

        self.assertTrue(can_group_tasks_by_person("Admin", {"Admin"}))
        self.assertTrue(can_group_tasks_by_person("Parent", {"Admin"}))
        self.assertEqual(
            {task.name for task in visible_tasks_for_person(
                tasks, "Admin", {"Admin"}, include_managed=True
            )},
            {"Admin", "Parent", "Kid", "Member"},
        )
        self.assertEqual(
            {task.name for task in visible_tasks_for_person(
                tasks, "Parent", {"Admin"}, include_managed=True
            )},
            {"Parent", "Kid"},
        )
        self.assertEqual(task_group_people(tasks[2], "Parent", {"Admin"}), ["Kid"])

    def test_project_visibility_uses_project_and_step_assignments(self):
        storage.save_admins(["Admin"])
        save_person("Admin", "parent")
        save_person("Ben", "member")
        save_person("Marina", "member")
        own_project = Project(name="Keller", room="Keller", assigned_to="Ben")
        shared_project = Project(name="Garage", room="Garage", assigned_to="Marina")
        own_step = Step(project_id=shared_project.id, name="Regal", assigned_to="Ben")
        other_step = Step(project_id=shared_project.id, name="Boden", assigned_to="Marina")
        steps_by_project = {
            own_project.id: [],
            shared_project.id: [own_step, other_step],
        }

        self.assertTrue(can_view_project(own_project, [], "Ben", {"Admin"}))
        self.assertTrue(can_view_project(shared_project, steps_by_project[shared_project.id], "Ben", {"Admin"}))
        self.assertEqual(
            visible_project_steps(shared_project, steps_by_project[shared_project.id], "Ben", {"Admin"}),
            [own_step],
        )
        self.assertEqual(
            {project.name for project in visible_projects_for_person(
                [own_project, shared_project], "Ben",
                lambda project_id: steps_by_project[project_id], {"Admin"},
            )},
            {"Keller", "Garage"},
        )

    def test_housekeeping_access_rules_are_role_based(self):
        storage.save_admins(["Admin"])
        save_person("Admin", "member")
        save_person("Parent", "parent")
        save_person("Helper", "housekeeper")
        save_person("Member", "member")

        self.assertTrue(can_manage_housekeeping("Admin", {"Admin"}))
        self.assertTrue(can_manage_housekeeping("Parent", {"Admin"}))
        self.assertFalse(can_manage_housekeeping("Helper", {"Admin"}))
        self.assertTrue(is_housekeeper("Helper"))
        self.assertTrue(can_create_housekeeping_entry("Helper", "Helper", {"Admin"}))
        self.assertTrue(can_create_housekeeping_entry("Parent", "Helper", {"Admin"}))
        self.assertFalse(can_create_housekeeping_entry("Member", "Helper", {"Admin"}))


if __name__ == "__main__":
    unittest.main()
