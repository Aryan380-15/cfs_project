from django.contrib import admin
from .models import (
    FeedbackQuestion,
    TeacherAssignment,
    FeedbackSubmissionTracker,
    FeedbackResponse,
    FeedbackReview,
)


@admin.register(FeedbackQuestion)
class FeedbackQuestionAdmin(admin.ModelAdmin):
    list_display = ("text", "order", "is_active")
    list_editable = ("order", "is_active")


@admin.register(TeacherAssignment)
class TeacherAssignmentAdmin(admin.ModelAdmin):
    list_display = ("teacher", "subject", "student", "session")
    list_filter = ("session", "teacher")


@admin.register(FeedbackSubmissionTracker)
class FeedbackSubmissionTrackerAdmin(admin.ModelAdmin):
    """
    Visible to Admin ONLY to confirm who has/hasn't submitted (for reminders).
    Deliberately does not join to FeedbackResponse/FeedbackReview anywhere
    in the codebase, preserving anonymity of actual answers.
    """
    list_display = ("student", "teacher", "session", "submitted_at")
    list_filter = ("session", "teacher")


@admin.register(FeedbackResponse)
class FeedbackResponseAdmin(admin.ModelAdmin):
    list_display = ("teacher", "question", "rating", "session", "created_at")
    list_filter = ("teacher", "session", "question")
    # No student field exists on this model - fully anonymous by design.


@admin.register(FeedbackReview)
class FeedbackReviewAdmin(admin.ModelAdmin):
    list_display = ("teacher", "session", "moderation_status", "created_at")
    list_filter = ("moderation_status", "teacher", "session")
    search_fields = ("comment",)
