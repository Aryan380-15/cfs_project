from django import forms
from django.contrib.auth.hashers import make_password

from apps.accounts.models import User
from apps.core.models import Department, Subject
from .models import Teacher


class TeacherCreateForm(forms.Form):
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={"class": "form-control"}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control"}))
    full_name = forms.CharField(max_length=150, widget=forms.TextInput(attrs={"class": "form-control"}))
    employee_id = forms.CharField(max_length=30, widget=forms.TextInput(attrs={"class": "form-control"}))
    department = forms.ModelChoiceField(queryset=Department.objects.all(), widget=forms.Select(attrs={"class": "form-select"}))
    subjects = forms.ModelMultipleChoiceField(
        queryset=Subject.objects.all(),
        widget=forms.SelectMultiple(attrs={"class": "form-select"}),
        required=False,
    )
    designation = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={"class": "form-control"}))

    def clean_username(self):
        username = self.cleaned_data["username"]
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken.")
        return username

    def clean_employee_id(self):
        employee_id = self.cleaned_data["employee_id"]
        if Teacher.objects.filter(employee_id=employee_id).exists():
            raise forms.ValidationError("A teacher with this employee ID already exists.")
        return employee_id

    def save(self):
        user = User.objects.create(
            username=self.cleaned_data["username"],
            password=make_password(self.cleaned_data["password"]),
            role=User.Role.TEACHER,
        )
        teacher = Teacher.objects.create(
            user=user,
            full_name=self.cleaned_data["full_name"],
            employee_id=self.cleaned_data["employee_id"],
            department=self.cleaned_data["department"],
            designation=self.cleaned_data.get("designation", ""),
        )
        teacher.subjects.set(self.cleaned_data["subjects"])
        return teacher
