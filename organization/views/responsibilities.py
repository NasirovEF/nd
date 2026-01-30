from django.urls import reverse, reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    ListView,
    UpdateView,
)
from django.http import Http404
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from organization.forms import ResponsibleForTrainingForm
from organization.models import ResponsibleForTraining, PositionGroup, Organization, Branch, Group, District, Division


class ResponsibleForTrainingListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    """Создание профессии/должности"""

    model = ResponsibleForTraining
    template_name = 'organization/responsible_list.html'
    permission_required = 'organization.view_responsiblefortraining'
    paginate_by = 20

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['model_name'] = self.kwargs['model_name']
        context['model_pk'] = self.kwargs['model_pk']
        context['position_groups'] = PositionGroup.objects.all()
        context['search_params'] = {
            'level': self.request.GET.get('level', ''),
            'affiliation': self.request.GET.get('affiliation', ''),
            'surname': self.request.GET.get('surname', ''),
            'position': self.request.GET.get('position', ''),
            'position_groups': self.request.GET.get('position_groups', ''),
        }
        return context

    def get_queryset(self, *args, **kwargs):
        queryset = super().get_queryset(*args, **kwargs)
        model = self.kwargs['model_name']
        model_pk = self.kwargs['model_pk']
        if model == 'organization':
            queryset = queryset.filter(organization__pk=model_pk)
        elif model == 'branch':
            queryset = queryset.filter(branch__pk=model_pk)
        elif model == 'division':
            queryset = queryset.filter(division__pk=model_pk)
        elif model == 'district':
            queryset = queryset.filter(district__pk=model_pk)
        elif model == 'group':
            queryset = queryset.filter(group__pk=model_pk)

        level = self.request.GET.get("level")
        affiliation = self.request.GET.get("affiliation")
        surname = self.request.GET.get("surname")
        position = self.request.GET.get("position")
        position_groups = self.request.GET.get("position_groups")

        if level:
            queryset = queryset.filter(level__order=level)
        if affiliation:
            queryset = queryset.filter(Q(organization__name__icontains=affiliation) |
                                       Q(branch__name__icontains=affiliation) |
                                       Q(division__name__icontains=affiliation) |
                                       Q(district__name__icontains=affiliation) |
                                       Q(group__name__icontains=affiliation)
                                       )
        if surname:
            queryset = queryset.filter(responsible_worker__surname__icontains=surname)
        if position:
            queryset = queryset.filter(responsible_worker__position__name__name__icontains=position,
                                       responsible_worker__position__is_main=True)
        if position_groups:
            queryset = queryset.filter(position_groups__in=position_groups)
        return queryset



class ResponsibleForTrainingCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """Создание профессии/должности"""

    model = ResponsibleForTraining
    template_name = 'organization/responsible_form.html'
    form_class = ResponsibleForTrainingForm
    permission_required = 'organization.add_responsiblefortraining'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['model_name'] = self.kwargs['model_name']
        context['model_pk'] = self.kwargs['model_pk']
        return context

    def get_success_url(self):
        model_name = self.kwargs['model_name']
        model_pk = self.kwargs['model_pk']
        return reverse("organization:responsible_list", kwargs={'model_name': model_name,
                                                                'model_pk': model_pk})


class ResponsibleForTrainingUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """Редактирование профессии/должности"""

    model = ResponsibleForTraining
    template_name = 'organization/responsible_form.html'
    form_class = ResponsibleForTrainingForm
    permission_required = 'organization.change_responsiblefortraining'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['model_name'] = self.kwargs['model_name']
        context['model_pk'] = self.kwargs['model_pk']
        return context

    def get_success_url(self):
        model_name = self.kwargs['model_name']
        model_pk = self.kwargs['model_pk']
        return reverse("organization:responsible_list", kwargs={'model_name': model_name,
                                                                'model_pk': model_pk})


class ResponsibleForTrainingDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """Удаление профессии/должности"""

    model = ResponsibleForTraining
    template_name = 'organization/responsible_confirm_delete.html'
    permission_required = 'organization.delete_responsiblefortraining'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['model_name'] = self.kwargs['model_name']
        context['model_pk'] = self.kwargs['model_pk']
        return context

    def get_success_url(self):
        model_name = self.kwargs['model_name']
        model_pk = self.kwargs['model_pk']
        return reverse("organization:responsible_list", kwargs={'model_name': model_name,
                                                                'model_pk': model_pk})
