from django.db import models
from datetime import timedelta
from learning.services import add_prot_url, get_current_date
from organization.models import Worker, Division
from organization.services import NULLABLE


class Protocol(models.Model):
    """Модель протокола проверки знаний"""
    division = models.ForeignKey(Division, on_delete=models.SET_NULL, verbose_name="Структурное подразделение выдавшее протокол", related_name="protocol", null=True)
    chairman = models.ForeignKey(Worker, on_delete=models.SET_NULL, verbose_name="Председатель комиссии", related_name="protocol_chairman", null=True)
    members = models.ManyToManyField(Worker, verbose_name="Члены комиссии", related_name="protocol_members")
    prot_date = models.DateField(verbose_name="Дата протокола проверки знаний", default=get_current_date)
    program = models.ManyToManyField("Program", verbose_name="Программа обучения", related_name="protocol")
    learner = models.ManyToManyField("Learner", verbose_name="Работники проходящие проверку знаний",  related_name="protocol")
    direction = models.ManyToManyField("Direction", related_name="protocol", verbose_name="Направление обучения")
    doc_scan = models.FileField(verbose_name="Скан-копия протокола проверки знаний",
                                upload_to=add_prot_url, **NULLABLE)

    class Meta:
        verbose_name = "Протокол проверки знаний"
        verbose_name_plural = "Протоколы проверки знаний"
        ordering = ["-prot_date", "-id"]

    def __str__(self):
        return f"Протокол проверки знаний от {self.prot_date.strftime("%d.%m.%Y")}"


class KnowledgeDate(models.Model):
    """Класс даты проверки знаний"""
    kn_date = models.DateField(verbose_name="Дата проверки знаний", default=get_current_date)
    protocol = models.ForeignKey(Protocol, verbose_name="Протокол проверки", related_name="knowledge_date", on_delete=models.CASCADE, **NULLABLE)
    direction = models.ForeignKey("Direction", verbose_name="Направление обучения", related_name="knowledge_date", on_delete=models.SET_NULL, **NULLABLE)
    learner = models.ForeignKey("Learner", verbose_name="Работник", related_name="knowledge_date", on_delete=models.CASCADE,
                                  **NULLABLE)
    next_date = models.DateField(verbose_name="Дата следующей проверки знаний", default=get_current_date)

    def calculate_next_date(self):
        """Рассчитывает next_date после сохранения ProtocolResult."""
        try:
            protocol_result = self.protocol.protocol_result.get(learner=self.learner)
            if protocol_result.passed:
                self.next_date = self.kn_date + timedelta(days=self.direction.periodicity)
            else:
                self.next_date = self.kn_date + timedelta(days=30)
        except ProtocolResult.DoesNotExist:
            pass

    def save(self, *args, **kwargs):
        self.calculate_next_date()
        return super().save(*args, **kwargs)


    class Meta:
        verbose_name = "Дата проверки знаний"
        verbose_name_plural = "Даты проверки знаний"
        ordering = ["-kn_date"]

    def __str__(self):
        return f"{self.kn_date.strftime("%d.%m.%Y")}"


class ProtocolResult(models.Model):
    protocol = models.ForeignKey(Protocol, on_delete=models.CASCADE, related_name="protocol_result", **NULLABLE)
    learner = models.ForeignKey("Learner", on_delete=models.CASCADE, related_name="protocol_result", **NULLABLE)
    passed = models.BooleanField(verbose_name='Сдал', default=True)
    comment = models.TextField(verbose_name='Комментарий', **NULLABLE)

    class Meta:
        unique_together = ('protocol', 'learner')
        verbose_name = "Результат проверки знаний"
        verbose_name_plural = "Результаты проверки знаний"
