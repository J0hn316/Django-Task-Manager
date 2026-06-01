# Django Task Manager / Project Tracker

A Django web application for managing projects and tasks. Users can create projects, add tasks to each project, update task status and priority, search/filter/sort tasks, view project stats, and run automated tests to verify ownership and behavior.

This project was built as the second Django learning project after a Django Notes App.

---

## Project Overview

The app follows this core relationship:

```text
User
└── Project
    └── Task
```

Each user owns their own projects. Each project contains tasks. Task ownership is protected indirectly through the project owner.

That means a user can only view, edit, delete, or manage tasks that belong to their own projects.

---

## Features

### Project Features

- Create projects
- View project list
- View project detail pages
- Edit projects
- Delete projects
- Each project belongs to a logged-in user
- Users only see their own projects

### Task Features

- Create tasks inside a project
- View tasks on the project detail page
- Edit tasks
- Delete tasks
- Mark tasks complete
- Reopen completed tasks
- Task status options:
  - To Do
  - In Progress
  - Done
- Task priority options:
  - Low
  - Medium
  - High
- Optional due dates
- Completed timestamp tracking

### Search, Filter, and Sort

Tasks can be searched and filtered on the project detail page.

Supported task search/filter options:

- Search by title or description
- Filter by status
- Filter by priority
- Sort by:
  - Due date
  - Created date
  - Title
  - Priority

The app also displays how many tasks are currently shown after filters are applied.

Example:

```text
Showing 3 of 10 task(s).
```

### Project Stats

Each project detail page includes a dashboard-style stats section:

- Total tasks
- To Do tasks
- In Progress tasks
- Completed tasks
- High priority tasks
- Overdue tasks

Overdue tasks are calculated as tasks with a due date before today that are not marked as done.

---

## Tech Stack

- Python
- Django
- SQLite
- HTML
- CSS
- Django Templates
- Django Authentication
- Django Test Framework

---

## Main Django Concepts Practiced

This project focuses on practical Django backend concepts:

- Django apps and project structure
- Models
- Model relationships with `ForeignKey`
- `TextChoices` for controlled status and priority values
- ModelForms
- Function-based views
- URL routing
- Template inheritance
- Static files
- Django messages framework
- Authentication protection with `login_required`
- Ownership-based query filtering
- QuerySet filtering, searching, and sorting
- Automated tests with Django `TestCase`

---

## Project Structure

```text
django-task-manager/
├── manage.py
├── db.sqlite3
├── task_manager/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
└── tasks/
    ├── __init__.py
    ├── admin.py
    ├── apps.py
    ├── forms.py
    ├── models.py
    ├── tests.py
    ├── urls.py
    ├── views.py
    ├── migrations/
    ├── static/
    │   └── tasks/
    │       └── styles.css
    └── templates/
        └── tasks/
            ├── base.html
            ├── home.html
            ├── project_list.html
            ├── project_detail.html
            ├── project_form.html
            ├── project_confirm_delete.html
            ├── task_form.html
            └── task_confirm_delete.html
```

Note: `db.sqlite3` should be ignored by Git and should not be committed.

---

## Models

### Project Model

The `Project` model belongs to a user.

Main fields:

- `owner`
- `name`
- `description`
- `created_at`
- `updated_at`

Important relationship:

```python
owner = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete=models.CASCADE,
    related_name="projects",
)
```

This allows code like:

```python
request.user.projects.all()
```

---

### Task Model

The `Task` model belongs to a project.

Main fields:

- `project`
- `title`
- `description`
- `status`
- `priority`
- `due_date`
- `completed_at`
- `created_at`
- `updated_at`

Important relationship:

```python
project = models.ForeignKey(
    Project,
    on_delete=models.CASCADE,
    related_name="tasks",
)
```

This allows code like:

```python
project.tasks.all()
```

---

## Ownership and Security

The most important security pattern in this project is ownership filtering.

For projects:

```python
Project.objects.filter(owner=request.user)
```

For task access:

```python
get_object_or_404(Task, pk=pk, project__owner=request.user)
```

This protects against users manually typing URLs to access another user's projects or tasks.

For example, this is secure:

```python
project = get_object_or_404(Project, pk=pk, owner=request.user)
```

This is not safe enough by itself:

```python
project = get_object_or_404(Project, pk=pk)
```

The safe version checks both the project ID and the logged-in user.

---

## Routes

### General Routes

```text
/                       Home page
/projects/              Project list
/projects/create/       Create project
/projects/<id>/         Project detail
/projects/<id>/edit/    Edit project
/projects/<id>/delete/  Delete project
```

### Task Routes

```text
/projects/<project_id>/tasks/create/   Create task inside a project
/tasks/<task_id>/edit/                  Edit task
/tasks/<task_id>/delete/                Delete task
/tasks/<task_id>/toggle-complete/       Mark task complete or reopen task
```

---

## Forms

The project uses Django `ModelForm` classes.

### ProjectForm

```python
class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ["name", "description"]
```

The owner is intentionally not included in the form because the backend assigns ownership with:

```python
project.owner = request.user
```

---

### TaskForm

```python
class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ["title", "description", "status", "priority", "due_date"]
        widgets = {
            "due_date": forms.DateInput(attrs={"type": "date"}),
        }
```

The project is intentionally not included in the form because the backend assigns the project with:

```python
task.project = project
```

---

## Search and Filter Logic

The project detail view starts with all tasks that belong to the current project:

```python
all_tasks = project.tasks.all()
tasks = all_tasks
```

Then search/filter/sort logic is applied to `tasks`.

Search uses Django `Q` objects:

```python
tasks = tasks.filter(
    Q(title__icontains=query) | Q(description__icontains=query)
)
```

This means the search checks both the task title and task description.

---

## Project Stats Logic

Stats are calculated from `all_tasks`, not the filtered task list.

This means project stats still describe the whole project even when the user is searching or filtering.

Example:

```python
total_tasks = all_tasks.count()
todo_tasks = all_tasks.filter(status=Task.Status.TODO).count()
in_progress_tasks = all_tasks.filter(status=Task.Status.IN_PROGRESS).count()
completed_tasks = all_tasks.filter(status=Task.Status.DONE).count()
high_priority_tasks = all_tasks.filter(priority=Task.Priority.HIGH).count()
overdue_tasks = all_tasks.filter(
    due_date__lt=timezone.localdate()
).exclude(status=Task.Status.DONE).count()
```

The overdue logic means:

```text
Due date is before today
AND task is not completed
```

---

## Template System

The app uses Django template inheritance.

All pages extend:

```text
tasks/base.html
```

Example:

```django
{% extends "tasks/base.html" %}

{% block title %}My Projects | Django Task Manager{% endblock %}

{% block content %}
    Page content goes here.
{% endblock %}
```

The base template handles:

- HTML document structure
- CSS loading
- Navigation
- Messages
- Main content container

---

## Static CSS

The CSS file is located at:

```text
tasks/static/tasks/styles.css
```

It includes basic styling for:

- Layout container
- Navigation
- Cards
- Forms
- Buttons
- Messages
- Task badges
- Stats cards
- Empty states

---

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
cd django-task-manager
```

### 2. Create a Virtual Environment

Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

macOS/Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

If a `requirements.txt` file exists:

```bash
pip install -r requirements.txt
```

If not, install Django manually:

```bash
pip install django
```

Optional: create a requirements file after installing dependencies:

```bash
pip freeze > requirements.txt
```

### 4. Run Migrations

```bash
python manage.py migrate
```

### 5. Create a Superuser

```bash
python manage.py createsuperuser
```

### 6. Start the Development Server

```bash
python manage.py runserver
```

Then visit:

```text
http://127.0.0.1:8000/
```

---

## Admin Panel

The Django admin is available at:

```text
http://127.0.0.1:8000/admin/
```

The admin can be used to manage:

- Users
- Projects
- Tasks

---

## Running Tests

Run all tests:

```bash
python manage.py test
```

The test suite checks:

- Project ownership
- Project CRUD
- Task ownership
- Task CRUD
- Task completion and reopening
- Search behavior
- Status filtering
- Priority filtering
- Project stats
- Overdue count behavior

---

## Test Coverage Highlights

Important tests include:

```python
def test_user_only_sees_their_own_projects(self):
```

This confirms users only see their own projects.

```python
def test_user_cannot_edit_other_users_task(self):
```

This confirms users cannot edit tasks belonging to another user's project.

```python
def test_search_tasks_by_title_or_description(self):
```

This confirms the search feature checks both task titles and descriptions.

```python
def test_overdue_count_excludes_completed_tasks(self):
```

This confirms completed tasks are not counted as overdue.

---

## Important Lessons Learned

### 1. Backend Ownership Matters

Even if the frontend hides links, users can still manually type URLs.

That is why every sensitive view checks ownership on the backend.

### 2. `ForeignKey` Creates Real App Structure

The project uses relationships like:

```text
User → Project → Task
```

This is a major step beyond a simple single-table CRUD app.

### 3. Forms Should Not Expose Ownership Fields

The user does not choose the project owner or task project directly from unrestricted form fields.

The backend controls that logic.

### 4. Tests Protect Against Regressions

After refactoring templates and changing UI text, some tests needed updates.

This showed how tests help catch changes and confirm the app still works.

### 5. Formatters Can Break Django Templates

Some HTML formatters may incorrectly change Django template syntax.

For example, this is valid:

```django
{% if selected_priority == value %}
```

But a formatter might change it to:

```django
{% if selected_priority==value %}
```

That can cause a `TemplateSyntaxError`.

For Django templates, be careful with format-on-save or use a formatter that understands Django template syntax.

---

## Git Ignore Notes

Recommended files to ignore:

```gitignore
__pycache__/
*.py[cod]
venv/
.venv/
env/
.env
db.sqlite3
db.sqlite3-journal
/staticfiles/
/media/
*.log
.coverage
htmlcov/
.pytest_cache/
.vscode/
.idea/
.DS_Store
Thumbs.db
```

Migration files should be committed.

The local SQLite database should not be committed.


## Summary

This project is a complete Django Task Manager / Project Tracker application.

It demonstrates practical full-stack backend skills with Django:

```text
Authentication-aware views
User-owned data
Model relationships
CRUD operations
Search and filtering
Dashboard stats
Template inheritance
Automated testing
```

The most important pattern in the project is secure ownership filtering:

```python
get_object_or_404(Task, pk=pk, project__owner=request.user)
```

That pattern keeps each user's project and task data private.
