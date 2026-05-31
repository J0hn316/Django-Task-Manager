from django.urls import path

from . import views

app_name = "tasks"

urlpatterns = [
    path("", views.home, name="home"),
    path("projects/", views.project_list, name="project_list"),
    path("projects/create/", views.project_create, name="project_create"),
    path("projects/<int:pk>/", views.project_detail, name="project_detail"),
    path("projects/<int:pk>/edit/", views.project_edit, name="project_edit"),
    path("projects/<int:pk>/delete/", views.project_delete, name="project_delete"),
    path(
        "projects/<int:project_pk>/tasks/create/", views.task_create, name="task_create"
    ),
    path("tasks/<int:pk>/edit/", views.task_edit, name="task_edit"),
    path("tasks/<int:pk>/delete/", views.task_delete, name="task_delete"),
    path(
        "tasks/<int:pk>/toggle-complete/",
        views.task_toggle_complete,
        name="task_toggle_complete",
    ),
]
