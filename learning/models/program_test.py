from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator

from learning.models import Direction
from organization.services import NULLABLE


class Test(models.Model):
    """Тест для направления, поднаправления, программы инструктажа"""
    direction = models.ForeignKey(
        "Direction",
        on_delete=models.CASCADE,
        verbose_name="Направление",
        related_name="test",
        **NULLABLE
    )
    sub_direction = models.ForeignKey(
        "SubDirection",
        on_delete=models.CASCADE,
        verbose_name="Поднаправление",
        **NULLABLE,
        help_text="Оставьте пустым, если тест для всего направления",
        related_name="test"
    )
    briefing_program = models.OneToOneField(
        "ProgramBriefing",
        on_delete=models.CASCADE,
        verbose_name="Программа инструктажа",
        related_name="test",
        **NULLABLE
    )

    class Meta:
        verbose_name = "Тест"
        verbose_name_plural = "Тесты"
        constraints = [
            models.UniqueConstraint(
                fields=['direction', 'sub_direction', 'briefing_program'],
                name='unique_test_per_direction_or_subdirection'
            )
        ]

    def __str__(self):
        if self.direction:
            if self.sub_direction:
                return f"Тест к направлению обучения: ({self.direction.name} → {self.sub_direction.name})"
            return f"Тест к направлению обучения: ({self.direction.name})"
        elif self.briefing_program:
            return f"Тест к программе инструктажа: ({self.briefing_program.name})"

    def clean(self):
        # Проверка: если направление не имеет поднаправлений, sub_direction должно быть пустым
        if not self.direction.have_sub_direction and self.sub_direction:
            raise ValidationError({
                'sub_direction': "Это направление не поддерживает поднаправления."
            })
        # Если sub_direction задан, он должен относиться к этому направлению
        if self.sub_direction and self.sub_direction.direction != self.direction:
            raise ValidationError({
                'sub_direction': "Поднаправление не относится к выбранному направлению."
            })


class Question(models.Model):
    """Модель Вопроса к тесту"""
    test = models.ForeignKey("Test", on_delete=models.CASCADE, verbose_name="Вопрос", related_name="question")
    text = models.TextField(verbose_name="Текст вопроса")
    weight = models.PositiveIntegerField(verbose_name="Вес вопроса (баллы)", default=1)

    class Meta:
        verbose_name = "Вопрос"
        verbose_name_plural = "Вопросы"
        ordering = ['pk']

    def __str__(self):
        return f"{self.text}"


class Answer(models.Model):
    """Модель Ответа к Вопросу теста"""

    question = models.ForeignKey("Question", on_delete=models.CASCADE, verbose_name="Вопрос", related_name="answer")
    text = models.TextField(verbose_name="Текст ответа")
    is_correct = models.BooleanField(verbose_name="Правильный ответ", default=False)

    class Meta:
        verbose_name = "Ответ"
        verbose_name_plural = "Ответы"

    def __str__(self):
        return f"{self.text}"


class ExamResult(models.Model):
    """Результат прохождения экзамена"""
    learner = models.ForeignKey(
        "Learner",
        on_delete=models.CASCADE,
        verbose_name="Работник",
        related_name="exam_results"
    )
    exam = models.ForeignKey(
        "Exam",
        on_delete=models.CASCADE,
        verbose_name="Экзамен",
        related_name="results"
    )
    test_date = models.DateField(verbose_name="Дата тестирования", auto_now_add=True)
    is_passed = models.BooleanField(verbose_name="Сдан?", default=False)
    score = models.DecimalField(
        verbose_name="Набранный балл (%)",
        max_digits=5,
        decimal_places=2,
        default=0
    )
    total_score = models.PositiveIntegerField(verbose_name="Максимально возможный балл", default=0)
    attempt_number = models.PositiveIntegerField(verbose_name="Попытка №", default=1)
    answered_questions = models.JSONField(
        verbose_name="Ответы пользователя",
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = "Результат экзамена"
        verbose_name_plural = "Результаты экзаменов"
        unique_together = ('exam', 'learner', 'attempt_number')
        ordering = ['-test_date', '-id']


class ExamAssignment(models.Model):
    """Назначение экзамена работнику"""
    learner = models.ForeignKey(
        "Learner",
        on_delete=models.CASCADE,
        verbose_name="Работник",
        related_name="exam_assignments"
    )
    exam = models.ForeignKey(
        "Exam",
        on_delete=models.CASCADE,
        verbose_name="Экзамен",
        related_name="assignments"
    )
    assigned_date = models.DateField(verbose_name="Дата назначения", auto_now_add=True)
    deadline = models.DateField(verbose_name="Срок выполнения", null=True, blank=True)
    status = models.CharField(
        max_length=20,
        verbose_name="Статус",
        choices=[
            ('assigned', 'Назначен'),
            ('in_progress', 'В процессе'),
            ('completed', 'Завершён'),
            ('expired', 'Просрочен'),
        ],
        default='assigned'
    )
    total_attempts = models.PositiveIntegerField(verbose_name="Максимальное количество попыток", default=1)
    attempts_left = models.PositiveIntegerField(verbose_name="Осталось попыток", default=1)

    def clean(self):
        if self.attempts_left > self.total_attempts:
            raise ValidationError("Оставшееся количество попыток не может быть больше максимального количества попыток")

    class Meta:
        verbose_name = "Назначение экзамена"
        verbose_name_plural = "Назначения экзаменов"
        unique_together = ('learner', 'exam', 'assigned_date')
        ordering = ['-assigned_date', '-id']

    def __str__(self):
        return f"{self.learner} — {self.exam}"


class Exam(models.Model):
    """Экзамен, объединяющий тесты по программе"""
    program = models.ForeignKey(
        "Program",
        on_delete=models.CASCADE,
        verbose_name="Программа",
        related_name="exams",
        **NULLABLE
    )
    briefing_program = models.OneToOneField(
        "ProgramBriefing",
        on_delete=models.CASCADE,
        verbose_name="Программа инструктажа",
        related_name="exams",
        **NULLABLE
    )
    is_active = models.BooleanField(verbose_name="Активен", default=True)
    time_limit = models.PositiveIntegerField(
        verbose_name="Время на тест (мин)",
        default=20,
        **NULLABLE
    )
    passing_score = models.PositiveIntegerField(
        verbose_name="Проходной балл (%)",
        default=80,
        validators=[MinValueValidator(0)]
    )
    total_questions = models.PositiveIntegerField(
        verbose_name="Количество вопросов в тесте",
        default=20,
        validators=[MinValueValidator(1)]
    )

    class Meta:
        verbose_name = "Экзамен"
        verbose_name_plural = "Экзамены"

    def __str__(self):
        if self.program:
            return f"Экзамен к {self.program.name}"
        elif self.briefing_program:
            return f"Экзамен к {self.briefing_program.name}"

    def get_random_questions(self):
        """Возвращает N случайных вопросов из всех тестов программы"""
        if self.program:
            directions = Direction.objects.filter(program=self.program)

            # Базовые тесты (привязаны напрямую к направлениям)
            base_tests = Test.objects.filter(direction__in=directions)

            # Тесты из поднаправлений (только если есть направления с поднаправлениями)
            subdirection_tests = Test.objects.none()  # Пустой queryset по умолчанию

            directions_with_subs = directions.filter(have_sub_direction=True)
            if directions_with_subs.exists():
                subdirection_tests = Test.objects.filter(
                    sub_direction__direction__in=directions_with_subs
                )

            all_tests = base_tests | subdirection_tests

            questions = Question.objects.filter(test__in=all_tests)
        elif self.briefing_program:
            tests = Test.objects.filter(briefing_program=self.briefing_program)
            questions = Question.objects.filter(test__in=tests)

        return questions.order_by('?')[:self.total_questions]

    