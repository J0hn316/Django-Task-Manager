from django import forms

from .models import Project, Task

BASE_INPUT_CLASSES = (
    "w-full rounded-lg border border-slate-300 bg-white px-3 py-2 "
    "text-sm text-slate-900 shadow-sm "
    "focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-200"
)

BASE_TEXTAREA_CLASSES = (
    "w-full rounded-lg border border-slate-300 bg-white px-3 py-2 "
    "text-sm text-slate-900 shadow-sm "
    "focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-200"
)

BASE_SELECT_CLASSES = (
    "w-full rounded-lg border border-slate-300 bg-white px-3 py-2 "
    "text-sm text-slate-900 shadow-sm "
    "focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-200"
)


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ["name", "description"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": BASE_INPUT_CLASSES,
                    "placeholder": "Enter project name",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": BASE_TEXTAREA_CLASSES,
                    "placeholder": "Enter project description",
                    "rows": 5,
                }
            ),
        }


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ["title", "description", "status", "priority", "due_date"]
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": BASE_INPUT_CLASSES,
                    "placeholder": "Enter task title",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": BASE_TEXTAREA_CLASSES,
                    "placeholder": "Enter task description",
                    "rows": 5,
                }
            ),
            "status": forms.Select(
                attrs={
                    "class": BASE_SELECT_CLASSES,
                }
            ),
            "priority": forms.Select(
                attrs={
                    "class": BASE_SELECT_CLASSES,
                }
            ),
            "due_date": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": BASE_INPUT_CLASSES,
                }
            ),
        }
