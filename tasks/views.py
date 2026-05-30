from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from .models import Project
from .forms import ProjectForm


def home(request):
    return render(request, "tasks/home.html")


@login_required
def project_list(request):
    projects = Project.objects.filter(owner=request.user)

    return render(request, "tasks/project_list.html", {"projects": projects})


@login_required
def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk, owner=request.user)
    tasks = project.tasks.all()

    return render(
        request,
        "tasks/project_detail.html",
        {
            "project": project,
            "tasks": tasks,
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
