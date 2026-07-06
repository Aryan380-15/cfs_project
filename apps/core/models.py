import uuid
from django.db import models
from django.conf import settings


class Department(models.Model):
    name = models.CharField(max_length=120, unique=True)
    code = models.CharField(max_length=20, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Subject(models.Model):
    name = models.CharField(max_length=150)
    code = models.CharField(max_length=20, unique=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name="subjects")
    semester = models.PositiveSmallIntegerField(default=1)

    class Meta:
        ordering = ["department", "semester", "name"]

    def __str__(self):
        return f"{self.name} ({self.code})"


class AcademicSession(models.Model):
    """e.g. 2025-26 Odd Semester"""
    name = models.CharField(max_length=100, unique=True)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=False)
    feedback_open = models.BooleanField(default=False)

    class Meta:
        ordering = ["-start_date"]

    def __str__(self):
        return self.name


class Notification(models.Model):
    class NotificationType(models.TextChoices):
        FEEDBACK_OPEN = "feedback_open", "Feedback Session Opened"
        FEEDBACK_DEADLINE = "feedback_deadline", "Feedback Deadline Reminder"
        SUGGESTION_UPDATE = "suggestion_update", "Suggestion Status Updated"
        GENERAL = "general", "General"

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications"
    )
    notification_type = models.CharField(max_length=30, choices=NotificationType.choices, default=NotificationType.GENERAL)
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} -> {self.recipient}"
