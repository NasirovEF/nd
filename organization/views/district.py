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

from organization.forms import DistrictForm
from organization.models import District, Division


class DistrictListView(ListView):
    """Просмотр списка участков"""

    model = District


class DistrictDetailView(DetailView):
    """Просмотр одной из участков"""

    model = District


class DistrictCreateView(CreateView):
    """Создание участков"""

    model = District
    form_class = DistrictForm

    def get_success_url(self):
        return reverse("organization:organization_list")

    def form_valid(self, form):
        district = form.save()
        division = self.request.GET["division"]
        district.division = Division.objects.get(pk=division)
        form.save()

        return super().form_valid(form)


class DistrictUpdateView(UpdateView):
    """Редактирование участков"""

    model = District
    form_class = DistrictForm

    def get_success_url(self):
        return reverse("organization:organization_list")


class DistrictDeleteView(DeleteView):
    """Удаление участков"""

    model = District
    success_url = reverse_lazy("organization:organization_list")
