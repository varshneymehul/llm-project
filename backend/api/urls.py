from django.urls import path
from . import views

urlpatterns = [
    path("chat/", views.chat_with_llm, name="chat_with_llm"),
    path("health/", views.health_check, name="health_check"),
    path("status/", views.repository_status, name="repository_status"),
    path("reset-retrieval/", views.reset_retrieval_chain, name="reset_retrieval_chain"),
    path("graph-folders/", views.list_graph_folders, name="graph_folders"),
    path("graph-folders/<str:folder_name>/", views.get_graph_folder_details, name="graph_folder_details"),
    path("graph-file/<str:folder>/<str:filename>", views.serve_graph_file, name="serve_graph_file"),
]