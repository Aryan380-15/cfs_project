from django.contrib import admin
from .models import Department, Subject, AcademicSession, Notification


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "created_at")
    search_fields = ("name", "code")


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "department", "semester")
    list_filter = ("department", "semester")
    search_fields = ("name", "code")


@admin.register(AcademicSession)
class AcademicSessionAdmin(admin.ModelAdmin):
    list_display = ("name", "start_date", "end_date", "is_active", "feedback_open")
    list_filter = ("is_active", "feedback_open")


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("title", "recipient", "notification_type", "is_read", "created_at")
    list_filter = ("notification_type", "is_read")
