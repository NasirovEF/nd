from django.urls import reverse, reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    ListView,
    UpdateView,
)
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from organization.forms import ResponsibleForTrainingForm
from organization.models import ResponsibleForTraining


class ResponsibleForTrainingListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    """Создание профессии/должности"""

    model = ResponsibleForTraining
    template_name = 'organization/responsible_list.html'
    permission_required = 'organization.view_responsiblefortraining'
    paginate_by = 20

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['model_name'] = self.request.GET.get('model_name')
        context['pk'] = self.request.GET.get('pk')
        return context



class ResponsibleForTrainingCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """Создание профессии/должности"""

    model = ResponsibleForTraining
    template_name = 'organization/responsible_form.html'
    form_class = ResponsibleForTrainingForm
    permission_required = 'organization.add_responsiblefortraining'

    def get_success_url(self):
        return reverse("organization:responsible_list")


class ResponsibleForTrainingUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """Редактирование профессии/должности"""

    model = ResponsibleForTraining
    template_name = 'organization/responsible_form.html'
    form_class = ResponsibleForTrainingForm
    permission_required = 'organization.change_responsiblefortraining'

    def get_success_url(self):
        return reverse("organization:responsible_list")


class ResponsibleForTrainingDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """Удаление профессии/должности"""

    model = ResponsibleForTraining
    template_name = 'organization/responsible_confirm_delete.html'
    permission_required = 'organization.delete_responsiblefortraining'
    success_url = reverse_lazy("organization:responsible_list")
