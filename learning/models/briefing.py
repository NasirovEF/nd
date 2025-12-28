from django.db import models
from learning.models import BaseProgram


class Briefing(models.Model):
    """Модель инструктажа"""
    briefing_type = models.CharField(max_length=20, verbose_name="Вид инструктажа", choices=[
            ('introductory', 'Вводный'),
            ('primary', 'Первичный'),
            ('repeated', 'Повторный'),
            ('unscheduled', 'Внеплановый'),
            ('purposeful', 'Целевой'),
        ])
    periodicity = models.PositiveIntegerField(verbose_name="Периодичность проведения в днях", default=0)

    class Meta:
        verbose_name = "Вид инструктажа"
        verbose_name_plural = "Виды инструктажей"

    def __str__(self):
        return f"{self.briefing_type}"


class ProgramBriefing(BaseProgram):
    """Модель программы инструктажа"""
    briefing = models.ManyToManyField("Briefing", verbose_name="Тип инструктажа", related_name="briefing_program")

    class Meta:
        verbose_name = "Программа обучения"
        verbose_name_plural = "Программы обучения"
