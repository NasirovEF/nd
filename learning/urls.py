from django.urls import path

from learning.apps import LearningConfig
from learning.models import Program, ProgramBriefing
from learning.views.briefing import ProgramBriefingCreateView, ProgramBriefingDetailView, ProgramBriefingUpdateView, \
    ProgramBriefingDeleteView, BriefingDayCreateView, BriefingDayListView, BriefingDayUpdateView, BriefingDayDeleteView, \
    create_bulk_briefing_day, BriefingLogListView
from learning.views.direction import DirectionListView
from learning.views.direction_test import QuestionDeleteView, QuestionListView, QuestionCreateView, QuestionUpdateView
from learning.views.exam import start_exam, take_exam, submit_answers, exam_results, detail_exam_results, \
    all_exam_results, all_exam_assignment, create_bulk_exam_assignment, all_results_for_exam, ExamAssignmentUpdateView, \
    ExamAssignmentDeleteView
from learning.views.knowledge_order import KnowledgeOrderCreateView, KnowledgeOrderListView, KnowledgeOrderUpdateView, \
    KnowledgeOrderDeleteView
from learning.views.learner import LearnerUpdateView, LearnerListView
from learning.views.learning_doc_poster import LearningDocUpdateView, LearningPosterUpdateView
from learning.views.load_docs import generate_protocol, generate_identity
from learning.views.program import ProgramCreateView, ProgramUpdateView, ProgramDeleteView, ProgramDetailView
from learning.views.protocol import ProtocolCreateView, ProtocolUpdateView, ProtocolDeleteView, ProtocolListView, \
    ProtocolDetailView
from learning.views.protocol_result import ProtocolResultsUpdateView
from learning.views.verbal_exam import VerbalExamListView, create_bulk_verbalexam, VerbalExamUpdateView, \
    VerbalExamDeleteView, toggle_exam_status, VerbalExamDetailView, complete_exam_status, create_verbalexam_result

app_name = LearningConfig.name

urlpatterns = [
    path("direction_list/", DirectionListView.as_view(), name="direction_list"),

    path("learner_list/", LearnerListView.as_view(), name="learner_list"),
    path("learner_update/<int:pk>", LearnerUpdateView.as_view(), name="learner_update"),

    path("program_create/<str:model_name>/<int:model_pk>/", ProgramCreateView.as_view(), name="program_create"),
    path("program_detail/<str:model_name>/<int:model_pk>/<int:pk>", ProgramDetailView.as_view(), name="program_detail"),
    path("program_update/<str:model_name>/<int:model_pk>/<int:pk>", ProgramUpdateView.as_view(), name="program_update"),
    path("program_delete/<str:model_name>/<int:model_pk>/<int:pk>", ProgramDeleteView.as_view(), name="program_delete"),

    path('program/<str:model_name>/<int:model_pk>/<int:pk>/docs/', LearningDocUpdateView.as_view(), {
        'model_class': Program
    }, name='program_docs'),
    path('briefing/<str:model_name>/<int:model_pk>/<int:pk>/docs/', LearningDocUpdateView.as_view(), {
        'model_class': ProgramBriefing
    }, name='briefing_docs'),

    path('program/<str:model_name>/<int:model_pk>/<int:pk>/poster/', LearningPosterUpdateView.as_view(), {
        'model_class': Program
    }, name='program_posters'),
    path('briefing/<str:model_name>/<int:model_pk>/<int:pk>/poster/', LearningPosterUpdateView.as_view(), {
        'model_class': ProgramBriefing
    }, name='briefing_posters'),

    path("protocol_list/", ProtocolListView.as_view(), name="protocol_list"),
    path("protocol_create/", ProtocolCreateView.as_view(), name="protocol_create"),
    path("protocol_detail/<int:pk>", ProtocolDetailView.as_view(), name="protocol_detail"),
    path("protocol_update/<int:pk>", ProtocolUpdateView.as_view(), name="protocol_update"),
    path("protocol_delete/<int:pk>", ProtocolDeleteView.as_view(), name="protocol_delete"),

    path("protocol_results_edit/<int:pk>", ProtocolResultsUpdateView.as_view(), name="protocol_results_edit"),

    path('question_list/<int:test_pk>', QuestionListView.as_view(), name='question_list'),
    path("question_delete/<int:pk>", QuestionDeleteView.as_view(), name="question_delete"),
    path("question_create/<int:test_pk>", QuestionCreateView.as_view(), name="question_create"),
    path("question_update/<int:pk>", QuestionUpdateView.as_view(), name="question_update"),

    path('start-exam/<int:learner_id>/<int:assignment_id>/', start_exam, name='start_exam'),
    path('take-exam/<int:learner_id>/<int:result_id>/', take_exam, name='take_exam'),
    path('submit-answers/<int:learner_id>/<int:result_id>/', submit_answers, name='submit_answers'),
    path('results/<int:learner_id>/', exam_results, name='exam_results'),
    path('all_results/', all_exam_results, name='all_exam_results'),
    path('all_results/<int:exam_id>/<int:learner_id>/', all_results_for_exam, name='all_results_for_exam'),
    path('all_assignment/', all_exam_assignment, name='all_exam_assignment'),
    path('detail_exam_results/<int:result_id>/', detail_exam_results, name='detail_exam_results'),
    path('create_bulk_exam_assignment/', create_bulk_exam_assignment, name='create_bulk_exam_assignment'),
    path('exam_assignment_update/<int:pk>', ExamAssignmentUpdateView.as_view(), name='exam_assignment_update'),
    path('exam_assignment_delete/<int:pk>', ExamAssignmentDeleteView.as_view(), name='exam_assignment_delete'),

    path("verbalexam_list/", VerbalExamListView.as_view(), name="verbalexam_list"),
    path("verbalexam_create/", create_bulk_verbalexam, name="verbalexam_create"),
    path("verbalexam_update/<int:pk>", VerbalExamUpdateView.as_view(), name="verbalexam_update"),
    path("verbalexam_delete/<int:pk>", VerbalExamDeleteView.as_view(), name="verbalexam_delete"),
    path("verbalexam_detail/<int:pk>", VerbalExamDetailView.as_view(), name="verbalexam_detail"),
    path('exam/<int:pk>/toggle-status/', toggle_exam_status, name='toggle_exam_status'),
    path('exam/<int:pk>/completed/', complete_exam_status, name='complete_exam_status'),
    path('create_verbalexam_result/<int:pk>/<str:score>/', create_verbalexam_result, name='create_verbalexam_result'),

    path("briefing_program_create/<str:model_name>/<int:model_pk>/", ProgramBriefingCreateView.as_view(), name="briefing_program_create"),
    path("briefing_program_detail/<str:model_name>/<int:model_pk>/<int:pk>", ProgramBriefingDetailView.as_view(), name="briefing_program_detail"),
    path("briefing_program_update/<str:model_name>/<int:model_pk>/<int:pk>", ProgramBriefingUpdateView.as_view(), name="briefing_program_update"),
    path("briefing_program_delete/<str:model_name>/<int:model_pk>/<int:pk>", ProgramBriefingDeleteView.as_view(), name="briefing_program_delete"),

    path("briefing_day_bulk_create/", create_bulk_briefing_day,  name="briefing_day_bulk_create"),
    path("briefing_day_create/<int:learner_pk>", BriefingDayCreateView.as_view(), name="briefing_day_create"),
    path("briefing_day_list/<int:worker_pk>", BriefingDayListView.as_view(), name="briefing_day_list"),
    path("briefing_log_list/<str:model_name>/<int:pk>/", BriefingLogListView.as_view(), name="briefing_log_list"),
    path("briefing_day_update/<int:pk>", BriefingDayUpdateView.as_view(), name="briefing_day_update"),
    path("briefing_day_delete/<int:pk>/<int:worker_pk>", BriefingDayDeleteView.as_view(), name="briefing_day_delete"),

    path("knowledge_order_list/", KnowledgeOrderListView.as_view(), name="knowledge_order_list"),
    path("knowledge_order_create/>", KnowledgeOrderCreateView.as_view(), name="knowledge_order_create"),
    path("knowledge_order_update/<int:pk>", KnowledgeOrderUpdateView.as_view(), name="knowledge_order_update"),
    path("knowledge_order_delete/<int:pk>", KnowledgeOrderDeleteView.as_view(), name="knowledge_order_delete"),


    path("load_protocol/<int:pk>/<str:template_name>", generate_protocol, name="load_protocol"),
    path("load_identity/<int:pk>", generate_identity, name="load_identity")

]