from django.contrib import admin

from .models import Learner, Protocol, ProtocolResult, Program, Direction, KnowledgeDate

admin.site.register(Learner)
admin.site.register(Protocol)
admin.site.register(ProtocolResult)
admin.site.register(Program)
admin.site.register(Direction)
admin.site.register(KnowledgeDate)