from django.urls import path
from . import views

app_name = "suggestions"

urlpatterns = [
    path("", views.board, name="board"),
    path("submit/", views.submit, name="submit"),
    path("<int:suggestion_id>/upvote/", views.upvote, name="upvote"),
]
