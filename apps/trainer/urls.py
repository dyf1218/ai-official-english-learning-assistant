"""
URL configuration for trainer app.
"""

from django.urls import path

from apps.trainer import views

app_name = "trainer"

urlpatterns = [
    path("", views.SessionListView.as_view(), name="session_list"),
    path("create/", views.SessionCreateView.as_view(), name="session_create"),
    path(
        "sessions/<uuid:session_id>/",
        views.SessionWorkspaceView.as_view(),
        name="session_workspace",
    ),
    path(
        "sessions/<uuid:session_id>/submit/",
        views.TurnSubmitView.as_view(),
        name="turn_submit",
    ),
    path(
        "sessions/<uuid:session_id>/history/",
        views.TurnHistoryView.as_view(),
        name="turn_history",
    ),
    path(
        "sessions/<uuid:session_id>/archive/",
        views.SessionArchiveView.as_view(),
        name="session_archive",
    ),
]