from django.urls import path
from organization.apps import OrganizationConfig
from organization.views.organization import (
    OrganizationListView,
    OrganizationUpdateView,
    OrganizationCreateView,
    OrganizationDeleteView,
    OrganizationDetailView,
)
from organization.views.worker import (
    WorkerCreateView,
    WorkerDeleteView,
    WorkerDetailView,
    WorkerListView,
    WorkerUpdateView,
)
from organization.views.group import (
    GroupListView,
    GroupUpdateView,
    GroupCreateView,
    GroupDeleteView,
    GroupDetailView,
)
from organization.views.branch import (
    BranchUpdateView,
    BranchCreateView,
    BranchDeleteView,
    BranchDetailView,
    BranchListView,
)
from organization.views.position import (
    PositionCreateView,
    PositionListView,
    PositionDeleteView,
    PositionDetailView,
    PositionUpdateView,
)
from organization.views.district import (
    DistrictUpdateView,
    DistrictListView,
    DistrictCreateView,
    DistrictDeleteView,
    DistrictDetailView,
)
from organization.views.division import (
    DivisionUpdateView,
    DivisionListView,
    DivisionCreateView,
    DivisionDeleteView,
    DivisionDetailView,
)

app_name = OrganizationConfig.name

urlpatterns = [
    path(
        "organization_list/", OrganizationListView.as_view(), name="organization_list"
    ),
    path(
        "organization_create/",
        OrganizationCreateView.as_view(),
        name="organization_create",
    ),
    # path(
    #     "organization_detail/<int:pk>/",
    #     OrganizationDetailView.as_view(),
    #     name="organization_detail",
    # ),
    path(
        "organization_update/<int:pk>",
        OrganizationUpdateView.as_view(),
        name="organization_update",
    ),
    path(
        "organization_delete/<int:pk>",
        OrganizationDeleteView.as_view(),
        name="organization_delete",
    ),
    #path("branch_list/", BranchListView.as_view(), name="branch_list"),
    path("branch_create/", BranchCreateView.as_view(), name="branch_create"),
    #path("branch_detail/<int:pk>/", BranchDetailView.as_view(), name="branch_detail"),
    path("branch_update/<int:pk>", BranchUpdateView.as_view(), name="branch_update"),
    path("branch_delete/<int:pk>", BranchDeleteView.as_view(), name="branch_delete"),
    #path("district_list/", DistrictListView.as_view(), name="district_list"),
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
    #path("division_list/", DivisionListView.as_view(), name="division_list"),
    path("division_create/", DivisionCreateView.as_view(), name="division_create"),
    # path(
    #     "division_detail/<int:pk>/",
    #     DivisionDetailView.as_view(),
    #     name="division_detail",
    # ),
    path(
        "division_update/<int:pk>", DivisionUpdateView.as_view(), name="division_update"
    ),
    path(
        "division_delete/<int:pk>", DivisionDeleteView.as_view(), name="division_delete"
    ),
    #path("group_list/", GroupListView.as_view(), name="group_list"),
    path("group_create/", GroupCreateView.as_view(), name="group_create"),
    #path("group_detail/<int:pk>/", GroupDetailView.as_view(), name="group_detail"),
    path("group_update/<int:pk>", GroupUpdateView.as_view(), name="group_update"),
    path("group_delete/<int:pk>", GroupDeleteView.as_view(), name="group_delete"),
    #path("position_list/", PositionListView.as_view(), name="position_list"),
    path("position_create/", PositionCreateView.as_view(), name="position_create"),
    path(
        "position_detail/<int:pk>/",
        PositionDetailView.as_view(),
        name="position_detail",
    ),
    path(
        "position_update/<int:pk>", PositionUpdateView.as_view(), name="position_update"
    ),
    path(
        "position_delete/<int:pk>", PositionDeleteView.as_view(), name="position_delete"
    ),
    #path("worker_list/", WorkerListView.as_view(), name="worker_list"),
    path("worker_create/", WorkerCreateView.as_view(), name="worker_create"),
    path("worker_detail/<int:pk>/", WorkerDetailView.as_view(), name="worker_detail"),
    path("worker_update/<int:pk>", WorkerUpdateView.as_view(), name="worker_update"),
    path("worker_delete/<int:pk>", WorkerDeleteView.as_view(), name="worker_delete"),
]
