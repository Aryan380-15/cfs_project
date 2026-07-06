from django.urls import path
from . import views

app_name = "teachers"

urlpatterns = [
    path("<int:teacher_id>/", views.public_profile, name="public_profile"),
]
