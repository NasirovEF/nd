from django.contrib import admin

from .models import Learner, Protocol, ProtocolResult, Program, Direction, KnowledgeDate, Test, Question, Answer, TestResult, StaffDirection

admin.site.register(Learner)
admin.site.register(Protocol)
admin.site.register(ProtocolResult)
admin.site.register(Program)
admin.site.register(Direction)
admin.site.register(KnowledgeDate)
admin.site.register(TestResult)
admin.site.register(StaffDirection)


@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'program')
    search_fields = ('program__name',)


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
