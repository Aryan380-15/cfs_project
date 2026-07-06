from django import forms
from django.contrib.auth.hashers import make_password

from apps.accounts.models import User
from apps.core.models import Department
from .models import Student


class StudentCreateForm(forms.Form):
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={"class": "form-control"}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control"}))
    full_name = forms.CharField(max_length=150, widget=forms.TextInput(attrs={"class": "form-control"}))
    roll_number = forms.CharField(max_length=30, widget=forms.TextInput(attrs={"class": "form-control"}))
    department = forms.ModelChoiceField(queryset=Department.objects.all(), widget=forms.Select(attrs={"class": "form-select"}))
    semester = forms.IntegerField(min_value=1, max_value=8, widget=forms.NumberInput(attrs={"class": "form-control"}))

    def clean_username(self):
        username = self.cleaned_data["username"]
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken.")
        return username

    def clean_roll_number(self):
        roll_number = self.cleaned_data["roll_number"]
        if Student.objects.filter(roll_number=roll_number).exists():
            raise forms.ValidationError("A student with this roll number already exists.")
        return roll_number

    def save(self):
        user = User.objects.create(
            username=self.cleaned_data["username"],
            password=make_password(self.cleaned_data["password"]),
            role=User.Role.STUDENT,
        )
        return Student.objects.create(
            user=user,
            full_name=self.cleaned_data["full_name"],
            roll_number=self.cleaned_data["roll_number"],
            department=self.cleaned_data["department"],
            semester=self.cleaned_data["semester"],
        )
