from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse


class RoleBasedAccessMiddleware:
    """
    Restricts access to /admin-panel/, /teacher/ and /student/ URL prefixes
    based on the logged-in user's role. Keeps role checks in one place
    instead of scattering them across every view.
    """

    PROTECTED_PREFIXES = {
        "/admin-panel/": "admin",
        "/teacher/": "teacher",
        "/student/": "student",
    }

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path

        for prefix, required_role in self.PROTECTED_PREFIXES.items():
            if path.startswith(prefix):
                if not request.user.is_authenticated:
                    messages.error(request, "Please log in to continue.")
                    return redirect(f"{reverse('accounts:login')}?next={path}")

                user_role = getattr(request.user, "role", None)
                if user_role != required_role and not request.user.is_superuser:
                    messages.error(request, "You are not authorized to access that page.")
                    return redirect("core:dashboard_redirect")
                break

        return self.get_response(request)
