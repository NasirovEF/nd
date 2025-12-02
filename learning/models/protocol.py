from django.db import models, transaction
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


class KnowledgeDateManager(models.Manager):
    @transaction.atomic
    def create_or_update_active(self, protocol=None, learner=None, direction=None, kn_date=None):
        if learner is None or direction is None:
            raise ValueError("learner и direction не могут быть None")

        # Блокируем записи для избежания гонок
        existing_records = self.filter(
            learner=learner,
            direction=direction
        ).select_for_update()

        # Создаём и сохраняем новую запись сразу
        new_record = self.model(
            protocol=protocol,
            learner=learner,
            direction=direction,
            kn_date=kn_date if kn_date is not None else get_current_date(),
            is_active=False,
            next_date=None
        )
        new_record.save()  # Сохраняем для генерации id

        # Теперь можно определить актуальную запись
        latest_record = max(
            list(existing_records) + [new_record],
            key=lambda x: (x.kn_date, x.id)
        )

        # Деактивируем все остальные
        self.filter(
            learner=learner,
            direction=direction
        ).exclude(id=latest_record.id).update(is_active=False)

        # Активируем актуальную
        if not latest_record.is_active:
            self.filter(id=latest_record.id).update(is_active=True)
            latest_record.is_active = True

        return latest_record


class KnowledgeDate(models.Model):
    """Класс даты проверки знаний"""
    kn_date = models.DateField(verbose_name="Дата проверки знаний", default=get_current_date)
    protocol = models.ForeignKey(Protocol, verbose_name="Протокол проверки", related_name="knowledge_date", on_delete=models.CASCADE, **NULLABLE)
    direction = models.ForeignKey("Direction", verbose_name="Направление обучения", related_name="knowledge_date", on_delete=models.SET_NULL, **NULLABLE)
    learner = models.ForeignKey("Learner", verbose_name="Работник", related_name="knowledge_date", on_delete=models.CASCADE,
                                  **NULLABLE)
    next_date = models.DateField(verbose_name="Дата следующей проверки знаний", default=get_current_date)
    is_active = models.BooleanField(default=True, verbose_name="Актуальность")

    objects = KnowledgeDateManager()

    def calculate_next_date(self):
        """Рассчитывает next_date после сохранения ProtocolResult."""
        try:
            if self.protocol:
                protocol_result = self.protocol.protocol_result.get(learner=self.learner)
                if protocol_result.passed:
                    self.next_date = self.kn_date + timedelta(days=self.direction.periodicity)
                else:
                    self.next_date = self.kn_date + timedelta(days=30)
            else:
                self.next_date = self.kn_date + timedelta(days=30)
        except (ProtocolResult.DoesNotExist, Protocol.DoesNotExist):
            self.next_date = self.kn_date + timedelta(days=30)

    def save(self, *args, **kwargs):
        self.calculate_next_date()
        return super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Дата проверки знаний"
        verbose_name_plural = "Даты проверки знаний"
        ordering = ["-kn_date"]

    def __str__(self):
        return f"{self.kn_date.strftime("%d.%m.%Y")} {self.learner}, направление обучения - {self.direction}"


class ProtocolResult(models.Model):
    protocol = models.ForeignKey(Protocol, on_delete=models.CASCADE, related_name="protocol_result", **NULLABLE)
    learner = models.ForeignKey("Learner", on_delete=models.CASCADE, related_name="protocol_result", **NULLABLE)
    passed = models.BooleanField(verbose_name='Сдал', default=True)
    comment = models.TextField(verbose_name='Комментарий', **NULLABLE)

    class Meta:
        unique_together = ('protocol', 'learner')
        verbose_name = "Результат проверки знаний"
        verbose_name_plural = "Результаты проверки знаний"
