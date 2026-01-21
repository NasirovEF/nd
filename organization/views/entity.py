from django.views.generic import DetailView
from django.http import Http404
from django.core.paginator import Paginator
from learning.models import KnowledgeDate, ProgramBriefing, Program, Direction, BriefingDay
from organization.models import Organization, Branch, Group, District, Division, Worker
from django.db.models import Q


def get_program_filter_q(obj, level=None):
    """
    Возвращает Q‑объект для фильтрации программ:
    - относящихся к obj или вышестоящим уровням;
    - (опционально) строго заданного уровня (level).

    :param obj: экземпляр Group/District/Division/Branch/Organization
    :param level: уровень ('1'–'4') или None (все уровни)
    :return: Q‑объект
    """
    q = Q()

    if isinstance(obj, Group):
        if level == '5':
            q &= Q(group=obj)
        elif level == '4':  # Участок (но не группа)
            q &= Q(district=obj.district) & Q(group__isnull=True)
        elif level == '3':  # СП (но не участок)
            q &= Q(division=obj.district.division) & Q(district__isnull=True)
        elif level == '2':  # Филиал (но не СП)
            q &= Q(branch=obj.district.division.branch) & Q(division__isnull=True)
        elif level == '1':  # ОСТ (но не филиал)
            q &= Q(organization=obj.district.division.branch.organization) & Q(branch__isnull=True)
        else:  # Все уровни (без дополнительного фильтра по уровню)
            q = (
                Q(group=obj) |
                Q(district=obj.district, group__isnull=True) |
                Q(division=obj.district.division, district__isnull=True) |
                Q(branch=obj.district.division.branch, division__isnull=True) |
                Q(organization=obj.district.division.branch.organization, branch__isnull=True)
            )

    elif isinstance(obj, District):
        if level == '5':
            q &= Q(group__district=obj)
        elif level == '4':
            q &= Q(district=obj) & Q(group__isnull=True)
        elif level == '3':
            q &= Q(division=obj.division) & Q(district__isnull=True)
        elif level == '2':
            q &= Q(branch=obj.division.branch) & Q(division__isnull=True)
        elif level == '1':
            q &= Q(organization=obj.division.branch.organization) & Q(branch__isnull=True)
        else:
            q = (
                Q(group__district=obj) |
                Q(district=obj) |
                Q(division=obj.division) & Q(district__isnull=True) |
                Q(branch=obj.division.branch) & Q(division__isnull=True) |
                Q(organization=obj.division.branch.organization) & Q(branch__isnull=True)
            )

    elif isinstance(obj, Division):
        if level == '5':
            q &= Q(group__district__division=obj)
        elif level == '4':
            q &= Q(district__division=obj) & Q(group__isnull=True)
        elif level == '3':
            q &= Q(division=obj) & Q(district__isnull=True)
        elif level == '2':
            q &= Q(branch=obj.branch) & Q(division__isnull=True)
        elif level == '1':
            q &= Q(organization=obj.branch.organization) & Q(branch__isnull=True)
        else:
            q = (
                Q(group__district__division=obj) |
                Q(district__division=obj) & Q(group__isnull=True) |
                Q(division=obj) & Q(district__isnull=True) |
                Q(branch=obj.branch) & Q(division__isnull=True) |
                Q(organization=obj.branch.organization) & Q(branch__isnull=True)
            )

    elif isinstance(obj, Branch):
        if level == '5':
            q &= Q(group__district__division__branch=obj)
        elif level == '4':
            q &= Q(district__division__branch=obj)
        elif level == '3':
            q &= Q(division__branch=obj)
        elif level == '2':
            q &= Q(branch=obj) & Q(division__isnull=True)
        elif level == '1':
            q &= Q(organization=obj.organization) & Q(branch__isnull=True)
        else:
            q = (
                Q(group__district__division__branch=obj) |
                Q(district__division__branch=obj) |
                Q(division__branch=obj) |
                Q(branch=obj) & Q(division__isnull=True) |
                Q(organization=obj.organization) & Q(branch__isnull=True)
            )

    elif isinstance(obj, Organization):
        if level == '5':
            q &= Q(group__district__division__branch__organization=obj)
        elif level == '4':
            q &= Q(district__division__branch__organization=obj) & Q(group__isnull=True)
        elif level == '3':
            q &= Q(division__branch__organization=obj) & Q(district__isnull=True)
        elif level == '2':
            q &= Q(branch__organization=obj) & Q(division__isnull=True)
        elif level == '1':
            q &= Q(organization=obj) & Q(branch__isnull=True)
        else:
            q = (
                Q(organization=obj) |
                Q(branch__organization=obj) |
                Q(division__branch__organization=obj) |
                Q(district__division__branch__organization=obj) |
                Q(group__district__division__branch__organization=obj)
            )

    return q


class EntityDetailView(DetailView):
    template_name = 'organization/entity_detail.html'

    def get_queryset(self):
        model_name = self.kwargs['model_name']
        pk = self.kwargs['pk']

        model = {
            'organization': Organization,
            'branch': Branch,
            'group': Group,
            'district': District,
            'division': Division,
        }.get(model_name)

        if not model:
            raise Http404("Модель не найдена")

        return model.objects.filter(pk=pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search_params = {
            'surname': self.request.GET.get('surname', ''),
            'position': self.request.GET.get('position', ''),
            'date_learning_from': self.request.GET.get('date_learning_from', ''),
            'date_learning_to': self.request.GET.get('date_learning_to', ''),
            'date_briefing_from': self.request.GET.get('date_briefing_from', ''),
            'date_briefing_to': self.request.GET.get('date_briefing_to', ''),
        }
        context['search_params'] = search_params

        worker_list = Worker.objects.all()

        if self.kwargs['model_name'] == 'organization':
            worker_list = Worker.objects.filter(district__division__branch__organization=self.object)
        elif self.kwargs['model_name'] == 'branch':
            worker_list = Worker.objects.filter(district__division__branch=self.object)
        elif self.kwargs['model_name'] == 'division':
            worker_list = Worker.objects.filter(district__division=self.object)
        elif self.kwargs['model_name'] == 'district':
            worker_list = Worker.objects.filter(district=self.object)
        elif self.kwargs['model_name'] == 'group':
            worker_list = Worker.objects.filter(group=self.object)

        if search_params['surname']:
            worker_list = worker_list.filter(surname__icontains=search_params['surname'])
        if search_params['position']:
            worker_list = worker_list.filter(position__name__full_name__icontains=search_params['position'])
        if search_params['date_learning_from']:
            valid_learner_ids = KnowledgeDate.objects.filter(
                next_date__gte=search_params['date_learning_from'],
                is_active=True
            ).values_list('learner_id', flat=True)
            worker_list = worker_list.filter(learner__id__in=valid_learner_ids)
        if search_params['date_learning_to']:
            valid_learner_ids = KnowledgeDate.objects.filter(
                next_date__lte=search_params['date_learning_to'],
                is_active=True
            ).values_list('learner_id', flat=True)
            worker_list = worker_list.filter(learner__id__in=valid_learner_ids)
        if search_params['date_briefing_from']:
            valid_learner_ids = BriefingDay.objects.filter(
                next_briefing_day__gte=search_params['date_briefing_from'],
                is_active=True,
            ).values_list('learner_id', flat=True)
            worker_list = worker_list.filter(learner__id__in=valid_learner_ids)
        if search_params['date_briefing_to']:
            valid_learner_ids = BriefingDay.objects.filter(
                next_briefing_day__lte=search_params['date_briefing_to'],
                is_active=True,
            ).values_list('learner_id', flat=True)
            worker_list = worker_list.filter(learner__id__in=valid_learner_ids)

        worker_list = worker_list.order_by('surname', 'name')

        worker_paginator = Paginator(worker_list, 20)
        worker_page_number = self.request.GET.get('worker_page')
        worker_page = worker_paginator.get_page(worker_page_number)

        worker_page.params = search_params.copy()
        context['worker_page'] = worker_page
        return context


class EntityBriefingProgramView(EntityDetailView):
    template_name = 'organization/entity_briefing_program.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search_params = {
            'level_briefing_program': self.request.GET.get('level_briefing_program', ''),
            'brief_prog_name': self.request.GET.get('brief_prog_name', ''),
            'briefing_type': self.request.GET.get('briefing_type', ''),
            'approval_date_from': self.request.GET.get('approval_date_from', ''),
            'approval_date_to': self.request.GET.get('approval_date_to', ''),
            'has_file': self.request.GET.get('has_file', ''),
            'has_not_file': self.request.GET.get('has_not_file', ''),
            'is_active': self.request.GET.get('is_active', ''),
        }
        context['search_params'] = search_params

        level = search_params.get('level_briefing_program')
        program_q = get_program_filter_q(self.object, level=level)

        briefing_program_list = ProgramBriefing.objects \
            .select_related('group', 'district', 'division', 'branch', 'organization') \
            .filter(program_q)

        if search_params['is_active'] == "0":
            briefing_program_list = briefing_program_list.filter()
        elif search_params['is_active'] == "1":
            briefing_program_list = briefing_program_list.filter(is_active=False)
        else:
            briefing_program_list = briefing_program_list.filter(is_active=True)

        if search_params['brief_prog_name']:
            briefing_program_list = briefing_program_list.filter(name__icontains=search_params['brief_prog_name'])
        if search_params['briefing_type']:
            briefing_program_list = briefing_program_list.filter(briefing__briefing_type=search_params['briefing_type'])
        if search_params['has_file'] == "1" and search_params['has_not_file'] != "0":
            briefing_program_list = briefing_program_list.exclude(doc_scan='').filter(doc_scan__isnull=False)
        elif search_params['has_file'] != "1" and search_params['has_not_file'] == "0":
            briefing_program_list = briefing_program_list.filter(doc_scan='')
        elif search_params['has_file'] == "1" and search_params['has_not_file'] == "0":
            briefing_program_list = briefing_program_list.filter()
        if search_params['approval_date_from']:
            briefing_program_list = briefing_program_list.filter(approval_date__gte=search_params['approval_date_from'])
        if search_params['approval_date_to']:
            briefing_program_list = briefing_program_list.filter(approval_date__lte=search_params['approval_date_to'])

        briefing_program_list = briefing_program_list.order_by('-approval_date')

        briefing_program_paginator = Paginator(briefing_program_list, 20)
        briefing_program_page_number = self.request.GET.get('briefing_program_page')
        briefing_program_page = briefing_program_paginator.get_page(briefing_program_page_number)

        briefing_program_page.params = search_params.copy()
        context['briefing_program_page'] = briefing_program_page
        return context


class EntityLearningProgramView(EntityDetailView):
    template_name = 'organization/entity_learning_program.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search_params = {
            'level_learning_program': self.request.GET.get('level_learning_program', ''),
            'learning_prog_name': self.request.GET.get('learning_prog_name', ''),
            'direction': self.request.GET.get('direction', ''),
            'approval_date_from': self.request.GET.get('approval_date_from', ''),
            'approval_date_to': self.request.GET.get('approval_date_to', ''),
            'has_file': self.request.GET.get('has_file', ''),
            'has_not_file': self.request.GET.get('has_not_file', ''),
            'is_active': self.request.GET.get('is_active', ''),
        }
        context['search_params'] = search_params
        context['directions'] = Direction.objects.all()
        level = search_params.get('level_learning_program')
        program_q = get_program_filter_q(self.object, level=level)

        learning_program_list = Program.objects \
            .select_related('group', 'district', 'division', 'branch', 'organization') \
            .filter(program_q)

        if search_params['is_active'] == "0":
            learning_program_list = learning_program_list.filter()
        elif search_params['is_active'] == "1":
            learning_program_list = learning_program_list.filter(is_active=False)
        else:
            learning_program_list = learning_program_list.filter(is_active=True)

        if search_params['learning_prog_name']:
            learning_program_list = learning_program_list.filter(name__icontains=search_params['learning_prog_name'])
        if search_params['direction']:
            learning_program_list = learning_program_list.filter(direction__name__icontains=search_params['direction'])
        if search_params['has_file'] == "1" and search_params['has_not_file'] != "0":
            learning_program_list = learning_program_list.exclude(doc_scan='').filter(doc_scan__isnull=False)
        elif search_params['has_file'] != "1" and search_params['has_not_file'] == "0":
            learning_program_list = learning_program_list.filter(doc_scan='')
        elif search_params['has_file'] == "1" and search_params['has_not_file'] == "0":
            learning_program_list = learning_program_list.filter()
        if search_params['approval_date_from']:
            learning_program_list = learning_program_list.filter(approval_date__gte=search_params['approval_date_from'])
        if search_params['approval_date_to']:
            learning_program_list = learning_program_list.filter(approval_date__lte=search_params['approval_date_to'])

        learning_program_list = learning_program_list.order_by('-approval_date')

        learning_program_paginator = Paginator(learning_program_list, 20)
        learning_program_page_number = self.request.GET.get('learning_program_page')
        learning_program_page = learning_program_paginator.get_page(learning_program_page_number)

        learning_program_page.params = search_params.copy()
        context['learning_program_page'] = learning_program_page
        return context
