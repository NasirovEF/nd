from django.db import models

from learning.services import get_current_date
from organization.services import NULLABLE


class Test(models.Model):
    """Модель тестов"""
    program = models.ManyToManyField("Program", verbose_name="Программа", related_name="test")

    class Meta:
        verbose_name = "Тест"
        verbose_name_plural = "Тесты"

    def __str__(self):
        return f"Тест к {self.program.name}"


class Question(models.Model):
    """Модель Вопроса к тесту"""

    test = models.ForeignKey("Test", on_delete=models.CASCADE, verbose_name="Вопрос", related_name="question")
    text = models.TextField(verbose_name="Текст вопроса")

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
    learner = models.ForeignKey("Learner", verbose_name="Работник", on_delete=models.CASCADE, related_name="test_result")
    test = models.ForeignKey("Test", verbose_name="Тест", on_delete=models.CASCADE, related_name="test_result")
    test_date = models.DateTimeField(verbose_name="Дата тестирования", auto_now_add=True)
    is_passed = models.BooleanField(verbose_name="Сдан?", default=False)

    class Meta:
        unique_together = ('test', 'learner')
        verbose_name = "Результат теста"
        verbose_name_plural = "Результаты тестирования"
