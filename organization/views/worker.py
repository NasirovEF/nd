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
from django.utils.datastructures import MultiValueDictKeyError
from organization.forms import WorkerForm
from organization.models import Worker, District, Group, Organization, Branch, Division


class WorkerListView(ListView):
    """Просмотр списка структурных подразделений"""

    model = Worker


class WorkerDetailView(DetailView):
    """Просмотр одной из структурных подразделений"""

    model = Worker


class WorkerCreateView(CreateView):
    """Создание структурных подразделений"""

    model = Worker
    form_class = WorkerForm

    def get_success_url(self):
        return reverse("organization:district_detail", args=[self.object.district.pk])
    
    def form_valid(self, form):
        worker = form.save()
        ost = self.request.GET["ost"]
        branch = self.request.GET["branch"]
        division = self.request.GET["division"]
        district = self.request.GET["district"]
        worker.organization = Organization.objects.get(pk=ost)
        worker.branch = Branch.objects.get(pk=branch)
        worker.division = Division.objects.get(pk=division)
        worker.district = District.objects.get(pk=district)
        try:
            group = self.request.GET["group"]
            worker.group = Group.objects.get(pk=group)
        except MultiValueDictKeyError:
            worker.group = None
        form.save()
        
        return super().form_valid(form)


class WorkerUpdateView(UpdateView):
    """Редактирование структурных подразделений"""

    model = Worker
    form_class = WorkerForm

    def get_success_url(self):
        return reverse("organization:district_detail", args=[self.object.district.pk])


class WorkerDeleteView(DeleteView):
    """Удаление структурных подразделений"""

    model = Worker
    success_url = reverse_lazy("organization:organization_list")
