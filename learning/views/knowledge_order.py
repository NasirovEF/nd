from django.views.generic import ListView, DeleteView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
from learning.forms import KnowledgeOrderForm
from learning.models import KnowledgeOrder


class KnowledgeOrderListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    """Просмотр списка распорядительных документов"""

    model = KnowledgeOrder
    permission_required = 'learning.view_knowledgeorder'
    paginate_by = 15


class KnowledgeOrderCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """Создание распорядительного документа"""

    model = KnowledgeOrder
    form_class = KnowledgeOrderForm
    permission_required = 'learning.add_knowledgeorder'
    success_url = reverse_lazy("learning:knowledgeorder_list")


class KnowledgeOrderUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """Создание распорядительного документа"""

    model = KnowledgeOrder
    form_class = KnowledgeOrderForm
    permission_required = 'learning.change_knowledgeorder'
    success_url = reverse_lazy("learning:knowledgeorder_list")


class KnowledgeOrderDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """Создание распорядительного документа"""

    model = KnowledgeOrder
    permission_required = 'learning.delete_knowledgeorder'
    success_url = reverse_lazy("learning:knowledgeorder_list")
