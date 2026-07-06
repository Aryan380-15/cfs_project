from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count, Q
from django.shortcuts import get_object_or_404, render

from apps.feedback.models import FeedbackQuestion, FeedbackResponse, FeedbackReview
from .models import Teacher


@login_required
def public_profile(request, teacher_id):
    """
    Public teacher profile: overall score, question-wise averages,
    a rating trend, and approved anonymous reviews.
    Visible to Admin, Teacher and Student roles alike -- no student
    identity is ever attached to any of this data.
    """
    teacher = get_object_or_404(Teacher, pk=teacher_id, is_active=True)

    responses = FeedbackResponse.objects.filter(teacher=teacher)
    overall_avg = responses.aggregate(avg=Avg("rating"))["avg"]

    question_breakdown = (
        FeedbackQuestion.objects.filter(is_active=True)
        .annotate(
            avg_rating=Avg("responses__rating", filter=Q(responses__teacher=teacher)),
            rating_count=Count("responses", filter=Q(responses__teacher=teacher)),
        )
        .order_by("order")
    )

    reviews = (
        FeedbackReview.objects.filter(
            teacher=teacher, moderation_status=FeedbackReview.ModerationStatus.APPROVED
        )
        .order_by("-created_at")[:50]
    )

    total_feedback_count = (
        responses.values("anonymous_id").distinct().count()
    )

    chart_labels = [q.text for q in question_breakdown]
    chart_values = [round(q.avg_rating, 2) if q.avg_rating else 0 for q in question_breakdown]

    context = {
        "teacher": teacher,
        "overall_avg": round(overall_avg, 2) if overall_avg else None,
        "question_breakdown": question_breakdown,
        "reviews": reviews,
        "total_feedback_count": total_feedback_count,
        "chart_labels": chart_labels,
        "chart_values": chart_values,
    }
    return render(request, "teachers/public_profile.html", context)
