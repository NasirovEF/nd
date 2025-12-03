from django.urls import path

from accident.apps import AccidentConfig
from accident.views import (AccidentCreateView, AccidentDeleteView,
                            AccidentDetailView, AccidentListView,
                            AccidentUpdateView)

app_name = AccidentConfig.name

urlpatterns = [
    path(
        "accident_detail/<int:pk>/",
        AccidentDetailView.as_view(),
        name="accident_detail",
    ),
    path("accident_create/", AccidentCreateView.as_view(), name="accident_create"),
    path(
        "accident_update/<int:pk>/",
        AccidentUpdateView.as_view(),
        name="accident_update",
    ),
    path(
        "accident_delete/<int:pk>/",
        AccidentDeleteView.as_view(),
        name="accident_delete",
    ),
    path("accident_list", AccidentListView.as_view(), name="accident_list"),
]
