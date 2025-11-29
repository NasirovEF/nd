from learning.forms import ProtocolResultForm
from learning.models import Protocol, ProtocolResult, KnowledgeDate
from django.shortcuts import get_object_or_404, redirect
from django.forms import modelformset_factory
from django.views.generic import UpdateView


class ProtocolResultsUpdateView(UpdateView):
    model = Protocol
    fields = []
    template_name = 'learning/results_edit.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if 'formset' not in context:
            ResultFormSet = modelformset_factory(
                ProtocolResult,
                form=ProtocolResultForm,
                extra=0
            )
            context['formset'] = ResultFormSet(
                queryset=ProtocolResult.objects.filter(protocol=self.object)
            )
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        ResultFormSet = modelformset_factory(ProtocolResult, form=ProtocolResultForm, extra=0)

        formset = ResultFormSet(
            request.POST,
            queryset=ProtocolResult.objects.filter(protocol=self.object)
        )
        if formset.is_valid():
            formset.save()
            directions = self.object.direction.all()
            learners = self.object.learner.all()
            for direction in directions:
                for learner in learners:
                    knowledge_date = KnowledgeDate.objects.get(protocol=self.object, direction=direction, learner=learner)
                    knowledge_date.save()

            return redirect('learning:protocol_detail', pk=self.object.pk)
        else:
            context = self.get_context_data()
            context['formset'] = formset
            return self.render_to_response(context)