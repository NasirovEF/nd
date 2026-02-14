from django.core.mail import send_mail
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)
from accident.forms import AccidentForm
from accident.models import Accident, AccidentСategory, Organization
from accident.services import insert_line_breaks
from config.settings import EMAIL_HOST_USER
from datetime import date
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
import plotly.graph_objects as go
import plotly.offline as opy
from collections import Counter
from datetime import datetime
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Q
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector


def find_similar_accidents(accident_id, limit=5):
    try:
        original = Accident.objects.get(id=accident_id)
    except Accident.DoesNotExist:
        return []

    query = ~Q(id=original.id)
    similar = Accident.objects.filter(query)

    # Полнотекстовый поиск (если есть описание)
    if original.description:
        search_text = original.description[:500]  # обрезаем длинный текст
        search_query = SearchQuery(search_text, config='russian')
        search_vector = SearchVector('description', config='russian')
        similar = similar.annotate(rank=SearchRank(search_vector, search_query))
        similar = similar.order_by('-rank')

    # Фильтры
    if original.category:
        similar = similar.filter(category=original.category)
    if original.organization:
        similar = similar.filter(organization=original.organization)

    similar = similar.filter(
        victims_count__gte=original.victims_count - 2,
        victims_count__lte=original.victims_count + 2
    )

    if original.scene:
        similar = similar.filter(scene__icontains=original.scene[:50])

    # Оптимизация загрузки
    similar = similar.select_related('category', 'organization').only(
        'id', 'order', 'date', 'description', 'scene',
        'category__id', 'organization__id', 'victims_count'
    )

    # Ручной расчёт, если нет описания или ранжирования
    if not original.description or 'rank' not in similar.query.annotations:
        def calculate_score(accident):
            score = 0
            if accident.category == original.category:
                score += 10
            if accident.organization == original.organization:
                score += 8
            if abs(accident.victims_count - original.victims_count) <= 2:
                score += 7 - abs(accident.victims_count - original.victims_count)
            if original.scene and accident.scene and original.scene.lower() in accident.scene.lower():
                score += 5
            return score

        results = sorted(similar, key=calculate_score, reverse=True)
    else:
        results = list(similar[:limit])

    return results[:limit]




class AccidentListView(ListView):
    model = Accident
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        organizations = Organization.objects.all()
        context["organizations"] = organizations
        categories = AccidentСategory.objects.all()
        context["categories"] = categories
        date_now = str(date.today())
        context["date_now"] = date_now
        context['search_params'] = {
            'order': self.request.GET.get('order', ''),
            'date_from': self.request.GET.get('date_from', ''),
            'date_to': self.request.GET.get('date_to', ''),
            'ost': self.request.GET.get('OST', ''),
            'category': self.request.GET.get('category', ''),
            'description': self.request.GET.get('description', ''),
            'is_death': self.request.GET.get('is_death'),
        }
        return context

    def get_queryset(self, *args, **kwargs):
        queryset = super().get_queryset(*args, **kwargs)
        order = self.request.GET.get("order")
        date_from = self.request.GET.get("date_from")
        date_to = self.request.GET.get("date_to")
        ost = self.request.GET.get("OST")
        category = self.request.GET.get("category")
        description = self.request.GET.get("description")
        is_death = self.request.GET.get("is_death")

        if order:
            queryset = queryset.filter(order__icontains=order)
        if date_from:
            queryset = queryset.filter(date__gte=date_from)
        if date_to:
            queryset = queryset.filter(date__lte=date_to)
        if ost:
            queryset = queryset.filter(organization__name__icontains=ost)
        if category:
            queryset = queryset.filter(category__name__icontains=category)
        if is_death == '1':
            queryset = queryset.filter(is_death=True)
        elif is_death == '0':
            queryset = queryset.filter(is_death=False)
        else:
            queryset
        if description:
            queryset = queryset.filter(description__icontains=description)

        return queryset


class AccidentDetailView(DetailView):
    model = Accident

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['similar_accidents'] = find_similar_accidents(self.object.pk)
        return context


class AccidentCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Accident
    form_class = AccidentForm
    permission_required = 'accident.add_accident'

    def get_success_url(self):
        return reverse("accident:accident_detail", args=[self.object.pk])

    def form_valid(self, form):
        object = form.save()
        host = self.request.get_host()
        # заглушка кода на случай введения уведомления через почту
        # send_mail(
        #     subject=f"Информация о новом несчастном случае",
        #     message=f"Внимание в АСУ НС добавлена информация о новом несчастном случае. "
        #     f"Для ознакомления перейдите по ссылке: http://{host}/accident/accident_detail/{object.pk}",
        #     from_email=EMAIL_HOST_USER,
        #     recipient_list=["i@ef-nasirov.ru",],
        # )
        return super().form_valid(form)


class AccidentUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Accident
    form_class = AccidentForm
    permission_required = 'accident.change_accident'

    def get_success_url(self):
        return reverse("accident:accident_detail", args=[self.object.pk])


class AccidentDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Accident
    permission_required = 'accident:delete_accident'
    success_url = reverse_lazy("accident:accident_list")


@login_required
@permission_required('accident.view_accident', raise_exception=True)
def accident_statistics(request):
    # Получаем все записи
    accidents = Accident.objects.all()

    # 1. График: Количество НС по категориям
    # Формируем данные с переносами
    category_data = Counter(acc.category.name for acc in accidents if acc.category)
    categories = list(category_data.keys())
    values = list(category_data.values())

    # Применяем перенос строк к каждой категории
    wrapped_categories = [insert_line_breaks(cat, max_chars=40) for cat in categories]

    # Строим горизонтальный бар‑чарт
    fig1 = go.Figure(data=[go.Bar(
        y=wrapped_categories,
        x=values,
        orientation='h',
        marker_color='indianred',
        hovertext=categories,
        hoverinfo='text+x'
    )])

    fig1.update_layout(
        title="Количество НС по категориям",
        xaxis_title="Количество",
        yaxis_title="Категория",
        yaxis=dict(
            tickmode='array',
            tickvals=wrapped_categories,  # Явно задаём значения тиков
            ticktext=wrapped_categories,  # И их отображения
            tickfont=dict(size=10),
            automargin=True  # Автоматически подбирает отступы
        ),
        margin=dict(l=150, r=20, t=50, b=20),  # Левый отступ для длинных подписей
        height=max(400, 30 * len(categories))  # Адаптивная высота
    )

    graph1 = opy.plot(fig1, auto_open=False, output_type='div')

    # 2. График: Динамика по годам
    year_data = Counter(acc.date.year for acc in accidents)
    fig2 = go.Figure(data=[go.Scatter(
        x=sorted(year_data.keys()),
        y=[year_data[year] for year in sorted(year_data.keys())],
        mode='lines+markers'
    )])
    fig2.update_layout(title="Динамика НС по годам", xaxis_title="Год", yaxis_title="Количество")
    graph2 = opy.plot(fig2, auto_open=False, output_type='div')

    # 3. График: Соотношение смертельных/несмертельных
    death_count = accidents.filter(is_death=True).count()
    non_death_count = accidents.count() - death_count
    fig3 = go.Figure(data=[go.Pie(
        labels=['Смертельные', 'Несмертельные'],
        values=[death_count, non_death_count],
        hole=.3
    )])
    fig3.update_layout(title="Соотношение смертельных и несмертельных случаев")
    graph3 = opy.plot(fig3, auto_open=False, output_type='div')

    # 4. График + таблица: Распределение по организациям
    org_data = {}
    for acc in accidents:
        if acc.organization:
            org_name = acc.organization.name
            org_data[org_name] = org_data.get(org_name, 0) + 1

    # Сортируем по убыванию количества НС
    sorted_orgs = sorted(org_data.items(), key=lambda x: x[1], reverse=True)

    # График (столбчатая диаграмма)
    if sorted_orgs:
        org_names, org_values = zip(*sorted_orgs)
        fig4 = go.Figure(data=[go.Bar(
            x=org_names,
            y=org_values,
            marker_color='steelblue',
            text=org_values,
            textposition='auto'
        )])
        fig4.update_layout(
            title="Распределение НС по организациям (ОСТ)",
            xaxis_title="Организация",
            yaxis_title="Количество НС",
            xaxis=dict(tickangle=-45),
            margin=dict(b=120)  # Увеличенный нижний отступ для длинных названий
        )
    else:
        fig4 = go.Figure()
        fig4.update_layout(title="Нет данных по организациям")

    graph4 = opy.plot(fig4, auto_open=False, output_type='div')

    # Подготавливаем данные для таблицы
    table_data = [
        {'organization': name, 'count': count}
        for name, count in sorted_orgs
    ]

    context = {
        'graph1': graph1,
        'graph2': graph2,
        'graph3': graph3,
        'graph4': graph4,
        'table_data': table_data,  # Передаём данные таблицы в шаблон
        'total_accidents': accidents.count(),
        'total_victims': sum(acc.victims_count for acc in accidents),
        'death_rate': f"{(death_count / accidents.count() * 100):.1f}%" if accidents.count() > 0 else "0%"
    }
    return render(request, 'accident/statistics.html', context)
