from django.views.generic import ListView, DeleteView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

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
    success_url = "learning:knowledgeorder_list"


class KnowledgeOrderUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """Создание распорядительного документа"""

    model = KnowledgeOrder
    form_class = KnowledgeOrderForm
    success_url = "learning:knowledgeorder_list"


class KnowledgeOrderDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """Создание распорядительного документа"""

    model = KnowledgeOrder
    success_url = "learning:knowledgeorder_list"