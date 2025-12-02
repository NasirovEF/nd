from django.contrib import admin

from .models import Learner, Protocol, ProtocolResult, Program, Direction, KnowledgeDate, Test, Question, Answer, TestResult, StaffDirection

admin.site.register(Learner)
admin.site.register(Protocol)
admin.site.register(ProtocolResult)
admin.site.register(Program)
admin.site.register(Direction)
admin.site.register(KnowledgeDate)
admin.site.register(Test)
admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(TestResult)
admin.site.register(StaffDirection)