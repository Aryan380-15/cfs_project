from django.contrib import admin
from .models import Student


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("full_name", "roll_number", "department", "semester", "is_active")
    list_filter = ("department", "semester", "is_active")
    search_fields = ("full_name", "roll_number")
