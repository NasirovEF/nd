from django.core.exceptions import ValidationError
from learning.models import ExamAssignment, ExamResult, Question
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib import messages
import json


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
        correct_answers = question.answers.filter(is_correct=True)
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
def my_exams(request):
    """Список назначенных экзаменов"""
    assignments = ExamAssignment.objects.filter(
        learner=request.user,
        status__in=['assigned', 'in_progress']
    ).select_related('exam')
    return render(request, 'exams/my_exams.html', {'assignments': assignments})


@login_required
def start_exam(request, assignment_id):
    """Старт попытки прохождения экзамена"""
    assignment = get_object_or_404(ExamAssignment, id=assignment_id, learner=request.user)

    if assignment.status == 'assigned':
        try:
            result = start_exam_attempt(assignment)
            return redirect('take_exam', result_id=result.id)
        except ValidationError as e:
            messages.error(request, str(e))

    return redirect('my_exams')


@login_required
def take_exam(request, result_id):
    """Экран прохождения экзамена"""
    result = get_object_or_404(
        ExamResult.objects.select_related('exam'),
        id=result_id,
        learner=request.user
    )
    questions = result.exam.get_random_questions()

    return render(request, 'exams/take_exam.html', {
        'result': result,
        'questions': questions,
        'time_limit': result.exam.time_limit
    })


@method_decorator(csrf_exempt, name='dispatch')
def submit_answers(request, result_id):
    """Обработка отправленных ответов"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_answers = data.get('answers', [])

            result = ExamResult.objects.get(id=result_id, learner=request.user)
            calculate_exam_result(result, user_answers)
            complete_exam_assignment(result.exam_assignment, result)

            return JsonResponse({
                'status': 'success',
                'score': round(result.score, 2),
                'is_passed': result.is_passed
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'Invalid request'})


@login_required
def exam_results(request):
    """Просмотр результатов экзаменов"""
    results = ExamResult.objects.filter(learner=request.user).select_related('exam')
    return render(request, 'exams/exam_results.html', {'results': results})