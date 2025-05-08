from django.urls import path
from . import views

urlpatterns = [
    path("chat/", views.chat_with_llm, name="chat_with_llm"),
    path("health/", views.health_check, name="health_check"),
    path("status/", views.repository_status, name="repository_status"),
]
