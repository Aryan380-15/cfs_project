from django.conf import settings
from django.db import models
from apps.core.models import Department


class Student(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="student_profile")
    roll_number = models.CharField(max_length=30, unique=True)
    full_name = models.CharField(max_length=150)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, related_name="students")
    semester = models.PositiveSmallIntegerField(default=1)
    photo = models.ImageField(upload_to="student_photos/", blank=True, null=True)
    is_active = models.BooleanField(default=True)
    admitted_on = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["roll_number"]

    def __str__(self):
        return f"{self.full_name} ({self.roll_number})"
