from django.db import models
from django.core.exceptions import ValidationError
from learning.services import get_current_date
from organization.services import NULLABLE


class Test(models.Model):
    """Тест для направления или поднаправления"""
    direction = models.ForeignKey(
        "Direction",
        on_delete=models.CASCADE,
        verbose_name="Направление",
        related_name="test"
    )
    sub_direction = models.ForeignKey(
        "SubDirection",
        on_delete=models.CASCADE,
        verbose_name="Поднаправление",
        **NULLABLE,
        help_text="Оставьте пустым, если тест для всего направления",
        related_name="test"
    )

    class Meta:
        verbose_name = "Тест"
        verbose_name_plural = "Тесты"
        constraints = [
            models.UniqueConstraint(
                fields=['direction', 'sub_direction'],
                name='unique_test_per_direction_or_subdirection'
            )
        ]

    def __str__(self):
        if self.sub_direction:
            return f"Тест к направлению обучения: ({self.direction.name} → {self.sub_direction.name})"
        return f"Тест к направлению обучения: ({self.direction.name})"

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


class TestResult(models.Model):
    """Модель результата теста"""
    learner = models.ForeignKey("Learner", verbose_name="Работник", on_delete=models.CASCADE, related_name="test_results")
    test = models.ForeignKey("Test", verbose_name="Тест", on_delete=models.CASCADE, related_name="results")
    test_date = models.DateTimeField(verbose_name="Дата тестирования", auto_now_add=True)
    is_passed = models.BooleanField(verbose_name="Сдан?", default=False)
    score = models.DecimalField(verbose_name="Набранный балл (%)", max_digits=5, decimal_places=2, default=0)
    total_score = models.PositiveIntegerField(verbose_name="Максимально возможный балл", default=0)

    attempt_number = models.PositiveIntegerField(verbose_name="Попытка №", default=1)

    class Meta:
        unique_together = ('test', 'learner', 'attempt_number')
        verbose_name = "Результат теста"
        verbose_name_plural = "Результаты тестирования"


class TestAssignment(models.Model):
    """Модель процесса назначения теста"""
    learner = models.ForeignKey("Learner", verbose_name="Работник", on_delete=models.CASCADE, related_name="assigned_tests")
    test = models.ForeignKey("Test", verbose_name="Тест", on_delete=models.CASCADE, related_name="assignments")
    assigned_date = models.DateTimeField(verbose_name="Дата назначения", auto_now_add=True)
    deadline = models.DateTimeField(verbose_name="Срок выполнения", null=True, blank=True)
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
    attempts_left = models.PositiveIntegerField(verbose_name="Осталось попыток", default=1)

    class Meta:
        verbose_name = "Назначение теста"
        verbose_name_plural = "Назначения тестов"



