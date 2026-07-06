import csv
import io

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db.models import Avg, Count
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from apps.accounts.models import User
from apps.core.models import Department
from apps.students.models import Student
from apps.students.forms import StudentCreateForm
from apps.teachers.models import Teacher
from apps.teachers.forms import TeacherCreateForm
from apps.feedback.models import FeedbackQuestion, FeedbackResponse, FeedbackReview

from .admin_forms import CSVImportForm


def _require_admin(request):
    if not (request.user.is_superuser or getattr(request.user, "role", None) == "admin"):
        raise PermissionDenied("Admin access required.")


# ---------------------------------------------------------------- Students
@login_required
def student_list(request):
    _require_admin(request)
    students = Student.objects.select_related("user", "department").order_by("roll_number")

    query = request.GET.get("q", "")
    if query:
        students = students.filter(full_name__icontains=query) | students.filter(roll_number__icontains=query)

    paginator = Paginator(students, 15)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(request, "core/admin_students.html", {"page_obj": page_obj, "query": query})


@login_required
def student_add(request):
    _require_admin(request)
    form = StudentCreateForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Student account created successfully.")
        return redirect("core:admin_student_list")
    return render(request, "core/admin_student_add.html", {"form": form})


@login_required
def student_import_csv(request):
    _require_admin(request)
    form = CSVImportForm(request.POST or None, request.FILES or None)

    if request.method == "POST" and form.is_valid():
        csv_file = request.FILES["csv_file"]
        decoded = csv_file.read().decode("utf-8")
        reader = csv.DictReader(io.StringIO(decoded))

        created_count = 0
        error_rows = []
        for i, row in enumerate(reader, start=2):  # row 1 is the header
            try:
                username = row["username"].strip()
                roll_number = row["roll_number"].strip()
                if User.objects.filter(username=username).exists() or Student.objects.filter(roll_number=roll_number).exists():
                    error_rows.append(f"Row {i}: username/roll number already exists, skipped.")
                    continue

                department = Department.objects.get(code=row["department_code"].strip())
                user = User.objects.create_user(
                    username=username, password=row["password"].strip(), role=User.Role.STUDENT
                )
                Student.objects.create(
                    user=user,
                    full_name=row["full_name"].strip(),
                    roll_number=roll_number,
                    department=department,
                    semester=int(row["semester"]),
                )
                created_count += 1
            except Exception as e:
                error_rows.append(f"Row {i}: {e}")

        messages.success(request, f"Imported {created_count} students successfully.")
        for err in error_rows[:10]:
            messages.warning(request, err)
        return redirect("core:admin_student_list")

    return render(request, "core/admin_student_import.html", {"form": form})


# ---------------------------------------------------------------- Teachers
@login_required
def teacher_list(request):
    _require_admin(request)
    teachers = Teacher.objects.select_related("user", "department").order_by("full_name")

    query = request.GET.get("q", "")
    if query:
        teachers = teachers.filter(full_name__icontains=query) | teachers.filter(employee_id__icontains=query)

    paginator = Paginator(teachers, 15)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(request, "core/admin_teachers.html", {"page_obj": page_obj, "query": query})


@login_required
def teacher_add(request):
    _require_admin(request)
    form = TeacherCreateForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Teacher account created successfully.")
        return redirect("core:admin_teacher_list")
    return render(request, "core/admin_teacher_add.html", {"form": form})


# ---------------------------------------------------------------- Reports
@login_required
def reports_page(request):
    _require_admin(request)
    teachers = Teacher.objects.filter(is_active=True).order_by("full_name")
    return render(request, "core/admin_reports.html", {"teachers": teachers})


@login_required
def report_teacher_pdf(request, teacher_id):
    _require_admin(request)
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib import colors
    from reportlab.lib.units import cm
    from django.db.models import Q

    teacher = get_object_or_404(Teacher, pk=teacher_id)
    responses = FeedbackResponse.objects.filter(teacher=teacher)
    overall_avg = responses.aggregate(avg=Avg("rating"))["avg"]
    question_breakdown = (
        FeedbackQuestion.objects.filter(is_active=True)
        .annotate(avg_rating=Avg("responses__rating", filter=Q(responses__teacher=teacher)))
        .order_by("order")
    )
    reviews = FeedbackReview.objects.filter(
        teacher=teacher, moderation_status=FeedbackReview.ModerationStatus.APPROVED
    )[:20]

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="feedback_report_{teacher.employee_id}.pdf"'

    doc = SimpleDocTemplate(response, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("Anonymous Teacher Feedback Report", styles["Title"]))
    story.append(Spacer(1, 10))
    story.append(Paragraph(f"Teacher: {teacher.full_name} ({teacher.employee_id})", styles["Heading2"]))
    story.append(Paragraph(f"Department: {teacher.department}", styles["Normal"]))
    story.append(Paragraph(f"Overall Rating: {round(overall_avg, 2) if overall_avg else 'N/A'} / 10", styles["Normal"]))
    story.append(Spacer(1, 16))

    story.append(Paragraph("Question-wise Averages", styles["Heading3"]))
    table_data = [["Question", "Average Rating"]]
    for q in question_breakdown:
        table_data.append([q.text, f"{round(q.avg_rating, 2) if q.avg_rating else 'N/A'}"])
    table = Table(table_data, colWidths=[11 * cm, 5 * cm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#8b5cf6")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
    ]))
    story.append(table)
    story.append(Spacer(1, 16))

    story.append(Paragraph("Anonymous Written Reviews", styles["Heading3"]))
    if reviews:
        for r in reviews:
            story.append(Paragraph(f"&bull; {r.comment}", styles["Normal"]))
            story.append(Spacer(1, 4))
    else:
        story.append(Paragraph("No written reviews yet.", styles["Normal"]))

    doc.build(story)
    return response


@login_required
def report_excel_all(request):
    _require_admin(request)
    import openpyxl
    from openpyxl.styles import Font

    _require_admin(request)
    wb = openpyxl.Workbook()

    # --- Sheet 1: Teacher summary ---
    ws1 = wb.active
    ws1.title = "Teacher Summary"
    ws1.append(["Teacher", "Department", "Overall Rating", "Total Feedback Count"])
    for cell in ws1[1]:
        cell.font = Font(bold=True)

    for teacher in Teacher.objects.filter(is_active=True):
        responses = FeedbackResponse.objects.filter(teacher=teacher)
        avg = responses.aggregate(avg=Avg("rating"))["avg"]
        count = responses.values("anonymous_id").distinct().count()
        ws1.append([teacher.full_name, str(teacher.department), round(avg, 2) if avg else "N/A", count])

    # --- Sheet 2: All anonymous responses ---
    ws2 = wb.create_sheet("Anonymous Responses")
    ws2.append(["Teacher", "Question", "Rating", "Session", "Submitted On"])
    for cell in ws2[1]:
        cell.font = Font(bold=True)
    for r in FeedbackResponse.objects.select_related("teacher", "question", "session").order_by("-created_at")[:5000]:
        ws2.append([r.teacher.full_name, r.question.text, r.rating, r.session.name, r.created_at.strftime("%Y-%m-%d")])

    response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = 'attachment; filename="feedback_report.xlsx"'
    wb.save(response)
    return response
