from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render

from apps.core.models import AcademicSession
from apps.feedback.models import FeedbackSubmissionTracker, TeacherAssignment


@login_required
def teacher_list(request):
    """
    Shows the logged-in student's assigned teachers for the active
    session, with a submitted/pending indicator for each.
    """
    if getattr(request.user, "role", None) != "student":
        raise PermissionDenied("Only students can view this page.")

    student = getattr(request.user, "student_profile", None)
    if student is None:
        messages.error(request, "No student profile found for this account.")
        return render(request, "students/teacher_list.html", {"rows": [], "active_session": None})

    active_session = AcademicSession.objects.filter(is_active=True, feedback_open=True).first()
    rows = []

    if active_session:
        assignments = (
            TeacherAssignment.objects.filter(student=student, session=active_session)
            .select_related("teacher", "subject")
        )
        submitted_teacher_ids = set(
            FeedbackSubmissionTracker.objects.filter(
                student=student, session=active_session
            ).values_list("teacher_id", flat=True)
        )
        seen_teachers = set()
        for a in assignments:
            if a.teacher_id in seen_teachers:
                continue
            seen_teachers.add(a.teacher_id)
            rows.append({
                "teacher": a.teacher,
                "subject": a.subject,
                "submitted": a.teacher_id in submitted_teacher_ids,
            })

    total = len(rows)
    completed = sum(1 for r in rows if r["submitted"])

    context = {
        "rows": rows,
        "active_session": active_session,
        "total": total,
        "completed": completed,
        "progress_percent": int((completed / total) * 100) if total else 0,
    }
    return render(request, "students/teacher_list.html", context)
