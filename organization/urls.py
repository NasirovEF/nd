from django.urls import path
from organization.apps import OrganizationConfig
from organization.views.organization import (
    OrganizationListView,
)
from organization.views.worker import (
    WorkerCreateView,
    WorkerDeleteView,
    WorkerDetailView,
    WorkerUpdateView,
)
from organization.views.group import (
    GroupUpdateView,
    GroupCreateView,
    GroupDeleteView,
)
from organization.views.branch import (
    BranchUpdateView,
    BranchCreateView,
    BranchDeleteView,
)

from organization.views.district import (
    DistrictUpdateView,
    DistrictCreateView,
    DistrictDeleteView,
    DistrictDetailView,
)
from organization.views.division import (
    DivisionUpdateView,
    DivisionCreateView,
    DivisionDeleteView,
)

app_name = OrganizationConfig.name

urlpatterns = [
    path(
        "", OrganizationListView.as_view(), name="organization_list"
    ),

    path("branch_create/", BranchCreateView.as_view(), name="branch_create"),
    path("branch_update/<int:pk>", BranchUpdateView.as_view(), name="branch_update"),
    path("branch_delete/<int:pk>", BranchDeleteView.as_view(), name="branch_delete"),
    path("district_create/", DistrictCreateView.as_view(), name="district_create"),
    path(
        "district_detail/<int:pk>/",
        DistrictDetailView.as_view(),
        name="district_detail",
    ),
    path(
        "district_update/<int:pk>", DistrictUpdateView.as_view(), name="district_update"
    ),
    path(
        "district_delete/<int:pk>", DistrictDeleteView.as_view(), name="district_delete"
    ),
    path("division_create/", DivisionCreateView.as_view(), name="division_create"),

    path(
        "division_update/<int:pk>", DivisionUpdateView.as_view(), name="division_update"
    ),
    path(
        "division_delete/<int:pk>", DivisionDeleteView.as_view(), name="division_delete"
    ),
    path("group_create/", GroupCreateView.as_view(), name="group_create"),
    path("group_update/<int:pk>", GroupUpdateView.as_view(), name="group_update"),
    path("group_delete/<int:pk>", GroupDeleteView.as_view(), name="group_delete"),

    path("worker_create/", WorkerCreateView.as_view(), name="worker_create"),
    path("worker_detail/<int:pk>/", WorkerDetailView.as_view(), name="worker_detail"),
    path("worker_update/<int:pk>", WorkerUpdateView.as_view(), name="worker_update"),
    path("worker_delete/<int:pk>", WorkerDeleteView.as_view(), name="worker_delete"),
]
