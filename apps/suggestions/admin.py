from django.contrib import admin
from .models import CollegeSuggestion, SuggestionResponse, SuggestionUpvote


class SuggestionResponseInline(admin.TabularInline):
    model = SuggestionResponse
    extra = 1


@admin.register(CollegeSuggestion)
class CollegeSuggestionAdmin(admin.ModelAdmin):
    list_display = ("category", "short_text", "status", "upvote_count", "created_at")
    list_filter = ("category", "status")
    list_editable = ("status",)
    search_fields = ("text",)
    inlines = [SuggestionResponseInline]

    def short_text(self, obj):
        return obj.text[:60]
    short_text.short_description = "Suggestion"


@admin.register(SuggestionUpvote)
class SuggestionUpvoteAdmin(admin.ModelAdmin):
    list_display = ("suggestion", "device_token", "created_at")
