from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

from tasks import views as task_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="tasks/registration/login.html",
            redirect_authenticated_user=True,
        ),
        name="login",
    ),
    path("logout/", task_views.logout_user, name="logout"),
    path("register/", task_views.register, name="register"),
    path("", include("tasks.urls")),
]
