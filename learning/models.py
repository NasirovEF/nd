from django.db import models
from datetime import date, timedelta
from learning.services import add_doc_url
from organization.models import Position, Worker, Organization, Branch, Division, District, Group
from organization.services import NULLABLE


class Direction(models.Model):
    """Модель направления обучения"""
    name = models.CharField(max_length=150, verbose_name="Направление обучения", unique=True)
    periodicity = models.PositiveIntegerField(verbose_name="Периодичность обучения")

    class Meta:
        verbose_name = "Направление обучения"
        verbose_name_plural = "Направления обучения"

    def __str__(self):
        return self.name


class Program(models.Model):
    """Модель программы обучения"""
    name = models.CharField(max_length=150, verbose_name="Наименование программы обучения")
    direction = models.ManyToManyField(Direction, related_name="program", verbose_name="Направление обучения")
    duration = models.PositiveIntegerField(verbose_name="Продолжительность обучения (часов)")
    position = models.ForeignKey(Position, on_delete=models.SET_NULL, related_name="program", verbose_name="Наименование профессии", **NULLABLE)
    approve = models.CharField(max_length=150, verbose_name="Программа утверждена", help_text="Введите должность, И.О. Фамилию лица утвердившего программу")
    approval_date = models.DateField(verbose_name="Дата утверждения программы", default=date.today, help_text="Введите дату в формате ДД.ММ.ГГ")
    organization = models.ForeignKey(Organization, verbose_name="ОСТ", related_name="organization", on_delete=models.SET_NULL, **NULLABLE)
    branch = models.ForeignKey(Branch, verbose_name="Филиал", related_name="program", on_delete=models.SET_NULL, **NULLABLE)
    division = models.ForeignKey(Division, verbose_name="Структурное подразделение", related_name="program", on_delete=models.SET_NULL, **NULLABLE)
    district = models.ForeignKey(District, verbose_name="Участок", related_name="program", on_delete=models.SET_NULL, **NULLABLE)
    group = models.ForeignKey(Group, verbose_name="Группа", related_name="program", on_delete=models.SET_NULL, **NULLABLE)
    doc_scan = models.FileField(verbose_name="Скан-копия программы обучения",
                                upload_to=add_doc_url, **NULLABLE)

    class Meta:
        verbose_name = "Программа обучения"
        verbose_name_plural = "Программы обучения"

    def __str__(self):
        return self.name


class Learner(models.Model):
    """Модель обучаемого"""
    worker = models.OneToOneField(Worker, on_delete=models.CASCADE, verbose_name="Работник", related_name="learner", **NULLABLE)
    direction = models.ManyToManyField(Direction, verbose_name="Направления обучения", related_name="learner")

    class Meta:
        verbose_name = "Обучаемый"
        verbose_name_plural = "Обучаемые"

    def __str__(self):
        return self.worker.__str__()


class Protocol(models.Model):
    """Модель протокола проверки знаний"""
    chairman = models.ForeignKey(Worker, on_delete=models.SET_NULL, verbose_name="Председатель комиссии", related_name="protocol_chairman", null=True,)
    members = models.ManyToManyField(Worker, verbose_name="Члены комиссии", related_name="protocol_members")
    prot_date = models.DateField(verbose_name="Дата протокола проверки знаний", default=date.today())
    program = models.ManyToManyField(Program, verbose_name="Программа обучения", related_name="protocol")
    learner = models.ManyToManyField(Learner, verbose_name="Работники проходящие проверку знаний",  related_name="protocol")
    direction = models.ManyToManyField(Direction, related_name="protocol", verbose_name="Направление обучения")
    doc_scan = models.FileField(verbose_name="Скан-копия протокола проверки знаний",
                                upload_to=add_doc_url, **NULLABLE)

    class Meta:
        verbose_name = "Протокол проверки знаний"
        verbose_name_plural = "Протоколы проверки знаний"
        ordering = ["-prot_date"]

    def __str__(self):
        return f"Протокол проверки знаний от {self.prot_date.strftime("%d.%m.%Y")}"


class KnowledgeDate(models.Model):
    """Класс даты проверки знаний"""
    kn_date = models.DateField(verbose_name="Дата проверки знаний", default=date.today())
    protocol = models.ForeignKey(Protocol, verbose_name="Протокол проверки", related_name="knowledge_date", on_delete=models.CASCADE, **NULLABLE)
    direction = models.ForeignKey(Direction, verbose_name="Направление обучения", related_name="knowledge_date", on_delete=models.SET_NULL, **NULLABLE)
    learner = models.ForeignKey(Learner, verbose_name="Работник", related_name="knowledge_date", on_delete=models.CASCADE,
                                  **NULLABLE)
    next_date = models.DateField(verbose_name="Дата следующей проверки знаний", default=date.today())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.protocol.protocol_result.get(learner=self.learner):
            self.next_date = self.kn_date + timedelta(days=self.direction.periodicity)
        else:
            self.next_date = self.kn_date + timedelta(days=30)

    class Meta:
        verbose_name = "Дата проверки знаний"
        verbose_name_plural = "Даты проверки знаний"
        ordering = ["-kn_date"]

    def __str__(self):
        return self.date.strftime("%d.%m.%Y")


class ProtocolResult(models.Model):
    protocol = models.ForeignKey(Protocol, on_delete=models.CASCADE, related_name="protocol_result")
    learner = models.ForeignKey(Learner, on_delete=models.CASCADE, related_name="protocol_result")
    passed = models.BooleanField(verbose_name='Сдал', default=True)
    comment = models.TextField(verbose_name='Комментарий', **NULLABLE)

    class Meta:
        unique_together = ('protocol', 'learner')