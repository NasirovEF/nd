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


class HierarchicalEntityView(DetailView):
    """
    Базовый класс для представлений, работающих с иерархическими сущностями
    (организация → филиал → подразделение → и т.д.).
    """
    model_mapping = {
        'organization': Organization,
        'branch': Branch,
        'group': Group,
        'district': District,
        'division': Division,
    }
    template_name = None
    paginate_by = 20

    def get_model(self):
        """Получаем модель по имени из URL."""
        model_name = self.kwargs['model_name']
        model = self.model_mapping.get(model_name)
        if not model:
            raise Http404("Модель не найдена")
        return model

    def get_queryset(self):
        model = self.get_model()
        pk = self.kwargs['pk']
        return model.objects.filter(pk=pk)

    def get_search_params(self):
        """Собираем параметры поиска из GET."""
        return {
            'surname': self.request.GET.get('surname', ''),
            'position': self.request.GET.get('position', ''),
            'date_learning_from': self.request.GET.get('date_learning_from', ''),
            'date_learning_to': self.request.GET.get('date_learning_to', ''),
            'date_briefing_from': self.request.GET.get('date_briefing_from', ''),
            'date_briefing_to': self.request.GET.get('date_briefing_to', ''),
        }

    def apply_filters(self, queryset, search_params):
        """Применяем фильтры к QuerySet работников."""

        # 1. Текстовые фильтры
        if search_params.get('surname'):
            queryset = queryset.filter(surname__icontains=search_params['surname'])

        if search_params.get('position'):
            queryset = queryset.filter(
                position__name__full_name__icontains=search_params['position']
            )

        # 2. Группируем параметры дат для единообразной обработки
        date_filters = [
            # Обучение
            ('date_learning_from', KnowledgeDate, 'next_date__gte'),
            ('date_learning_to', KnowledgeDate, 'next_date__lte'),
            # Инструктаж
            ('date_briefing_from', BriefingDay, 'next_briefing_day__gte'),
            ('date_briefing_to', BriefingDay, 'next_briefing_day__lte'),
        ]

        for param_name, model, lookup in date_filters:
            if not search_params.get(param_name):
                continue

            # Формируем подзапрос без values_list(flat=True) — эффективнее
            valid_ids = model.objects.filter(
                **{lookup: search_params[param_name]},
                is_active=True
            ).values('learner')  # Возвращает QuerySet с полем learner

            queryset = queryset.filter(learner__in=valid_ids)

        return queryset

    def get_paginated_page(self, queryset, page_param):
        """Пагинируем QuerySet и добавляем параметры поиска."""
        paginator = Paginator(queryset, self.paginate_by)
        page_number = self.request.GET.get(page_param)
        page = paginator.get_page(page_number)
        page.params = self.get_search_params().copy()
        return page



class EntityDetailView(HierarchicalEntityView):
    template_name = 'organization/entity_detail.html'

    def get_worker_queryset(self, entity_obj):
        """Определяем QuerySet работников в зависимости от типа сущности."""
        model_name = self.kwargs['model_name']

        if model_name == 'organization':
            return Worker.objects.filter(district__division__branch__organization=entity_obj)
        elif model_name == 'branch':
            return Worker.objects.filter(district__division__branch=entity_obj)
        elif model_name == 'division':
            return Worker.objects.filter(district__division=entity_obj)
        elif model_name == 'district':
            return Worker.objects.filter(district=entity_obj)
        elif model_name == 'group':
            return Worker.objects.filter(group=entity_obj)

        return Worker.objects.none()  # если тип не распознан

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search_params = self.get_search_params()
        context['search_params'] = search_params

        # Проверяем, что объект существует
        if not self.object:
            return context

        # Получаем работников для текущей сущности
        worker_list = self.get_worker_queryset(self.object)

        # Применяем фильтры
        worker_list = self.apply_filters(worker_list, search_params)
        # Сортируем
        worker_list = worker_list.order_by('surname', 'name')

        # Пагинируем
        worker_page = self.get_paginated_page(worker_list, 'worker_page')
        context['worker_page'] = worker_page

        return context


class ProgramListView(HierarchicalEntityView):
    """
    Базовый класс для отображения списков программ (инструктажей/обучения).
    Должен быть унаследован и настроен.
    """
    # Обязательные атрибуты (должны быть заданы в подклассе)
    program_model = None  # Модель программы (ProgramBriefing/Program)
    template_name = None
    search_fields = {}  # Поля для поиска: {'param_name': 'lookup'}
    extra_context = {}  # Дополнительные данные для контекста

    paginate_by = 20

    def get_search_params(self):
        """Собираем все параметры поиска из GET."""
        params = super().get_search_params()
        params.update({
            'level_program': self.request.GET.get('level_program', ''),
            'program_name': self.request.GET.get('program_name', ''),
            'approval_date_from': self.request.GET.get('approval_date_from', ''),
            'approval_date_to': self.request.GET.get('approval_date_to', ''),
            'has_file': self.request.GET.get('has_file', ''),
            'has_not_file': self.request.GET.get('has_not_file', ''),
            'is_active': self.request.GET.get('is_active', ''),
        })
        # Добавляем специфические поля из search_fields
        for key in self.search_fields.keys():
            params[key] = self.request.GET.get(key, '')
        return params

    def get_base_filter(self):
        """Возвращает базовый фильтр для программ (может быть переопределён)."""
        level = self.get_search_params().get('level_program')
        return get_program_filter_q(self.object, level=level)

    def apply_active_filter(self, queryset, search_params):
        """Фильтрация по is_active."""
        if search_params['is_active'] == "1":
            return queryset.filter(is_active=False)
        elif not search_params['is_active']:
            return queryset.filter(is_active=True)
        return queryset

    def apply_file_filter(self, queryset, search_params):
        """Фильтрация по наличию/отсутствию файла."""
        has_file = search_params['has_file'] == "1"
        has_not_file = search_params['has_not_file'] == "0"

        if has_file and has_not_file:
            return queryset  # игнорируем оба
        elif has_file:
            return queryset.exclude(doc_scan='').filter(doc_scan__isnull=False)
        elif has_not_file:
            return queryset.filter(doc_scan='')
        return queryset

    def apply_search_filters(self, queryset, search_params):
        """Применяем все поисковые фильтры через Q-объекты."""
        q_filters = Q()

        for param, lookup in self.search_fields.items():
            if search_params.get(param):
                q_filters &= Q(**{lookup: search_params[param]})

        if search_params['program_name']:
            q_filters &= Q(name__icontains=search_params['program_name'])
        if search_params['approval_date_from']:
            q_filters &= Q(approval_date__gte=search_params['approval_date_from'])
        if search_params['approval_date_to']:
            q_filters &= Q(approval_date__lte=search_params['approval_date_to'])

        return queryset.filter(q_filters)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search_params = self.get_search_params()
        context['search_params'] = search_params

        # Базовый фильтр
        program_q = self.get_base_filter()

        # Исходный QuerySet
        program_list = self.program_model.objects \
            .select_related('group', 'district', 'division', 'branch', 'organization') \
            .filter(program_q)

        # Применяем фильтры
        program_list = self.apply_active_filter(program_list, search_params)
        program_list = self.apply_file_filter(program_list, search_params)
        program_list = self.apply_search_filters(program_list, search_params)

        # Сортировка
        program_list = program_list.order_by('-approval_date')

        # Пагинация
        program_page = self.get_paginated_page(program_list, 'program_page')
        context['program_page'] = program_page

        # Добавляем дополнительный контекст
        context.update(self.extra_context)

        return context


class EntityBriefingProgramView(ProgramListView):
    template_name = 'organization/entity_briefing_program.html'
    program_model = ProgramBriefing
    search_fields = {
        'briefing_type': 'briefing__briefing_type',
    }


class EntityLearningProgramView(ProgramListView):
    template_name = 'organization/entity_learning_program.html'
    program_model = Program
    search_fields = {
        'direction': 'direction__name',
    }
    extra_context = {
        'directions': Direction.objects.all(),
    }



