from django.core.exceptions import ValidationError
from learning.models import ExamAssignment, ExamResult, Question, Learner
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
import json
from django.http import HttpResponseNotFound
import logging
from django.db import transaction

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

    assignment.status = 'in_progress'
    assignment.attempts_left -= 1
    assignment.save()

    # Создаём запись о результате
    result = ExamResult.objects.create(
        learner=assignment.learner,
        exam=assignment.exam,
        attempt_number=assignment.attempts_left + 1
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
    assignment.status = 'completed' if result.is_passed else 'failed'
    assignment.save()
    return assignment


@login_required
def my_exams(request, learner_id):
    """Список назначенных экзаменов"""
    try:
        learner = request.user.worker.learner.get(pk=learner_id)
    except Learner.DoesNotExist:
        return HttpResponseNotFound("Learner not found")

    assignments = ExamAssignment.objects.filter(
        learner=learner,
        status__in=['assigned', 'in_progress']
    ).select_related('exam')
    return render(request, 'learning/my_exams.html', {'assignments': assignments})


@login_required
def start_exam(request, learner_id, assignment_id):
    """Старт попытки прохождения экзамена"""
    try:
        learner = request.user.worker.learner.get(pk=learner_id)
    except Learner.DoesNotExist:
        return HttpResponseNotFound("Learner not found")

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


@csrf_protect  # Вместо csrf_exempt
def submit_answers(request, learner_id, result_id):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request'})

    try:
        learner = Learner.objects.get(worker=request.user.worker, pk=learner_id)
        data = json.loads(request.body)
        user_answers = data.get('answers', [])

        # Проверка и получение результата
        result = ExamResult.objects.select_related('exam').get(
            id=result_id,
            learner=learner
        )

        # 2. Получаем ExamAssignment, связанный с этим экзаменом и учеником
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
    """Просмотр результатов экзаменов"""
    try:
        learner = request.user.worker.learner.get(pk=learner_id)
    except Learner.DoesNotExist:
        return HttpResponseNotFound("Learner not found")
    results = ExamResult.objects.filter(learner=learner).select_related('exam')
    return render(request, 'learning/exam_results.html', {'results': results})