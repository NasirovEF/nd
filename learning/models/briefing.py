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
    learner = models.ForeignKey(
        "Learner", on_delete=models.CASCADE,
        verbose_name="Инструктируемый",
        related_name="briefing_day"
    )
    briefing_type = models.ForeignKey(
        "Briefing",
        on_delete=models.SET_NULL,
        verbose_name="Вид инструктажа",
        null=True
    )
    briefing_day = models.DateField(verbose_name="Дата инструктажа", default=get_current_date)
    next_briefing_day = models.DateField(
        verbose_name="Дата следующего инструктажа",
        default=None,
        **NULLABLE
    )
    briefing_program = models.ForeignKey(
        "ProgramBriefing",
        on_delete=models.SET_NULL,
        verbose_name="Программа инструктажа или документ в объеме которого проведен инструктаж",
        related_name="briefing_day",
        null=True
    )
    briefing_reason = models.TextField(verbose_name="Причина проведения инструктажа", **NULLABLE)
    is_active = models.BooleanField(verbose_name="Актуальность", default=True)

    def calculate_next_date(self):
        if self.briefing_type.briefing_type == "repeated":
            self.next_briefing_day = self.briefing_day + timedelta(self.briefing_type.periodicity)
        else:
            return

    def save(self, *args, **kwargs):
        if not self.pk:
            if self.briefing_type and self.briefing_type.briefing_type == "repeated":
                BriefingDay.objects.filter(
                    learner=self.learner,
                    briefing_type__briefing_type__in=["primary", "repeated"],
                    is_active=True
                ).update(is_active=False)

        # Вычисляем next_briefing_day
        self.calculate_next_date()
        return super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Инструктаж"
        verbose_name_plural = "Инструктажи"

    def __str__(self):
        return f"{self.briefing_type} инструктаж от {self.briefing_day}"
