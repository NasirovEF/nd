from django.urls import reverse, reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from organization.forms import GroupForm
from organization.models import Group, District


class GroupCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """Создание групп"""

    model = Group
    form_class = GroupForm
    permission_required = 'organization.add_group'

    def get_success_url(self):
        return reverse("organization:organization_list")

    def form_valid(self, form):
        group = form.save()
        district = self.request.GET["district"]
        group.district = District.objects.get(pk=district)
        form.save()

        return super().form_valid(form)


class GroupUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """Редактирование групп"""

    model = Group
    form_class = GroupForm
    permission_required = 'organization.change_group'

    def get_success_url(self):
        return reverse("organization:organization_list")


class GroupDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """Удаление групп"""

    model = Group
    permission_required = 'organization.delete_group'
    success_url = reverse_lazy("organization:organization_list")
