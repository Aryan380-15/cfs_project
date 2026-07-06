from django.urls import path
from . import views

app_name = "feedback"

urlpatterns = [
    path("teacher/<int:teacher_id>/notice/", views.feedback_notice, name="feedback_notice"),
    path("teacher/<int:teacher_id>/form/", views.submit_feedback, name="submit_feedback"),
    path("thank-you/", views.thank_you, name="thank_you"),
    path("my-feedback/", views.my_feedback, name="my_feedback"),
]
