from django.db import models

from learning.services import get_current_date
from organization.services import NULLABLE


class Test(models.Model):
    """Модель тестов"""
    program = models.OneToOneField("Program", verbose_name="Программа", related_name="test", on_delete=models.SET_NULL, **NULLABLE)
    is_active = models.BooleanField(verbose_name="Активен", default=True)
    time_limit = models.PositiveIntegerField(verbose_name="Время на тест (мин)", default=20, **NULLABLE)
    passing_score = models.PositiveIntegerField(verbose_name="Проходной балл (%)", default=90)

    class Meta:
        verbose_name = "Тест"
        verbose_name_plural = "Тесты"

    def __str__(self):
        if self.program:
            return f"Тест к {self.program.name}"
        else:
            return "Тест без программы"


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



