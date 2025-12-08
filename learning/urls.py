from django.urls import path

from learning.apps import LearningConfig
from learning.views.learner import LearnerCreateView, LearnerUpdateView, LearnerDeleteView, LearnerListView
from learning.views.learning_doc_poster import LearningDocUpdateView, LearningPosterUpdateView
from learning.views.program import ProgramCreateView, ProgramUpdateView, ProgramDeleteView, ProgramDetailView
from learning.views.prot_test import TestUpdateView
from learning.views.protocol import ProtocolCreateView, ProtocolUpdateView, ProtocolDeleteView, ProtocolListView, \
    ProtocolDetailView
from learning.views.protocol_result import ProtocolResultsUpdateView

app_name = LearningConfig.name

urlpatterns = [

    path("learner_list/", LearnerListView.as_view(), name="learner_list"),
    path("learner_update/<int:pk>", LearnerUpdateView.as_view(), name="learner_update"),

    path("program_create/", ProgramCreateView.as_view(), name="program_create"),
    path("program_detail/<int:pk>", ProgramDetailView.as_view(), name="program_detail"),
    path("program_update/<int:pk>", ProgramUpdateView.as_view(), name="program_update"),
    path("program_delete/<int:pk>", ProgramDeleteView.as_view(), name="program_delete"),
    path("learning_doc_update/<int:pk>", LearningDocUpdateView.as_view(), name="learning_doc_update"),
    path("learning_poster_update/<int:pk>", LearningPosterUpdateView.as_view(), name="learning_poster_update"),

    path("protocol_list/", ProtocolListView.as_view(), name="protocol_list"),
    path("protocol_create/", ProtocolCreateView.as_view(), name="protocol_create"),
    path("protocol_detail/<int:pk>", ProtocolDetailView.as_view(), name="protocol_detail"),
    path("protocol_update/<int:pk>", ProtocolUpdateView.as_view(), name="protocol_update"),
    path("protocol_delete/<int:pk>", ProtocolDeleteView.as_view(), name="protocol_delete"),

    path("protocol_results_edit/<int:pk>", ProtocolResultsUpdateView.as_view(), name="protocol_results_edit"),

    path("test_update/<int:pk>", TestUpdateView.as_view(), name="test_update"),

]