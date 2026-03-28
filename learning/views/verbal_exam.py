from django.views.generic import CreateView, UpdateView, ListView, DeleteView, DetailView
from django.urls import reverse, reverse_lazy
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.contrib.auth.decorators import login_required, permission_required
from learning.forms import BulkVerbalExamForm, VerbalExamForm
from learning.models.program_test import VerbalExam
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db import transaction, IntegrityError
from django.http import HttpResponseForbidden


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
            'exam_date_from': self.request.GET.get('exam_date_from', ''),
            'exam_date_to': self.request.GET.get('exam_date_to', ''),
            'affiliation': self.request.GET.get('affiliation', ''),
        }
        return context

    def get_queryset(self, *args, **kwargs):
        queryset = super().get_queryset(*args, **kwargs)
        status = self.request.GET.get("status")
        learner = self.request.GET.get("learner")
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
        if exam_date_from:
            queryset = queryset.filter(exam_date__gte=exam_date_from)
        if exam_date_to:
            queryset = queryset.filter(exam_date__lte=exam_date_to)
        if affiliation:
            queryset = queryset.filter(Q(organization__name__icontains=affiliation) |
                                       Q(branch__name__icontains=affiliation) |
                                       Q(division__name__icontains=affiliation) |
                                       Q(district__name__icontains=affiliation) |
                                       Q(group__name__icontains=affiliation)
                                       )

        return queryset


@login_required
@permission_required('learning.add_verbalexam')
def create_bulk_verbalexam(request):
    """Назначения экзамена работникам"""
    if request.method == 'POST':
        form = BulkVerbalExamForm(request.POST)
        if form.is_valid():
            try:
                verbal_exams = form.save()
                return redirect('learning:verbalexam_list')
            except IntegrityError as e:
                msg = "Ошибка целостности данных. Возможно, дублируются записи."

                messages.error(request, msg)
        else:
            messages.error(request, "Ошибка при заполнении формы. Проверьте поля ниже.")
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
    permission_required = 'learning.change_verbalexam'
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