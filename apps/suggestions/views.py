import secrets

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.shortcuts import redirect, render, get_object_or_404
from django.views.decorators.http import require_POST

from apps.feedback.utils import contains_abusive_language

from .forms import SuggestionForm
from .models import CollegeSuggestion, SuggestionUpvote

DEVICE_TOKEN_SESSION_KEY = "suggestion_device_token"


def _get_device_token(request):
    """
    A random per-browser-session token (not tied to the user account) used
    only to stop the same browser from upvoting a suggestion twice. It
    carries no identity information.
    """
    token = request.session.get(DEVICE_TOKEN_SESSION_KEY)
    if not token:
        token = secrets.token_hex(16)
        request.session[DEVICE_TOKEN_SESSION_KEY] = token
    return token


@login_required
def board(request):
    """Public suggestion board -- visible to Admin, Teacher and Student alike."""
    suggestions = CollegeSuggestion.objects.all().prefetch_related("responses")

    category = request.GET.get("category", "")
    status = request.GET.get("status", "")
    query = request.GET.get("q", "")

    if category:
        suggestions = suggestions.filter(category=category)
    if status:
        suggestions = suggestions.filter(status=status)
    if query:
        suggestions = suggestions.filter(text__icontains=query)

    paginator = Paginator(suggestions, 10)
    page_obj = paginator.get_page(request.GET.get("page"))

    device_token = _get_device_token(request)
    upvoted_ids = set(
        SuggestionUpvote.objects.filter(device_token=device_token).values_list("suggestion_id", flat=True)
    )

    context = {
        "page_obj": page_obj,
        "categories": CollegeSuggestion.Category.choices,
        "statuses": CollegeSuggestion.Status.choices,
        "selected_category": category,
        "selected_status": status,
        "query": query,
        "upvoted_ids": upvoted_ids,
    }
    return render(request, "suggestions/board.html", context)


@login_required
def submit(request):
    """
    Anonymous suggestion submission. The saved CollegeSuggestion row has
    no reference to the logged-in user at all -- there's no way to trace
    it back to whoever submitted it.
    """
    form = SuggestionForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        text = form.cleaned_data["text"].strip()
        if contains_abusive_language(text):
            messages.error(
                request,
                "Your suggestion contains language that isn't allowed. "
                "Please rewrite it respectfully and constructively.",
            )
        else:
            CollegeSuggestion.objects.create(
                category=form.cleaned_data["category"],
                text=text,
            )
            messages.success(request, "Your anonymous suggestion has been submitted. Thank you!")
            return redirect("suggestions:board")

    return render(request, "suggestions/submit.html", {"form": form})


@login_required
@require_POST
def upvote(request, suggestion_id):
    suggestion = get_object_or_404(CollegeSuggestion, pk=suggestion_id)
    device_token = _get_device_token(request)

    try:
        SuggestionUpvote.objects.create(suggestion=suggestion, device_token=device_token)
        suggestion.upvote_count = suggestion.upvotes.count()
        suggestion.save(update_fields=["upvote_count"])
    except IntegrityError:
        pass  # already upvoted from this browser -- silently ignore

    next_url = request.POST.get("next") or "suggestions:board"
    if next_url.startswith("/"):
        return redirect(next_url)
    return redirect("suggestions:board")
