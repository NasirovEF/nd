from django.contrib import admin

from .models import Learner, Protocol, ProtocolResult, Program, Direction, KnowledgeDate, Test, Question, Answer, \
    ExamResult, StaffDirection, SubDirection, Exam, ExamAssignment, BriefingDay, Briefing, ProgramBriefing

admin.site.register(Direction)
admin.site.register(SubDirection)
admin.site.register(StaffDirection)


@admin.register(Learner)
class LearnerAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'is_active')
    search_fields = ('worker__name', 'worker__surname',
                     'worker__patronymic', 'position__name__name')


@admin.register(Protocol)
class ProtocolAdmin(admin.ModelAdmin):
    list_display = ('issued_division', '__str__')


@admin.register(ProtocolResult)
class ProtocolResultAdmin(admin.ModelAdmin):
    list_display = ('learner', 'protocol', 'type', 'passed')
    search_fields = ('learner__worker__name', 'learner__worker__surname',
                     'learner__worker__patronymic',)


@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ('name', 'return_affiliation', 'is_active')
    search_fields = ('name', 'direction__name', 'subdirection__name',
                     'organization__name', 'branch__name',
                     'division__name', 'district__name',
                     'group__name')


@admin.register(KnowledgeDate)
class KnowledgeDateAdmin(admin.ModelAdmin):
    list_display = ('learner', 'direction', 'kn_date', 'is_passed', 'next_date', 'is_active')
    search_fields = ('learner__worker__name', 'learner__worker__surname',
                     'learner__worker__patronymic', 'direction__name')


@admin.register(ExamResult)
class ExamResultAdmin(admin.ModelAdmin):
    list_display = ('learner', 'exam', 'test_date', 'is_passed')
    search_fields = ('learner__worker__name', 'learner__worker__surname',
                     'learner__worker__patronymic')


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('__str__',)
    search_fields = ('program__name', 'briefing_program__name')


@admin.register(ExamAssignment)
class ExamAssignmentAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'assigned_date', 'deadline', 'status', 'attempts_left')
    search_fields = ('learner__worker__name', 'learner__worker__surname',
                     'learner__worker__patronymic')


@admin.register(Briefing)
class BriefingAdmin(admin.ModelAdmin):
    list_display = ('briefing_type', 'periodicity')
    search_fields = ('briefing_type', 'periodicity')


@admin.register(BriefingDay)
class BriefingDayAdmin(admin.ModelAdmin):
    list_display = ('learner', 'briefing_type', 'briefing_day', 'next_briefing_day', 'is_active')
    search_fields = ('learner__worker__name', 'learner__worker__surname',
                     'learner__worker__patronymic', 'briefing_type__briefing_type',
                     'briefing_day', 'next_briefing_day')


@admin.register(ProgramBriefing)
class ProgramBriefingAdmin(admin.ModelAdmin):
    list_display = ('name', 'return_affiliation', 'is_active')
    search_fields = ('name', 'briefing__briefing_type',
                     'organization__name', 'branch__name',
                     'division__name', 'district__name',
                     'group__name')


@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'direction', 'sub_direction')
    search_fields = ('direction__name', 'sub_direction__name')


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 1
    max_num = 3
    can_delete = True


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'test')
    inlines = [AnswerInline]
    search_fields = ('test__name',)
