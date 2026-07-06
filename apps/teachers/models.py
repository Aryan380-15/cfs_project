from django.conf import settings
from django.db import models
from apps.core.models import Department, Subject


class Teacher(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="teacher_profile")
    employee_id = models.CharField(max_length=30, unique=True)
    full_name = models.CharField(max_length=150)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, related_name="teachers")
    subjects = models.ManyToManyField(Subject, related_name="teachers", blank=True)
    designation = models.CharField(max_length=100, blank=True)
    photo = models.ImageField(upload_to="teacher_photos/", blank=True, null=True)
    bio = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    joined_on = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["full_name"]

    def __str__(self):
        return f"{self.full_name} - {self.department}"

    @property
    def total_feedback_count(self):
        return self.feedback_responses.count() if hasattr(self, "feedback_responses") else 0
