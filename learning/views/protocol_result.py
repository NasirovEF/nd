from learning.forms import ProtocolResultForm
from learning.models import Protocol, ProtocolResult, KnowledgeDate
from django.shortcuts import get_object_or_404, redirect
from django.forms import modelformset_factory
from django.views.generic import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin


class ProtocolResultsUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Protocol
    fields = []
    permission_required = 'learning.change_protocolresult'
    template_name = 'learning/results_edit.html'

    def get_formset_class(self):
        return modelformset_factory(
            ProtocolResult,
            form=ProtocolResultForm,
            extra=0,
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        formset_class = self.get_formset_class()
        context['formset'] = formset_class(
            queryset=ProtocolResult.objects.filter(protocol=self.object)
        )
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        formset_class = self.get_formset_class()
        formset = formset_class(
            request.POST,
            queryset=ProtocolResult.objects.filter(protocol=self.object)
        )

        if not formset.is_valid():
            context = self.get_context_data()
            context['formset'] = formset
            return self.render_to_response(context)

        formset.save()

        programs = self.object.program.all()
        learners = self.object.learner.all()
        directions = {d for p in programs for d in p.direction.all()}

        try:
            for direction in directions:
                for learner in learners:
                    knowledge_date = KnowledgeDate.objects.get(
                        protocol=self.object,
                        direction=direction,
                        learner=learner
                    )
                    knowledge_date.save()
            return redirect('learning:protocol_detail', pk=self.object.pk)

        except KnowledgeDate.DoesNotExist:
            context = self.get_context_data()
            context['formset'] = formset
            context['error'] = 'Не найдено KnowledgeDate для некоторых записей.'
            return self.render_to_response(context)

