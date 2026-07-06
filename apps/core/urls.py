from django.urls import path
from . import views
from . import admin_views

app_name = "core"

urlpatterns = [
    path("", views.dashboard_redirect, name="dashboard_redirect"),
    path("admin-panel/dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("teacher/dashboard/", views.teacher_dashboard, name="teacher_dashboard"),
    path("student/dashboard/", views.student_dashboard, name="student_dashboard"),

    # Admin: student management
    path("admin-panel/students/", admin_views.student_list, name="admin_student_list"),
    path("admin-panel/students/add/", admin_views.student_add, name="admin_student_add"),
    path("admin-panel/students/import/", admin_views.student_import_csv, name="admin_student_import"),

    # Admin: teacher management
    path("admin-panel/teachers/", admin_views.teacher_list, name="admin_teacher_list"),
    path("admin-panel/teachers/add/", admin_views.teacher_add, name="admin_teacher_add"),

    # Admin: reports
    path("admin-panel/reports/", admin_views.reports_page, name="admin_reports"),
    path("admin-panel/reports/pdf/<int:teacher_id>/", admin_views.report_teacher_pdf, name="admin_report_pdf"),
    path("admin-panel/reports/excel/", admin_views.report_excel_all, name="admin_report_excel"),
]
