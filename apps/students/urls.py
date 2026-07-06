from django.urls import path
from . import views

app_name = "students"

urlpatterns = [
    path("teachers/", views.teacher_list, name="teacher_list"),
]
