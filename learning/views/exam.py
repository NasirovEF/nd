from django.core.exceptions import ValidationError
from django.views.generic import UpdateView, DeleteView
from learning.forms import BulkExamAssignmentForm, ExamAssignmentForm
from learning.models import ExamAssignment, ExamResult, Question, Learner, Answer, Exam
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
import json
import logging
from django.db import transaction, IntegrityError
from django.urls import reverse, reverse_lazy
from learning.services import get_current_date
from organization.models import Worker, Division
from django.http import HttpResponseNotFound, HttpResponseForbidden
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.paginator import Paginator
logger = logging.getLogger(__name__)


def assign_exam_to_learner(learner, exam, deadline=None, max_attempts=1):
    """Назначить экзамен работнику"""
    if ExamAssignment.objects.filter(learner=learner, exam=exam).exists():
        raise ValidationError("Экзамен уже назначен этому работнику.")

    assignment = ExamAssignment.objects.create(
        learner=learner,
        exam=exam,
        deadline=deadline,
        attempts_left=max_attempts
    )
    return assignment


def start_exam_attempt(assignment):
    """Начать попытку прохождения экзамена"""
    if assignment.attempts_left <= 0:
        raise ValidationError("Попытки исчерпаны.")
    if assignment.status == 'completed':
        raise ValidationError("Экзамен уже завершён.")

    attempt_number = assignment.total_attempts - assignment.attempts_left + 1

    assignment.status = 'in_progress'
    assignment.attempts_left -= 1
    assignment.save()

    result = ExamResult.objects.create(
        learner=assignment.learner,
        exam=assignment.exam,
        attempt_number=attempt_number
    )
    return result


def calculate_exam_result(result, user_answers):
    """
    Подсчитать результат экзамена.
    useranswers: список dict с ключами {'question_id', 'answer_ids'}
    """
    questions = result.exam.get_random_questions()
    total_score = 0
    earned_score = 0

    for item in user_answers:
        question = Question.objects.get(id=item['question_id'])
        correct_answers = question.answer.filter(is_correct=True)
        user_answer_ids = set(item['answer_ids'])
        correct_ids = set(correct_answers.values_list('id', flat=True))

        if user_answer_ids == correct_ids:
            earned_score += question.weight
        total_score += question.weight

    result.score = (earned_score / total_score) * 100 if total_score > 0 else 0
    result.total_score = total_score
    result.is_passed = result.score >= result.exam.passing_score
    result.answered_questions = user_answers  # сохраняем ответы для истории
    result.save()

    return result


def complete_exam_assignment(assignment, result):
    """Обновить статус назначения после завершения попытки"""

    if assignment.attempts_left > 0 and not result.is_passed:
        assignment.status = 'assigned'
    else:
        assignment.status = 'completed'
    assignment.save()
    return assignment


@login_required
def start_exam(request, learner_id, assignment_id):
    """Старт попытки прохождения экзамена"""
    try:
        learner = request.user.worker.learner.get(pk=learner_id)
    except Learner.DoesNotExist:
        return HttpResponseNotFound("Работник не найден")

    if request.user.worker != learner.worker:
        return HttpResponseForbidden("Доступ запрещён")

    assignment = get_object_or_404(ExamAssignment, learner=learner, id=assignment_id)

    if assignment.status == 'assigned':
        try:
            result = start_exam_attempt(assignment)
            return redirect('learning:take_exam', learner_id=learner.pk, result_id=result.id)
        except ValidationError as e:
            messages.error(request, str(e))

    return redirect('learning:my_exams')


@login_required
def take_exam(request, learner_id, result_id):
    """Экран прохождения экзамена"""

    try:
        learner = request.user.worker.learner.get(pk=learner_id)
    except Learner.DoesNotExist:
        return HttpResponseNotFound("Learner not found")

    result = get_object_or_404(
        ExamResult.objects.select_related('exam'),
        id=result_id,
        learner=learner
    )
    questions = result.exam.get_random_questions()

    return render(request, 'learning/take_exam.html', {
        'result': result,
        'questions': questions,
        'time_limit': result.exam.time_limit
    })


@csrf_protect
def submit_answers(request, learner_id, result_id):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request'})

    try:
        learner = Learner.objects.get(worker=request.user.worker, pk=learner_id)
        data = json.loads(request.body)
        user_answers = data.get('answers', [])

        result = ExamResult.objects.select_related('exam').get(
            id=result_id,
            learner=learner
        )

        exam_assignment = ExamAssignment.objects.get(
            exam=result.exam,
            learner=learner,
            status='in_progress'
        )
        with transaction.atomic():
            calculate_exam_result(result, user_answers)
            complete_exam_assignment(exam_assignment, result)

        return JsonResponse({
            'status': 'success',
            'score': round(result.score, 2),
            'is_passed': result.is_passed
        })

    except Learner.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Ученик не найден'})
    except ExamResult.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Экзамен не найден или завершён'})
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Некорректный JSON'})
    except ValidationError as e:
        return JsonResponse({'status': 'error', 'message': e.message})
    except Exception as e:
        logger.error(f"[submit_answers] Ошибка: {e}", exc_info=True)
        return JsonResponse({'status': 'error', 'message': 'Внутренняя ошибка сервера'})


@login_required
def exam_results(request, learner_id):
    """Просмотр результатов экзаменов для одного работника"""

    try:
        learner = Learner.objects.get(pk=learner_id)
    except Learner.DoesNotExist:
        return HttpResponseNotFound("Learner not found")
    results = ExamResult.objects.filter(learner=learner).select_related('exam')
    paginator = Paginator(results, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'learning/exam_results.html', {'page_obj': page_obj, 'learner': learner})


@login_required
@permission_required('learning.view_examresult', raise_exception=True)
def all_exam_results(request):
    """Просмотр результатов экзамена всех работников"""
    results = ExamResult.objects.all()
    content = {}

    content['search_params'] = {
        'division': request.GET.get('division', ''),
        'date_from': request.GET.get('date_from', ''),
        'date_to': request.GET.get('date_to', ''),
        'has_program': request.GET.get('has_program', ''),
        'has_briefing_program': request.GET.get('has_briefing_program', ''),
        'is_passed': request.GET.get('is_passed', ''),
        'is_not_passed': request.GET.get('is_not_passed', ''),
        'surname': request.GET.get('surname', ''),
        'name': request.GET.get('name', ''),
        'patronymic': request.GET.get('patronymic', ''),
    }
    divisions = Division.objects.all()
    content['divisions'] = divisions
    division = request.GET.get("division")
    date_from = request.GET.get("date_from")
    date_to = request.GET.get("date_to")
    has_program = request.GET.get("has_program")
    has_briefing_program = request.GET.get("has_briefing_program")
    is_passed = request.GET.get("is_passed")
    is_not_passed = request.GET.get("is_not_passed")
    surname = request.GET.get("surname")
    name = request.GET.get("name")
    patronymic = request.GET.get("patronymic")
    if division:
        results = results.filter(learner__worker__district__division__name__icontains=division)
    if date_from:
        results = results.filter(test_date__gte=date_from)
    if date_to:
        results = results.filter(test_date__lte=date_to)

    if has_program == "1" and has_briefing_program != "0":
        results = results.filter(exam__program__isnull=False)
    elif has_program != "1" and has_briefing_program == "0":
        results = results.filter(exam__briefing_program__isnull=False)
    elif has_program == "1" and has_briefing_program == "0":
        results = results.filter()

    if is_passed == "1" and is_not_passed != "0":
        results = results.filter(is_passed=True)
    elif is_passed != "1" and is_not_passed == "0":
        results = results.filter(is_passed=False)
    elif is_passed == "1" and is_not_passed == "0":
        results = results.filter()

    if surname:
        worker = Worker.objects.filter(surname__icontains=surname)
        learner = Learner.objects.filter(worker__in=worker)
        results = results.filter(learner__in=learner)
    if name:
        worker = Worker.objects.filter(name__icontains=name)
        learner = Learner.objects.filter(worker__in=worker)
        results = results.filter(learner__in=learner)
    if patronymic:
        worker = Worker.objects.filter(patronymic__icontains=patronymic)
        learner = Learner.objects.filter(worker__in=worker)
        results = results.filter(learner__in=learner)

    paginator = Paginator(results, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'learning/all_exam_results.html', {'page_obj': page_obj, 'content': content})


@login_required
def detail_exam_results(request, result_id):
    """Подробный результат экзамена"""
    try:
        result = ExamResult.objects.get(pk=result_id)
    except ExamResult.DoesNotExist:
        return HttpResponseNotFound("Ошибка, результат не найден")

    if (
            request.user.worker != result.learner.worker or
            not request.user.has_perm('learning.view_examresult') or
            not request.user.is_superuser
    ):
        return HttpResponseForbidden("У вас нет доступа к этому результату экзамена.")

    content_list = []

    if request.GET.get("all_results") == "1":
        all_results = True
    else:
        all_results = False

    if request.GET.get("all_assignments") == "1":
        all_assignments = True
    else:
        all_assignments = False

    if result.answered_questions:
        for answer in result.answered_questions:
            content = {}
            question_id = answer['question_id']
            selected_answer_id = answer['answer_ids'][0]  # Берём первый (и единственный) ID

            # Получаем вопрос
            try:
                question = Question.objects.get(pk=question_id)
                content['question_text'] = question.text
            except Question.DoesNotExist:
                content['question_text'] = "Вопрос не найден"

            # Получаем выбранный ответ пользователя
            try:
                selected_answer = Answer.objects.get(pk=selected_answer_id)
                content['user_answer_text'] = selected_answer.text
                content['is_user_answer_correct'] = selected_answer.is_correct
            except Answer.DoesNotExist:
                content['user_answer_text'] = "Ответ не найден"
                content['is_user_answer_correct'] = False

            # Получаем правильный ответ (всегда один)
            correct_answer = Answer.objects.filter(
                question=question,
                is_correct=True
            ).first()  # first() вернёт None, если нет правильного ответа

            content['correct_answer_text'] = (
                correct_answer.text if correct_answer else "Правильный ответ не указан"
            )

            content_list.append(content)

    return render(request, 'learning/detail_exam_result.html', {
        'content_list': content_list,
        'result': result,
        'all_results': all_results,
        'all_assignments': all_assignments}
                  )

@login_required
@permission_required('learning.view_examassignment', raise_exception=True)
def all_exam_assignment(request):
    assignments = ExamAssignment.objects.all()
    content = {}

    content['search_params'] = {
        'division': request.GET.get('division', ''),
        'date_from': request.GET.get('date_from', ''),
        'date_to': request.GET.get('date_to', ''),
        'has_program': request.GET.get('has_program', ''),
        'has_briefing_program': request.GET.get('has_briefing_program', ''),
        'status': request.GET.get('status', ''),
        'surname': request.GET.get('surname', ''),
        'name': request.GET.get('name', ''),
        'patronymic': request.GET.get('patronymic', ''),
    }
    divisions = Division.objects.all()
    content['divisions'] = divisions
    division = request.GET.get("division")
    date_from = request.GET.get("date_from")
    date_to = request.GET.get("date_to")
    has_program = request.GET.get("has_program")
    has_briefing_program = request.GET.get("has_briefing_program")
    status = request.GET.get("status")
    surname = request.GET.get("surname")
    name = request.GET.get("name")
    patronymic = request.GET.get("patronymic")
    if division:
        assignments = assignments.filter(learner__worker__district__division__name__icontains=division)
    if date_from:
        assignments = assignments.filter(assigned_date__gte=date_from)
    if date_to:
        assignments = assignments.filter(assigned_date__lte=date_to)

    if has_program == "1" and has_briefing_program != "0":
        assignments = assignments.filter(exam__program__isnull=False)
    elif has_program != "1" and has_briefing_program == "0":
        assignments = assignments.filter(exam__briefing_program__isnull=False)
    elif has_program == "1" and has_briefing_program == "0":
        assignments = assignments.filter()

    if status:
        assignments = assignments.filter(status=status)

    if surname:
        worker = Worker.objects.filter(surname__icontains=surname)
        learner = Learner.objects.filter(worker__in=worker)
        assignments = assignments.filter(learner__in=learner)
    if name:
        worker = Worker.objects.filter(name__icontains=name)
        learner = Learner.objects.filter(worker__in=worker)
        assignments = assignments.filter(learner__in=learner)
    if patronymic:
        worker = Worker.objects.filter(patronymic__icontains=patronymic)
        learner = Learner.objects.filter(worker__in=worker)
        assignments = assignments.filter(learner__in=learner)

    paginator = Paginator(assignments, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request,
                  'learning/all_exam_assignment.html',
                  {'page_obj': page_obj, 'content': content}
                  )


@login_required
@permission_required('learning.add_examassignment')
def create_bulk_exam_assignment(request):
    """Назначения экзамена работникам"""
    if request.method == 'POST':
        form = BulkExamAssignmentForm(request.POST)
        if form.is_valid():
            try:
                assignments = form.save()
                return redirect('learning:all_exam_assignment')
            except IntegrityError as e:
                cleaned_data = form.cleaned_data
                exam = cleaned_data['exam']
                learners = cleaned_data['learners']

                existing = []
                for learner in learners:
                    if ExamAssignment.objects.filter(
                            learner=learner,
                            exam=exam,
                            assigned_date=get_current_date()
                    ).exists():
                        existing.append(f"{learner}")

                if existing:
                    msg = (
                            "Не удалось назначить тест следующим работникам: "
                            + ", ".join(existing)
                            + ". У них уже есть это назначение."
                    )
                else:
                    msg = "Ошибка целостности данных. Возможно, дублируются записи."

                messages.error(request, msg)
        else:
            messages.error(request, "Ошибка при заполнении формы. Проверьте поля ниже.")
    else:
        form = BulkExamAssignmentForm()

    return render(request, 'learning/exam_assignment_form.html', {'form': form})


@login_required
@permission_required('learning.view_examresult')
def all_results_for_exam(request, exam_id, learner_id):
    results = ExamResult.objects.filter(exam__pk=exam_id, learner__pk=learner_id)
    learner = Learner.objects.filter(pk=learner_id).first()
    exam = Exam.objects.filter(pk=exam_id).first()
    return render(
        request,
        'learning/results_for_exam.html',
        {
            'results': results,
            'learner': learner,
            'exam': exam,
        }
    )


class ExamAssignmentUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """Редактирование назначенного экзамена работнику"""
    model = ExamAssignment
    form_class = ExamAssignmentForm
    permission_required = 'learning.change_examassignment'

    def get_success_url(self):
        return reverse("learning:all_exam_assignment")


class ExamAssignmentDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """Удаление назначенного экзамена работнику"""
    model = ExamAssignment
    permission_required = 'learning.delete_examassignment'
    success_url = reverse_lazy("learning:all_exam_assignment")
