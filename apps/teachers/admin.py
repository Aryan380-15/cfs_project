from django.contrib import admin
from .models import Teacher


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ("full_name", "employee_id", "department", "designation", "is_active")
    list_filter = ("department", "is_active")
    search_fields = ("full_name", "employee_id")
    filter_horizontal = ("subjects",)
