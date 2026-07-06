from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render


@login_required
def dashboard_redirect(request):
    """Sends a freshly logged-in user to the correct role dashboard."""
    user = request.user
    if user.is_superuser or getattr(user, "role", None) == "admin":
        return redirect("core:admin_dashboard")
    if getattr(user, "role", None) == "teacher":
        return redirect("core:teacher_dashboard")
    if getattr(user, "role", None) == "student":
        return redirect("core:student_dashboard")
    return redirect("accounts:login")


@login_required
def admin_dashboard(request):
    from django.db.models import Avg, Count
    from apps.students.models import Student
    from apps.teachers.models import Teacher
    from apps.core.models import Department
    from apps.feedback.models import FeedbackResponse
    from apps.suggestions.models import CollegeSuggestion

    total_students = Student.objects.count()
    total_teachers = Teacher.objects.count()
    total_departments = Department.objects.count()

    responses = FeedbackResponse.objects.all()
    total_feedback_count = responses.values("anonymous_id").distinct().count()
    overall_avg = responses.aggregate(avg=Avg("rating"))["avg"]

    pending_suggestions = CollegeSuggestion.objects.filter(status=CollegeSuggestion.Status.PENDING).count()

    # Department-wise average rating
    dept_data = (
        Department.objects.annotate(
            avg_rating=Avg("teachers__feedback_responses__rating")
        )
        .filter(avg_rating__isnull=False)
        .order_by("-avg_rating")
    )
    dept_labels = [d.name for d in dept_data]
    dept_values = [round(d.avg_rating, 2) for d in dept_data]

    # Top 5 teacher ranking by average rating
    teacher_ranking = (
        Teacher.objects.annotate(avg_rating=Avg("feedback_responses__rating"))
        .filter(avg_rating__isnull=False)
        .order_by("-avg_rating")[:5]
    )
    ranking_labels = [t.full_name for t in teacher_ranking]
    ranking_values = [round(t.avg_rating, 2) for t in teacher_ranking]

    context = {
        "total_students": total_students,
        "total_teachers": total_teachers,
        "total_departments": total_departments,
        "total_feedback_count": total_feedback_count,
        "overall_avg": round(overall_avg, 2) if overall_avg else None,
        "pending_suggestions": pending_suggestions,
        "dept_labels": dept_labels,
        "dept_values": dept_values,
        "ranking_labels": ranking_labels,
        "ranking_values": ranking_values,
    }
    return render(request, "core/admin_dashboard.html", context)


@login_required
def teacher_dashboard(request):
    from django.db.models import Avg
    from apps.feedback.models import FeedbackResponse, FeedbackReview

    teacher = getattr(request.user, "teacher_profile", None)
    context = {"teacher": teacher}
    if teacher:
        responses = FeedbackResponse.objects.filter(teacher=teacher)
        overall_avg = responses.aggregate(avg=Avg("rating"))["avg"]
        context["overall_avg"] = round(overall_avg, 2) if overall_avg else None
        context["total_feedback_count"] = responses.values("anonymous_id").distinct().count()
        context["review_count"] = FeedbackReview.objects.filter(teacher=teacher).count()
    return render(request, "core/teacher_dashboard.html", context)


@login_required
def student_dashboard(request):
    return render(request, "core/student_dashboard.html")
