import uuid

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.core.exceptions import PermissionDenied

from apps.core.models import AcademicSession
from apps.teachers.models import Teacher
from apps.students.models import Student

from .forms import FeedbackReviewForm
from .models import (
    FeedbackQuestion,
    FeedbackResponse,
    FeedbackReview,
    FeedbackSubmissionTracker,
    TeacherAssignment,
)
from .utils import contains_abusive_language

SESSION_KEY_MY_SUBMISSIONS = "my_feedback_submissions"  # list of dicts, session-only


def _get_active_session():
    return AcademicSession.objects.filter(is_active=True, feedback_open=True).first()


def _require_student(request):
    """Raises PermissionDenied if the logged-in user is not a student with a profile."""
    if getattr(request.user, "role", None) != "student":
        raise PermissionDenied("Only students can submit feedback.")
    try:
        return request.user.student_profile
    except Student.DoesNotExist:
        raise PermissionDenied("Student profile not found for this account.")


@login_required
def feedback_notice(request, teacher_id):
    """
    Shows the mandatory 'Anonymous Feedback Notice' before the form opens.
    'I Understand' (POST) -> proceeds to the form.
    'Cancel' -> back to teacher list.

    Any student can give feedback to any active teacher -- there is no
    "must be assigned to this teacher" requirement.
    """
    student = _require_student(request)
    teacher = get_object_or_404(Teacher, pk=teacher_id, is_active=True)
    active_session = _get_active_session()

    if not active_session:
        messages.error(request, "Feedback submission is currently closed.")
        return redirect("students:teacher_list")

    already_submitted = FeedbackSubmissionTracker.objects.filter(
        student=student, teacher=teacher, session=active_session
    ).exists()
    if already_submitted:
        messages.info(request, "You have already submitted feedback for this teacher.")
        return redirect("students:teacher_list")

    if request.method == "POST":
        if request.POST.get("action") == "understood":
            return redirect("feedback:submit_feedback", teacher_id=teacher.id)
        return redirect("students:teacher_list")

    return render(request, "feedback/notice.html", {"teacher": teacher})


@login_required
def submit_feedback(request, teacher_id):
    student = _require_student(request)
    teacher = get_object_or_404(Teacher, pk=teacher_id, is_active=True)
    active_session = _get_active_session()

    if not active_session:
        messages.error(request, "Feedback submission is currently closed.")
        return redirect("students:teacher_list")

    if FeedbackSubmissionTracker.objects.filter(
        student=student, teacher=teacher, session=active_session
    ).exists():
        messages.info(request, "You have already submitted feedback for this teacher.")
        return redirect("students:teacher_list")

    if not TeacherAssignment.objects.filter(
        teacher=teacher, student=student, session=active_session
    ).exists():
        messages.error(request, "You are not assigned to this teacher for the active session.")
        return redirect("students:teacher_list")

    questions = FeedbackQuestion.objects.filter(is_active=True).order_by("order")
    review_form = FeedbackReviewForm(request.POST or None)

    if request.method == "POST":
        # Validate every question has a rating between 1 and 10
        ratings = {}
        errors = []
        for question in questions:
            raw = request.POST.get(f"question_{question.id}")
            if not raw or not raw.isdigit() or not (1 <= int(raw) <= 10):
                errors.append(f"Please rate: {question.text}")
            else:
                ratings[question.id] = int(raw)

        comment = ""
        if review_form.is_valid():
            comment = review_form.cleaned_data.get("comment", "").strip()

        if contains_abusive_language(comment):
            errors.append(
                "Your comment contains language that isn't allowed. "
                "Please rewrite it respectfully and constructively."
            )

        if errors:
            for e in errors:
                messages.error(request, e)
            return render(
                request,
                "feedback/submit_form.html",
                {"teacher": teacher, "questions": questions, "review_form": review_form, "rating_range": range(1, 11)},
            )

        # All good -- save anonymously
        anonymous_id = uuid.uuid4()
        response_snapshot = []
        for question in questions:
            FeedbackResponse.objects.create(
                anonymous_id=anonymous_id,
                teacher=teacher,
                session=active_session,
                question=question,
                rating=ratings[question.id],
            )
            response_snapshot.append({"question": question.text, "rating": ratings[question.id]})

        if comment:
            FeedbackReview.objects.create(
                anonymous_id=anonymous_id,
                teacher=teacher,
                session=active_session,
                comment=comment,
            )

        # Tracker: only stops duplicates / checks eligibility - no link to the answers above
        FeedbackSubmissionTracker.objects.create(
            student=student, teacher=teacher, session=active_session
        )

        # Session-only record so the student can see "their own" submission
        # in this browser session. Nothing here is persisted to the database
        # against the student, preserving full anonymity of the stored data.
        my_submissions = request.session.get(SESSION_KEY_MY_SUBMISSIONS, [])
        my_submissions.append({
            "teacher_name": teacher.full_name,
            "session_name": active_session.name,
            "ratings": response_snapshot,
            "comment": comment,
        })
        request.session[SESSION_KEY_MY_SUBMISSIONS] = my_submissions

        messages.success(request, "Thank you! Your anonymous feedback has been submitted.")
        return redirect("feedback:thank_you")

    return render(
        request,
        "feedback/submit_form.html",
        {"teacher": teacher, "questions": questions, "review_form": review_form, "rating_range": range(1, 11)},
    )


@login_required
def thank_you(request):
    return render(request, "feedback/thank_you.html")


@login_required
def my_feedback(request):
    """
    Shows feedback the student submitted *in this browser session only*.
    This is intentional: the database itself never links a student to
    their answers, so 'my submitted feedback' can only be reconstructed
    from what the browser remembers about this session -- not queried
    back from the database.
    """
    submissions = request.session.get(SESSION_KEY_MY_SUBMISSIONS, [])
    return render(request, "feedback/my_feedback.html", {"submissions": submissions})
