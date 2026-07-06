import uuid
from django.db import models
from apps.core.models import AcademicSession, Subject
from apps.teachers.models import Teacher
from apps.students.models import Student


class FeedbackQuestion(models.Model):
    """Standard rating questions (1-10 scale). Admin can add/edit/deactivate."""
    text = models.CharField(max_length=255)
    order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.text


class TeacherAssignment(models.Model):
    """
    Which students are officially assigned to which teacher/subject/session.
    Used ONLY to verify eligibility before allowing feedback submission.
    """
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name="assignments")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="assignments")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="assignments")
    session = models.ForeignKey(AcademicSession, on_delete=models.CASCADE, related_name="assignments")

    class Meta:
        unique_together = ("teacher", "subject", "student", "session")

    def __str__(self):
        return f"{self.student} -> {self.teacher} ({self.subject})"


class FeedbackSubmissionTracker(models.Model):
    """
    ANONYMITY-CRITICAL TABLE.

    This is the ONLY table in the system that links a student to a teacher.
    It exists purely to enforce "submit feedback only once per teacher per
    session" and to check eligibility. It intentionally has NO foreign key
    or shared identifier with FeedbackResponse/FeedbackReview, so nobody
    -- not even a database admin -- can join this table to actual answers
    to identify who wrote what.
    """
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="submission_records")
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name="submission_records")
    session = models.ForeignKey(AcademicSession, on_delete=models.CASCADE, related_name="submission_records")
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("student", "teacher", "session")

    def __str__(self):
        return f"Tracker: submitted (student/teacher hidden from reports)"


class FeedbackResponse(models.Model):
    """
    Stores the actual anonymous rating answers. Deliberately has NO
    foreign key to Student. `anonymous_id` groups the set of question
    ratings that belong to a single (unidentified) submission so they
    can be displayed together, without ever tying back to a person.
    """
    anonymous_id = models.UUIDField(default=uuid.uuid4, editable=False)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name="feedback_responses")
    session = models.ForeignKey(AcademicSession, on_delete=models.CASCADE, related_name="feedback_responses")
    question = models.ForeignKey(FeedbackQuestion, on_delete=models.CASCADE, related_name="responses")
    rating = models.PositiveSmallIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=["teacher", "session"])]

    def __str__(self):
        return f"Rating {self.rating}/10 for {self.teacher} - {self.question}"


class FeedbackReview(models.Model):
    """Anonymous free-text comment, optionally attached to a submission."""

    class ModerationStatus(models.TextChoices):
        APPROVED = "approved", "Approved"
        FLAGGED = "flagged", "Flagged for Review"
        REJECTED = "rejected", "Rejected"

    anonymous_id = models.UUIDField(default=uuid.uuid4, editable=False)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name="reviews")
    session = models.ForeignKey(AcademicSession, on_delete=models.CASCADE, related_name="reviews")
    comment = models.TextField()
    moderation_status = models.CharField(max_length=20, choices=ModerationStatus.choices, default=ModerationStatus.APPROVED)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Anonymous review for {self.teacher}"
