from django.urls import path

from learning.apps import LearningConfig
from learning.models import Program, ProgramBriefing
from learning.views.briefing import ProgramBriefingCreateView, ProgramBriefingDetailView, ProgramBriefingUpdateView, \
    ProgramBriefingDeleteView, BriefingDayCreateView, BriefingDayListView, BriefingDayUpdateView, BriefingDayDeleteView
from learning.views.direction import DirectionListView
from learning.views.direction_test import QuestionDeleteView, QuestionListView, QuestionCreateView, QuestionUpdateView
from learning.views.exam import start_exam, take_exam, submit_answers, exam_results, detail_exam_results, \
    all_exam_results
from learning.views.learner import LearnerUpdateView, LearnerListView
from learning.views.learning_doc_poster import LearningDocUpdateView, LearningPosterUpdateView
from learning.views.program import ProgramCreateView, ProgramUpdateView, ProgramDeleteView, ProgramDetailView
from learning.views.protocol import ProtocolCreateView, ProtocolUpdateView, ProtocolDeleteView, ProtocolListView, \
    ProtocolDetailView
from learning.views.protocol_result import ProtocolResultsUpdateView

app_name = LearningConfig.name

urlpatterns = [
    path("direction_list/", DirectionListView.as_view(), name="direction_list"),

    path("learner_list/", LearnerListView.as_view(), name="learner_list"),
    path("learner_update/<int:pk>", LearnerUpdateView.as_view(), name="learner_update"),

    path("program_create/", ProgramCreateView.as_view(), name="program_create"),
    path("program_detail/<int:pk>", ProgramDetailView.as_view(), name="program_detail"),
    path("program_update/<int:pk>", ProgramUpdateView.as_view(), name="program_update"),
    path("program_delete/<int:pk>", ProgramDeleteView.as_view(), name="program_delete"),

    path('program/<int:pk>/docs/', LearningDocUpdateView.as_view(), {
        'model_class': Program
    }, name='program_docs'),
    path('briefing/<int:pk>/docs/', LearningDocUpdateView.as_view(), {
        'model_class': ProgramBriefing
    }, name='briefing_docs'),

    path('program/<int:pk>/poster/', LearningPosterUpdateView.as_view(), {
        'model_class': Program
    }, name='program_posters'),
    path('briefing/<int:pk>/poster/', LearningPosterUpdateView.as_view(), {
        'model_class': ProgramBriefing
    }, name='briefing_posters'),

    path("protocol_list/", ProtocolListView.as_view(), name="protocol_list"),
    path("protocol_create/", ProtocolCreateView.as_view(), name="protocol_create"),
    path("protocol_detail/<int:pk>", ProtocolDetailView.as_view(), name="protocol_detail"),
    path("protocol_update/<int:pk>", ProtocolUpdateView.as_view(), name="protocol_update"),
    path("protocol_delete/<int:pk>", ProtocolDeleteView.as_view(), name="protocol_delete"),

    path("protocol_results_edit/<int:pk>", ProtocolResultsUpdateView.as_view(), name="protocol_results_edit"),

    #path("test_update/<int:pk>", TestUpdateView.as_view(), name="test_update"),

    path('question_list/<int:test_pk>', QuestionListView.as_view(), name='question_list'),
    path("question_delete/<int:pk>", QuestionDeleteView.as_view(), name="question_delete"),
    path("question_create/<int:test_pk>", QuestionCreateView.as_view(), name="question_create"),
    path("question_update/<int:pk>", QuestionUpdateView.as_view(), name="question_update"),

    path('start-exam/<int:learner_id>/<int:assignment_id>/', start_exam, name='start_exam'),
    path('take-exam/<int:learner_id>/<int:result_id>/', take_exam, name='take_exam'),
    path('submit-answers/<int:learner_id>/<int:result_id>/', submit_answers, name='submit_answers'),
    path('results/<int:learner_id>/', exam_results, name='exam_results'),
    path('all_results/', all_exam_results, name='all_exam_results'),

    path('detail_exam_results/<int:result_id>/', detail_exam_results, name='detail_exam_results'),

    path("briefing_program_create/", ProgramBriefingCreateView.as_view(), name="briefing_program_create"),
    path("briefing_program_detail/<int:pk>", ProgramBriefingDetailView.as_view(), name="briefing_program_detail"),
    path("briefing_program_update/<int:pk>", ProgramBriefingUpdateView.as_view(), name="briefing_program_update"),
    path("briefing_program_delete/<int:pk>", ProgramBriefingDeleteView.as_view(), name="briefing_program_delete"),

    path("briefing_day_create/<int:learner_pk>", BriefingDayCreateView.as_view(), name="briefing_day_create"),
    path("briefing_day_list/<int:worker_pk>", BriefingDayListView.as_view(), name="briefing_day_list"),
    path("briefing_day_update/<int:pk>", BriefingDayUpdateView.as_view(), name="briefing_day_update"),
    path("briefing_day_delete/<int:pk>/<int:worker_pk>", BriefingDayDeleteView.as_view(), name="briefing_day_delete"),

]