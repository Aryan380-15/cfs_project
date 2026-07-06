from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy

from .forms import RoleLoginForm


class RoleAwareLoginView(LoginView):
    """
    Single login page for Admin, Teacher and Student.
    After authenticating, the user is routed to their role's dashboard
    by core:dashboard_redirect (based on user.role / is_superuser).
    """
    template_name = "accounts/login.html"
    authentication_form = RoleLoginForm
    redirect_authenticated_user = True

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"Welcome back, {self.request.user.username}!")
        return response

    def get_success_url(self):
        return reverse_lazy("core:dashboard_redirect")


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect("accounts:login")
