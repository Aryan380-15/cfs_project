from django.conf import settings


def role_context(request):
    """Makes user role and college name available in every template."""
    user = getattr(request, "user", None)
    context = {
        "COLLEGE_NAME": settings.COLLEGE_NAME,
        "current_role": None,
        "unread_notification_count": 0,
    }
    if user and user.is_authenticated:
        context["current_role"] = getattr(user, "role", None)
        context["unread_notification_count"] = user.notifications.filter(is_read=False).count()
    return context
