from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("django-admin/", admin.site.urls),  # Django's built-in admin (superuser only)
    path("accounts/", include("apps.accounts.urls")),
    path("", include("apps.core.urls")),
    path("profiles/", include("apps.teachers.urls")),  # public teacher profiles - open to all logged-in roles
    path("student/", include("apps.students.urls")),
    path("feedback/", include("apps.feedback.urls")),
    path("suggestions/", include("apps.suggestions.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.BASE_DIR / "static")
