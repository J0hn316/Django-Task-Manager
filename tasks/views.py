from django.db.models import Q
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from .models import Project, Task
from .forms import ProjectForm, TaskForm


def home(request):
    return render(request, "tasks/home.html")


def register(request):
    if request.user.is_authenticated:
        return redirect("tasks:project_list")

    if request.method == "POST":
        form = UserCreationForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)

            messages.success(request, "Account created successfully")
            return redirect("tasks:project_list")
    else:
        form = UserCreationForm()

    input_classes = (
        "w-full rounded-lg border border-slate-300 bg-white px-3 py-2 "
        "text-sm text-slate-900 shadow-sm "
        "focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-200"
    )

    for field in form.fields.values():
        field.widget.attrs.update({"class": input_classes})

    return render(request, "tasks/registration/register.html", {"form": form})


@login_required
def project_list(request):
    projects = Project.objects.filter(owner=request.user)

    return render(request, "tasks/project_list.html", {"projects": projects})


@login_required
def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk, owner=request.user)

    all_tasks = project.tasks.all()

    total_tasks = all_tasks.count()

    todo_tasks = all_tasks.filter(status=Task.Status.TODO).count()

    in_progress_tasks = all_tasks.filter(status=Task.Status.IN_PROGRESS).count()

    completed_tasks = all_tasks.filter(status=Task.Status.DONE).count()

    high_priority_tasks = all_tasks.filter(priority=Task.Priority.HIGH).count()

    overdue_tasks = (
        all_tasks.filter(due_date__lt=timezone.localdate())
        .exclude(status=Task.Status.DONE)
        .count()
    )

    tasks = all_tasks

    query = request.GET.get("q", "")
    status = request.GET.get("status", "")
    priority = request.GET.get("priority", "")
    sort = request.GET.get("sort", "due_date")

    if query:
        tasks = tasks.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )

    if status:
        tasks = tasks.filter(status=status)

    if priority:
        tasks = tasks.filter(priority=priority)

    allowed_sorts = {
        "due_date": "due_date",
        "-due_date": "-due_date",
        "priority": "priority",
        "-priority": "-priority",
        "created_at": "created_at",
        "-created_at": "-created_at",
        "title": "title",
        "-title": "-title",
    }

    sort_field = allowed_sorts.get(sort, "due_date")
    tasks = tasks.order_by(sort_field)
    filtered_task_count = tasks.count()

    return render(
        request,
        "tasks/project_detail.html",
        {
            "project": project,
            "tasks": tasks,
            "query": query,
            "selected_status": status,
            "selected_priority": priority,
            "selected_sort": sort,
            "status_choices": Task.Status.choices,
            "priority_choices": Task.Priority.choices,
            "total_tasks": total_tasks,
            "todo_tasks": todo_tasks,
            "in_progress_tasks": in_progress_tasks,
            "completed_tasks": completed_tasks,
            "high_priority_tasks": high_priority_tasks,
            "overdue_tasks": overdue_tasks,
            "filtered_task_count": filtered_task_count,
        },
    )


@login_required
def project_create(request):
    if request.method == "POST":
        form = ProjectForm(request.POST)

        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()

            messages.success(request, "Project created successfully.")
            return redirect("tasks:project_detail", pk=project.pk)
    else:
        form = ProjectForm()

    return render(
        request, "tasks/project_form.html", {"form": form, "title": "Create Project"}
    )


@login_required
def project_edit(request, pk):
    project = get_object_or_404(Project, pk=pk, owner=request.user)

    if request.method == "POST":
        form = ProjectForm(request.POST, instance=project)

        if form.is_valid():
            form.save()

            messages.success(request, "Project updated successfully.")
            return redirect("tasks:project_detail", pk=project.pk)
    else:
        form = ProjectForm(instance=project)

    return render(
        request, "tasks/project_form.html", {"form": form, "title": "Edit Project"}
    )


@login_required
def project_delete(request, pk):
    project = get_object_or_404(Project, pk=pk, owner=request.user)

    if request.method == "POST":
        project.delete()

        messages.success(request, "Project deleted successfully.")
        return redirect("tasks:project_list")

    return render(request, "tasks/project_confirm_delete.html", {"project": project})


@login_required
def task_create(request, project_pk):
    project = get_object_or_404(Project, pk=project_pk, owner=request.user)

    if request.method == "POST":
        form = TaskForm(request.POST)

        if form.is_valid():
            task = form.save(commit=False)
            task.project = project

            if task.status == Task.Status.DONE and task.completed_at is None:
                task.completed_at = timezone.now()

            task.save()

            messages.success(request, "Task created successfully.")
            return redirect("tasks:project_detail", pk=project.pk)
    else:
        form = TaskForm()

    return render(
        request,
        "tasks/task_form.html",
        {
            "form": form,
            "project": project,
            "title": "Create Task",
        },
    )


@login_required
def task_edit(request, pk):
    task = get_object_or_404(Task, pk=pk, project__owner=request.user)

    if request.method == "POST":
        form = TaskForm(request.POST, instance=task)

        if form.is_valid():
            updated_task = form.save(commit=False)

            if (
                updated_task.status == Task.Status.DONE
                and updated_task.completed_at is None
            ):
                updated_task.completed_at = timezone.now()
            elif updated_task.status != Task.Status.DONE:
                updated_task.completed_at = None

            updated_task.save()

            messages.success(request, "Task updated successfully.")
            return redirect("tasks:project_detail", pk=updated_task.project.pk)
    else:
        form = TaskForm(instance=task)

    return render(
        request,
        "tasks/task_form.html",
        {
            "form": form,
            "project": task.project,
            "task": task,
            "title": "Edit Task",
        },
    )


@login_required
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk, project__owner=request.user)
    project_pk = task.project.pk

    if request.method == "POST":
        task.delete()

        messages.success(request, "Task deleted successfully.")
        return redirect("tasks:project_detail", pk=project_pk)

    return render(request, "tasks/task_confirm_delete.html", {"task": task})


@login_required
def task_toggle_complete(request, pk):
    task = get_object_or_404(Task, pk=pk, project__owner=request.user)

    if task.status == Task.Status.DONE:
        task.status = Task.Status.TODO
        task.completed_at = None
        messages.success(request, "Task reopened successfully.")
    else:
        task.status = Task.Status.DONE
        task.completed_at = timezone.now()
        messages.success(request, "Task marked as complete.")

    task.save()

    return redirect("tasks:project_detail", pk=task.project.pk)
