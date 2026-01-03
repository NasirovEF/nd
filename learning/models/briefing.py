from django.db import models
from learning.models import BaseProgram
from learning.services import get_current_date
from organization.services import NULLABLE
from datetime import timedelta


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
        return f"{self.get_briefing_type_display()}"


class ProgramBriefing(BaseProgram):
    """Модель программы инструктажа"""
    briefing = models.ManyToManyField("Briefing", verbose_name="Тип инструктажа", related_name="briefing_program")

    class Meta:
        verbose_name = "Программа инструктажа"
        verbose_name_plural = "Программы инструктажей"


class BriefingDay(models.Model):
    """Модель дня проведения инструктажа"""
    learner = models.ForeignKey("Learner", on_delete=models.CASCADE, verbose_name="Инструктируемый", related_name="briefing_day")
    briefing_type = models.ForeignKey("Briefing", on_delete=models.SET_NULL, verbose_name="Вид инструктажа", **NULLABLE)
    briefing_day = models.DateField(verbose_name="Дата инструктажа", default=get_current_date)
    next_briefing_day = models.DateField(verbose_name="Дата следующего инструктажа", default=get_current_date)
    briefing_reason = models.TextField(verbose_name="Причина проведения инструктажа", **NULLABLE)
    is_active = models.BooleanField(verbose_name="Актуальность", default=True)

    def calculate_next_date(self):
        if self.briefing_type.briefing_type in ["primary", "repeated"]:
            self.next_briefing_day = self.briefing_day + timedelta(self.briefing_type.periodicity)

    def save(self, *args, **kwargs):
        self.calculate_next_date()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.briefing_type} инструктаж от {self.briefing_day}"
