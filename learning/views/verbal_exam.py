from django.views.generic import CreateView, UpdateView, ListView, DeleteView, DetailView
from django.urls import reverse, reverse_lazy
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.contrib.auth.decorators import login_required, permission_required
from learning.forms import BulkVerbalExamForm, VerbalExamForm
from learning.models.program_test import VerbalExam, ExamResult
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db import transaction, IntegrityError
from django.http import HttpResponseForbidden
from urllib.parse import urlencode


class VerbalExamListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    """Просмотр списка устных экзаменов"""

    model = VerbalExam
    permission_required = 'learning.view_verbalexam'
    paginate_by = 20

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['search_params'] = {
            'status': self.request.GET.get('status', ''),
            'learner': self.request.GET.get('learner', ''),
            'position': self.request.GET.get('position', ''),
            'exam_date_from': self.request.GET.get('exam_date_from', ''),
            'exam_date_to': self.request.GET.get('exam_date_to', ''),
            'affiliation': self.request.GET.get('affiliation', ''),
        }
        return context

    def get_queryset(self, *args, **kwargs):
        queryset = super().get_queryset(*args, **kwargs)
        status = self.request.GET.get("status")
        learner = self.request.GET.get("learner")
        position = self.request.GET.get("position")
        exam_date_from = self.request.GET.get("exam_date_from")
        exam_date_to = self.request.GET.get("exam_date_to")
        affiliation = self.request.GET.get("affiliation")

        if status:
            queryset = queryset.filter(status=status)
        if learner:
            queryset = queryset.filter(Q(learner__worker__name__icontains=learner) |
                                       Q(learner__worker__surname__icontains=learner) |
                                       Q(learner__worker__patronymic__icontains=learner)
                                       )
        if position:
            queryset = queryset.filter(learner__position__name__full_name__icontains=position)
        if exam_date_from:
            queryset = queryset.filter(exam_date__gte=exam_date_from)
        if exam_date_to:
            queryset = queryset.filter(exam_date__lte=exam_date_to)
        if affiliation:
            queryset = queryset.filter(Q(learner__worker__organization__name__icontains=affiliation) |
                                       Q(learner__worker__branch__name__icontains=affiliation) |
                                       Q(learner__worker__division__name__icontains=affiliation) |
                                       Q(learner__worker__district__name__icontains=affiliation) |
                                       Q(learner__worker__group__name__icontains=affiliation)
                                       )

        return queryset


@login_required
@permission_required('learning.add_verbalexam')
def create_bulk_verbalexam(request):
    """Назначения экзамена работникам"""
    if request.method == 'POST':
        form = BulkVerbalExamForm(request.POST)
        if form.is_valid():
            results = form.save()

            # Показываем сообщения пользователю
            if results['created']:
                messages.success(request, f"Создано экзаменов: {len(results['created'])}")
            if results['skipped']:
                skipped_names = [learner.get_full_name() for learner in results['skipped']]
                messages.warning(request, f"Пропущено (дубликаты): {', '.join(skipped_names)}")
            if results['errors']:
                messages.error(request, "Ошибки при создании некоторых экзаменов")

            return redirect('learning:verbalexam_list')
    else:
        form = BulkVerbalExamForm()

    return render(request, 'learning/bulk_verbalexam_form.html', {'form': form})


class VerbalExamUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """Редактирование устного экзамена"""

    model = VerbalExam
    form_class = VerbalExamForm
    permission_required = 'learning.change_verbalexam'

    def get_success_url(self):
        return reverse('learning:verbalexam_list')


class VerbalExamDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """Редактирование устного экзамена"""

    model = VerbalExam
    permission_required = 'learning.delete_verbalexam'
    success_url = reverse_lazy('learning:verbalexam_list')


class VerbalExamDetailView(LoginRequiredMixin, DetailView):
    """Экран просмотра вопросов экзаменуемым"""

    model = VerbalExam

    def dispatch(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
        except self.model.DoesNotExist:
            return HttpResponseForbidden("Экзамен не найден.")

        if request.user.worker != self.object.learner.worker:
            return HttpResponseForbidden("У вас нет доступа к экзамену.")

        if self.object.status != "in_progress":
            self.object.status = "in_progress"
            self.object.save(update_fields=['status'])

        return super().dispatch(request, *args, **kwargs)


def toggle_exam_status(request, pk):
    exam = get_object_or_404(VerbalExam, id=pk)
    exam.is_active = not exam.is_active
    exam.save()

    # Берём параметры из POST (они переданы через скрытые поля)
    status = request.POST.get('status')
    learner = request.POST.get('learner')
    position = request.POST.get('position')
    exam_date_from = request.POST.get('exam_date_from')
    exam_date_to = request.POST.get('exam_date_to')
    affiliation = request.POST.get('affiliation')

    # Формируем URL с параметрами
    base_url = reverse('learning:verbalexam_list')
    params = {}
    if status:
        params['status'] = status
    if learner:
        params['learner'] = learner
    if position:
        params['position'] = position
    if exam_date_from:
        params['exam_date_from'] = exam_date_from
    if exam_date_to:
        params['exam_date_to'] = exam_date_to
    if affiliation:
        params['affiliation'] = affiliation

    if params:
        query_string = urlencode(params)
        redirect_url = f"{base_url}?{query_string}"
    else:
        redirect_url = base_url

    return redirect(redirect_url)


def complete_exam_status(request, pk):
    exam = get_object_or_404(VerbalExam, id=pk)
    exam.status = 'completed'
    exam.save(update_fields=['status'])
    return redirect('organization:worker_detail', pk=exam.learner.worker.pk)


@login_required
@permission_required('learning.change_verbalexam')
def create_verbalexam_result(request, pk, score):
    """Создание результата экзамена"""
    exam = get_object_or_404(VerbalExam, id=pk)

    if score not in ["1", "0"]:
        return redirect('learning:verbalexam_list')

    exam.status = 'completed'
    exam.is_active = False
    exam.save(update_fields=['status', 'is_active'])
    is_passed = (score == "1")
    try:
        result = ExamResult.objects.get(
            verbal_exam=exam,
            learner=exam.learner
        )
        result.is_passed = is_passed
        result.save(update_fields=['is_passed'])
    except ExamResult.DoesNotExist:
        result = ExamResult.objects.create(
            verbal_exam=exam,
            learner=exam.learner,
            is_passed=is_passed
        )
    status = request.POST.get('status', '')
    learner = request.POST.get('learner', '')
    position = request.POST.get('position', '')
    exam_date_from = request.POST.get('exam_date_from', '')
    exam_date_to = request.POST.get('exam_date_to', '')
    affiliation = request.POST.get('affiliation', '')

    base_url = reverse('learning:verbalexam_list')
    params = {}

    if status:
        params['status'] = status
    if learner:
        params['learner'] = learner
    if position:
        params['position'] = position
    if exam_date_from:
        params['exam_date_from'] = exam_date_from
    if exam_date_to:
        params['exam_date_to'] = exam_date_to
    if affiliation:
        params['affiliation'] = affiliation

    if params:
        query_string = urlencode(params)
        redirect_url = f"{base_url}?{query_string}"
    else:
        redirect_url = base_url

    return redirect(redirect_url)

