from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required

from .models import Project


def home(request):
    return render(request, "tasks/home.html")


@login_required
def project_list(request):
    projects = Project.objects.filter(owner=request.user)

    return render(request, "tasks/project_list.html", {"projects": projects})


@login_required
def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk, owner=request.user)

    return render(request, "tasks/project_detail.html", {"project": project})
