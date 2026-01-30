from django.urls import reverse, reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    ListView,
    UpdateView,
)
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from organization.forms import OrganizationForm
from organization.models import Organization


class OrganizationListView(LoginRequiredMixin, ListView):
    """Просмотр списка ОСТов"""

    model = Organization

    def get_queryset(self, *args, **kwargs):
        queryset = super().get_queryset(*args, **kwargs)
        queryset = queryset.filter(is_main=True)

        # Собираем ID из ответственностей
        branch_ids = []
        division_ids = []
        district_ids = []
        group_ids = []

        responsibilities = (
            self.request.user.worker.responsibilities
            .select_related('branch', 'division', 'district', 'group')
            .all()
        )

        for responsibil in responsibilities:
            if responsibil.branch:
                branch_ids.append(responsibil.branch.id)
            if responsibil.division:
                division_ids.append(responsibil.division.id)
            if responsibil.district:
                district_ids.append(responsibil.district.id)
            if responsibil.group:
                group_ids.append(responsibil.group.id)

        # Если нет фильтров — возвращаем пустой набор
        if not (branch_ids or division_ids or district_ids or group_ids):
            return queryset

        filtered_orgs = queryset.filter(
            Q(branch__id__in=branch_ids) |
            Q(branch__division__id__in=division_ids) |
            Q(branch__division__district__id__in=district_ids) |
            Q(branch__division__district__group__id__in=group_ids)
        ).distinct()

        return filtered_orgs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Собираем ID (аналогично get_queryset)
        branch_ids = []
        division_ids = []
        district_ids = []
        group_ids = []

        responsibilities = self.request.user.worker.responsibilities.select_related(
            'branch', 'division', 'district', 'group'
        ).all()

        for responsibil in responsibilities:
            if responsibil.branch:
                branch_ids.append(responsibil.branch.id)
            if responsibil.division:
                division_ids.append(responsibil.division.id)
            if responsibil.district:
                district_ids.append(responsibil.district.id)
            if responsibil.group:
                group_ids.append(responsibil.group.id)

        context.update({
            'branch_ids': branch_ids,
            'division_ids': division_ids,
            'district_ids': district_ids,
            'group_ids': group_ids,
        })
        return context


class OrganizationCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """Создание ОСТа"""

    model = Organization
    form_class = OrganizationForm
    permission_required = 'organization.add_organization'

    def get_success_url(self):
        return reverse("organization:organization_list")


class OrganizationUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """Редактирование ОСТа"""

    model = Organization
    form_class = OrganizationForm
    permission_required = 'organization.change_organization'

    def get_success_url(self):
        return reverse("organization:organization_list")


class OrganizationDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Organization
    permission_required = 'organization.delete_organization'
    success_url = reverse_lazy("organization:organization_list")
