from django.urls import path

from learning.apps import LearningConfig
from learning.views.direction import DirectionCreateView, DirectionUpdateView, DirectionDeleteView
from learning.views.learner import LearnerCreateView, LearnerUpdateView, LearnerDeleteView, LearnerListView
from learning.views.program import ProgramCreateView, ProgramUpdateView, ProgramDeleteView
from learning.views.prot_test import TestCreateView
from learning.views.protocol import ProtocolCreateView, ProtocolUpdateView, ProtocolDeleteView, ProtocolListView, \
    ProtocolDetailView
from learning.views.protocol_result import ProtocolResultsUpdateView

app_name = LearningConfig.name

urlpatterns = [
    path("direction_create/", DirectionCreateView.as_view(), name="direction_create"),
    path("direction_update/<int:pk>", DirectionUpdateView.as_view(), name="direction_update"),
    path("direction_delete/<int:pk>", DirectionDeleteView.as_view(), name="direction_delete"),

    path("learner_list/", LearnerListView.as_view(), name="learner_list"),
    path("learner_create/", LearnerCreateView.as_view(), name="learner_create"),
    path("learner_update/<int:pk>", LearnerUpdateView.as_view(), name="learner_update"),
    path("learner_delete/<int:pk>", LearnerDeleteView.as_view(), name="learner_delete"),

    path("program_create/", ProgramCreateView.as_view(), name="program_create"),
    path("program_update/<int:pk>", ProgramUpdateView.as_view(), name="program_update"),
    path("program_delete/<int:pk>", ProgramDeleteView.as_view(), name="program_delete"),

    path("protocol_list/", ProtocolListView.as_view(), name="protocol_list"),
    path("protocol_create/", ProtocolCreateView.as_view(), name="protocol_create"),
    path("protocol_detail/<int:pk>", ProtocolDetailView.as_view(), name="protocol_detail"),
    path("protocol_update/<int:pk>", ProtocolUpdateView.as_view(), name="protocol_update"),
    path("protocol_delete/<int:pk>", ProtocolDeleteView.as_view(), name="protocol_delete"),

    path("protocol_results_edit/<int:pk>", ProtocolResultsUpdateView.as_view(), name="protocol_results_edit"),

    path("test_create/", TestCreateView.as_view(), name="test_create"),
]