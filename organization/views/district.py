from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
    View,
)
from django.core.paginator import Paginator
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

from learning.models import KnowledgeDate
from organization.forms import DistrictForm
from organization.models import District, Division


class DistrictListView(ListView):
    """Просмотр списка участков"""

    model = District


class DistrictDetailView(DetailView):
    """Просмотр одной из участков"""

    model = District

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        object = self.object
        search_params = {
            'surname': self.request.GET.get('surname', ''),
            'position': self.request.GET.get('position', ''),
            'date_learning': self.request.GET.get('date_learning', ''),
            'date_briefing': self.request.GET.get('date_briefing', ''),
        }
        context['search_params'] = search_params

        worker_list = object.worker.all()

        if search_params['surname']:
            worker_list = worker_list.filter(surname__icontains=search_params['surname'])
        if search_params['position']:
            worker_list = worker_list.filter(position__name__full_name__icontains=search_params['position'])
        if search_params['date_learning']:
            valid_learner_ids = KnowledgeDate.objects.filter(
                next_date=search_params['date_learning'],
                is_active=True
            ).values_list('learner_id', flat=True)
            worker_list = worker_list.filter(learner__id__in=valid_learner_ids)
        if search_params['date_briefing']:
            valid_learner_ids = KnowledgeDate.objects.filter(
                next_date=search_params['date_briefing'],
                is_active=True,
            ).values_list('learner_id', flat=True)
            worker_list = worker_list.filter(learner__id__in=valid_learner_ids)
        worker_paginator = Paginator(worker_list, 20)
        worker_page_number = self.request.GET.get('worker_page')
        worker_page = worker_paginator.get_page(worker_page_number)

        worker_page.params = search_params.copy()
        context['worker_page'] = worker_page

        briefing_programs = object.programbriefing_set.all()
        briefing_paginator = Paginator(briefing_programs, 10)
        briefing_page_number = self.request.GET.get('briefing_page')
        context['briefing_page'] = briefing_paginator.get_page(briefing_page_number)

        learning_programs = object.program_set.all()
        learning_paginator = Paginator(learning_programs, 10)
        learning_page_number = self.request.GET.get('learning_page')
        context['learning_page'] = learning_paginator.get_page(learning_page_number)

        return context


class DistrictCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """Создание участков"""

    model = District
    form_class = DistrictForm
    permission_required = 'organization.add_district'

    def get_success_url(self):
        return reverse("organization:organization_list")

    def form_valid(self, form):
        district = form.save()
        division = self.request.GET["division"]
        district.division = Division.objects.get(pk=division)
        form.save()

        return super().form_valid(form)


class DistrictUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """Редактирование участков"""

    model = District
    form_class = DistrictForm
    permission_required = 'organization.change_district'

    def get_success_url(self):
        return reverse("organization:organization_list")


class DistrictDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """Удаление участков"""

    model = District
    permission_required = 'organization.delete_districtёёёёёёёёёёёёёёёёёёёёёё'
    success_url = reverse_lazy("organization:organization_list")
