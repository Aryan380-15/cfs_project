import uuid
from django.db import models


class CollegeSuggestion(models.Model):
    """
    Anonymous suggestion/complaint. Deliberately has NO foreign key to
    Student -- there is no way to trace a suggestion back to its author.
    """

    class Category(models.TextChoices):
        LIBRARY = "library", "Library"
        LABS = "labs", "Labs"
        WIFI = "wifi", "Wi-Fi"
        CANTEEN = "canteen", "Canteen"
        CLEANLINESS = "cleanliness", "Cleanliness"
        HOSTEL = "hostel", "Hostel"
        PLACEMENT = "placement", "Placement Cell"
        SPORTS = "sports", "Sports"
        INFRASTRUCTURE = "infrastructure", "Infrastructure"
        ADMINISTRATION = "administration", "Administration"
        EVENTS = "events", "Events"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        UNDER_REVIEW = "under_review", "Under Review"
        IN_PROGRESS = "in_progress", "In Progress"
        IMPLEMENTED = "implemented", "Implemented"
        REJECTED = "rejected", "Rejected"

    public_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    category = models.CharField(max_length=30, choices=Category.choices)
    text = models.TextField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    upvote_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"[{self.get_category_display()}] {self.text[:40]}"


class SuggestionResponse(models.Model):
    """The 'We Did' management response shown publicly under 'You Said -> We Did'."""
    suggestion = models.ForeignKey(CollegeSuggestion, on_delete=models.CASCADE, related_name="responses")
    message = models.TextField()
    responded_by_role = models.CharField(max_length=50, default="Administration")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Response to suggestion #{self.suggestion_id}"


class SuggestionUpvote(models.Model):
    """
    Tracks which session/browser upvoted which suggestion (to prevent
    duplicate upvotes) using a random device token instead of a user FK,
    so upvoting also stays anonymous.
    """
    suggestion = models.ForeignKey(CollegeSuggestion, on_delete=models.CASCADE, related_name="upvotes")
    device_token = models.CharField(max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("suggestion", "device_token")
