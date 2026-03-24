from django.views.generic import ListView, DeleteView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
from learning.forms import KnowledgeOrderForm
from learning.models import KnowledgeOrder
from django.db.models import Q


class KnowledgeOrderListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    """Просмотр списка распорядительных документов"""

    model = KnowledgeOrder
    permission_required = 'learning.view_knowledgeorder'
    paginate_by = 15

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['search_params'] = {
            'type': self.request.GET.get('type', ''),
            'doc_number': self.request.GET.get('doc_number', ''),
            'doc_date_from': self.request.GET.get('doc_date_from', ''),
            'doc_date_to': self.request.GET.get('doc_date_to', ''),
            'has_file': self.request.GET.get('has_file', ''),
            'has_not_file': self.request.GET.get('has_not_file', ''),
            'affiliation': self.request.GET.get('affiliation', ''),
        }
        return context

    def get_queryset(self, *args, **kwargs):
        queryset = super().get_queryset(*args, **kwargs)
        type = self.request.GET.get("type")
        doc_number = self.request.GET.get("doc_number")
        doc_date_from = self.request.GET.get("doc_date_from")
        doc_date_to = self.request.GET.get("doc_date_to")
        has_file = self.request.GET.get("has_file")
        has_not_file = self.request.GET.get("has_not_file")
        affiliation = self.request.GET.get("affiliation")

        if type:
            queryset = queryset.filter(type=type)
        if doc_number:
            queryset = queryset.filter(doc_number__icontains=doc_number)
        if doc_date_from:
            queryset = queryset.filter(doc_date__gte=doc_date_from)
        if doc_date_to:
            queryset = queryset.filter(doc_date__lte=doc_date_to)
        if has_file == "1" and has_not_file != "0":
            queryset = queryset.exclude(doc_scan='').filter(doc_scan__isnull=False)
        elif has_file != "1" and has_not_file == "0":
            queryset = queryset.filter(doc_scan='')
        elif has_file == "1" and has_not_file == "0":
            queryset = queryset.filter()
        if affiliation:
            queryset = queryset.filter(Q(organization__name__icontains=affiliation) |
                                       Q(branch__name__icontains=affiliation) |
                                       Q(division__name__icontains=affiliation) |
                                       Q(district__name__icontains=affiliation) |
                                       Q(group__name__icontains=affiliation)
                                       )

        return queryset

class KnowledgeOrderCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """Создание распорядительного документа"""

    model = KnowledgeOrder
    form_class = KnowledgeOrderForm
    permission_required = 'learning.add_knowledgeorder'
    success_url = reverse_lazy("learning:knowledge_order_list")


class KnowledgeOrderUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """Создание распорядительного документа"""

    model = KnowledgeOrder
    form_class = KnowledgeOrderForm
    permission_required = 'learning.change_knowledgeorder'
    success_url = reverse_lazy("learning:knowledge_order_list")


class KnowledgeOrderDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """Создание распорядительного документа"""

    model = KnowledgeOrder
    permission_required = 'learning.delete_knowledgeorder'
    success_url = reverse_lazy("learning:knowledge_order_list")
