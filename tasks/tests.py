from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Project, Task

User = get_user_model()


class ProjectViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="john",
            password="testpass123",
        )
        self.other_user = User.objects.create_user(
            username="otheruser",
            password="testpass123",
        )

        self.project = Project.objects.create(
            owner=self.user,
            name="John Project",
            description="A project owned by John.",
        )

        self.other_project = Project.objects.create(
            owner=self.other_user,
            name="Other User Project",
            description="A project owned by someone else.",
        )

    def test_logged_in_user_can_view_their_project_list(self):
        self.client.login(username="john", password="testpass123")

        response = self.client.get(reverse("tasks:project_list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "John Project")

    def test_user_only_sees_their_own_projects(self):
        self.client.login(username="john", password="testpass123")

        response = self.client.get(reverse("tasks:project_list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "John Project")
        self.assertNotContains(response, "Other User Project")

    def test_user_can_view_their_own_project_detail(self):
        self.client.login(username="john", password="testpass123")

        response = self.client.get(
            reverse("tasks:project_detail", args=[self.project.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "John Project")

    def test_user_cannot_view_other_users_project_detail(self):
        self.client.login(username="john", password="testpass123")

        response = self.client.get(
            reverse("tasks:project_detail", args=[self.other_project.pk])
        )

        self.assertEqual(response.status_code, 404)

    def test_user_can_create_project(self):
        self.client.login(username="john", password="testpass123")

        response = self.client.post(
            reverse("tasks:project_create"),
            {
                "name": "New Project",
                "description": "Created from test.",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Project.objects.filter(
                owner=self.user,
                name="New Project",
            ).exists()
        )

    def test_user_can_edit_their_project(self):
        self.client.login(username="john", password="testpass123")

        response = self.client.post(
            reverse("tasks:project_edit", args=[self.project.pk]),
            {
                "name": "Updated Project",
                "description": "Updated description.",
            },
        )

        self.project.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.project.name, "Updated Project")
        self.assertEqual(self.project.description, "Updated description.")

    def test_user_cannot_edit_other_users_project(self):
        self.client.login(username="john", password="testpass123")

        response = self.client.post(
            reverse("tasks:project_edit", args=[self.other_project.pk]),
            {
                "name": "Hacked Project",
                "description": "Should not update.",
            },
        )

        self.other_project.refresh_from_db()

        self.assertEqual(response.status_code, 404)
        self.assertNotEqual(self.other_project.name, "Hacked Project")

    def test_user_can_delete_their_project(self):
        self.client.login(username="john", password="testpass123")

        response = self.client.post(
            reverse("tasks:project_delete", args=[self.project.pk])
        )

        self.assertEqual(response.status_code, 302)
        self.assertFalse(Project.objects.filter(pk=self.project.pk).exists())


class TaskViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="john",
            password="testpass123",
        )
        self.other_user = User.objects.create_user(
            username="otheruser",
            password="testpass123",
        )

        self.project = Project.objects.create(
            owner=self.user,
            name="John Project",
        )

        self.other_project = Project.objects.create(
            owner=self.other_user,
            name="Other User Project",
        )

        self.task = Task.objects.create(
            project=self.project,
            title="John Task",
            description="A task owned through John project.",
            status=Task.Status.TODO,
            priority=Task.Priority.HIGH,
            due_date=timezone.localdate() + timedelta(days=1),
        )

        self.other_task = Task.objects.create(
            project=self.other_project,
            title="Other User Task",
            status=Task.Status.TODO,
            priority=Task.Priority.MEDIUM,
        )

    def test_project_detail_displays_project_tasks(self):
        self.client.login(username="john", password="testpass123")

        response = self.client.get(
            reverse("tasks:project_detail", args=[self.project.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "John Task")

    def test_project_detail_does_not_display_other_users_tasks(self):
        self.client.login(username="john", password="testpass123")

        response = self.client.get(
            reverse("tasks:project_detail", args=[self.project.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "John Task")
        self.assertNotContains(response, "Other User Task")

    def test_user_can_create_task_for_their_project(self):
        self.client.login(username="john", password="testpass123")

        response = self.client.post(
            reverse("tasks:task_create", args=[self.project.pk]),
            {
                "title": "New Task",
                "description": "Created from test.",
                "status": Task.Status.TODO,
                "priority": Task.Priority.MEDIUM,
                "due_date": timezone.localdate() + timedelta(days=3),
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Task.objects.filter(
                project=self.project,
                title="New Task",
            ).exists()
        )

    def test_user_cannot_create_task_for_other_users_project(self):
        self.client.login(username="john", password="testpass123")

        response = self.client.post(
            reverse("tasks:task_create", args=[self.other_project.pk]),
            {
                "title": "Bad Task",
                "description": "Should not be created.",
                "status": Task.Status.TODO,
                "priority": Task.Priority.MEDIUM,
            },
        )

        self.assertEqual(response.status_code, 404)
        self.assertFalse(Task.objects.filter(title="Bad Task").exists())

    def test_user_can_edit_their_task(self):
        self.client.login(username="john", password="testpass123")

        response = self.client.post(
            reverse("tasks:task_edit", args=[self.task.pk]),
            {
                "title": "Updated Task",
                "description": "Updated task description.",
                "status": Task.Status.IN_PROGRESS,
                "priority": Task.Priority.LOW,
                "due_date": timezone.localdate() + timedelta(days=5),
            },
        )

        self.task.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.task.title, "Updated Task")
        self.assertEqual(self.task.status, Task.Status.IN_PROGRESS)
        self.assertEqual(self.task.priority, Task.Priority.LOW)

    def test_user_cannot_edit_other_users_task(self):
        self.client.login(username="john", password="testpass123")

        response = self.client.post(
            reverse("tasks:task_edit", args=[self.other_task.pk]),
            {
                "title": "Hacked Task",
                "description": "Should not update.",
                "status": Task.Status.DONE,
                "priority": Task.Priority.HIGH,
            },
        )

        self.other_task.refresh_from_db()

        self.assertEqual(response.status_code, 404)
        self.assertNotEqual(self.other_task.title, "Hacked Task")

    def test_user_can_delete_their_task(self):
        self.client.login(username="john", password="testpass123")

        response = self.client.post(reverse("tasks:task_delete", args=[self.task.pk]))

        self.assertEqual(response.status_code, 302)
        self.assertFalse(Task.objects.filter(pk=self.task.pk).exists())

    def test_user_cannot_delete_other_users_task(self):
        self.client.login(username="john", password="testpass123")

        response = self.client.post(
            reverse("tasks:task_delete", args=[self.other_task.pk])
        )

        self.assertEqual(response.status_code, 404)
        self.assertTrue(Task.objects.filter(pk=self.other_task.pk).exists())

    def test_user_can_mark_task_complete(self):
        self.client.login(username="john", password="testpass123")

        response = self.client.get(
            reverse("tasks:task_toggle_complete", args=[self.task.pk])
        )

        self.task.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.task.status, Task.Status.DONE)
        self.assertIsNotNone(self.task.completed_at)

    def test_user_can_reopen_completed_task(self):
        self.task.status = Task.Status.DONE
        self.task.completed_at = timezone.now()
        self.task.save()

        self.client.login(username="john", password="testpass123")

        response = self.client.get(
            reverse("tasks:task_toggle_complete", args=[self.task.pk])
        )

        self.task.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.task.status, Task.Status.TODO)
        self.assertIsNone(self.task.completed_at)

    def test_user_cannot_toggle_other_users_task(self):
        self.client.login(username="john", password="testpass123")

        response = self.client.get(
            reverse("tasks:task_toggle_complete", args=[self.other_task.pk])
        )

        self.assertEqual(response.status_code, 404)


class TaskFilterAndStatsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="john",
            password="testpass123",
        )

        self.project = Project.objects.create(
            owner=self.user,
            name="Stats Project",
        )

        Task.objects.create(
            project=self.project,
            title="Build Django views",
            description="Work on project views.",
            status=Task.Status.TODO,
            priority=Task.Priority.HIGH,
            due_date=timezone.localdate() - timedelta(days=1),
        )

        Task.objects.create(
            project=self.project,
            title="Write tests",
            description="Add Django test cases.",
            status=Task.Status.IN_PROGRESS,
            priority=Task.Priority.MEDIUM,
            due_date=timezone.localdate() + timedelta(days=2),
        )

        Task.objects.create(
            project=self.project,
            title="Deploy app",
            description="Deploy completed app.",
            status=Task.Status.DONE,
            priority=Task.Priority.HIGH,
            due_date=timezone.localdate() - timedelta(days=2),
            completed_at=timezone.now(),
        )

    def test_search_tasks_by_title_or_description(self):
        self.client.login(username="john", password="testpass123")

        response = self.client.get(
            reverse("tasks:project_detail", args=[self.project.pk]),
            {"q": "Django"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Build Django views")
        self.assertContains(response, "Write tests")
        self.assertNotContains(response, "Deploy app")

    def test_filter_tasks_by_status(self):
        self.client.login(username="john", password="testpass123")

        response = self.client.get(
            reverse("tasks:project_detail", args=[self.project.pk]),
            {"status": Task.Status.DONE},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Deploy app")
        self.assertNotContains(response, "Build Django views")

    def test_filter_tasks_by_priority(self):
        self.client.login(username="john", password="testpass123")

        response = self.client.get(
            reverse("tasks:project_detail", args=[self.project.pk]),
            {"priority": Task.Priority.HIGH},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Build Django views")
        self.assertContains(response, "Deploy app")
        self.assertNotContains(response, "Write tests")

    def test_project_stats_display_correct_counts(self):
        self.client.login(username="john", password="testpass123")

        response = self.client.get(
            reverse("tasks:project_detail", args=[self.project.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Total Tasks")
        self.assertContains(response, "3")
        self.assertContains(response, "To Do")
        self.assertContains(response, "In Progress")
        self.assertContains(response, "Completed")
        self.assertContains(response, "High Priority")
        self.assertContains(response, "Overdue")

    def test_overdue_count_excludes_completed_tasks(self):
        self.client.login(username="john", password="testpass123")

        response = self.client.get(
            reverse("tasks:project_detail", args=[self.project.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Overdue")
        self.assertContains(response, "1")


class AuthViewTests(TestCase):
    def test_register_page_loads(self):
        response = self.client.get(reverse("register"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Register")

    def test_user_can_register(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "newuser",
                "password1": "StrongPass12345!",
                "password2": "StrongPass12345!",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_logged_in_user_is_redirected_from_register_page(self):
        User.objects.create_user(
            username="johnny",
            password="testpass123",
        )

        logged_in = self.client.login(username="johnny", password="testpass123")

        self.assertTrue(logged_in)

        response = self.client.get(reverse("register"))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("tasks:project_list"))

    def test_logged_in_user_is_redirected_from_login_page(self):
        User.objects.create_user(
            username="johnlogin",
            password="testpass123",
        )

        logged_in = self.client.login(username="johnlogin", password="testpass123")

        self.assertTrue(logged_in)

        response = self.client.get(reverse("login"))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("tasks:project_list"))

    def test_login_page_loads(self):
        response = self.client.get(reverse("login"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Log in")

    def test_user_can_logout(self):
        User.objects.create_user(
            username="logoutuser",
            password="testpass123",
        )

        logged_in = self.client.login(username="logoutuser", password="testpass123")

        self.assertTrue(logged_in)

        response = self.client.post(reverse("logout"))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("tasks:home"))

    def test_protected_page_redirects_to_login(self):
        response = self.client.get(reverse("tasks:project_list"))

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

    def test_logout_requires_post_for_state_change(self):
        User.objects.create_user(
            username="getlogoutuser",
            password="testpass123",
        )

        logged_in = self.client.login(username="getlogoutuser", password="testpass123")

        self.assertTrue(logged_in)

        response = self.client.get(reverse("logout"))

        self.assertEqual(response.status_code, 302)

        protected_response = self.client.get(reverse("tasks:project_list"))

        self.assertEqual(protected_response.status_code, 200)
