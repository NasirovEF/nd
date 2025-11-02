from django.db import models
from datetime import date
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
    organization = models.ForeignKey(Organization, verbose_name="ОСТ", related_name="organization", on_delete=models.SET_NULL, **NULLABLE)
    branch = models.ForeignKey(Branch, verbose_name="Филиал", related_name="program", on_delete=models.SET_NULL, **NULLABLE)
    division = models.ForeignKey(Division, verbose_name="Структурное подразделение", related_name="program", on_delete=models.SET_NULL, **NULLABLE)
    district = models.ForeignKey(District, verbose_name="Участок", related_name="program", on_delete=models.SET_NULL, **NULLABLE)
    group = models.ForeignKey(Group, verbose_name="Группа", related_name="program", on_delete=models.SET_NULL, **NULLABLE)

    def add_program_url(self):
        """Функция создания пути для папки"""
        if not self.group or self.group is None:
            program_url = f"{self.organization}/{self.branch}/{self.division}/{self.district}"
        elif not self.district or self.district is None:
            program_url = f"{self.organization}/{self.branch}/{self.division}"
        elif not self.division or self.division is None:
            program_url = f"{self.organization}/{self.branch}"
        elif not self.branch or self.branch is None:
            program_url = f"{self.organization}"
        else:
            program_url = f"{self.organization}/{self.branch}/{self.division}/{self.district}/{self.group}"

        self.doc_scan = models.FileField (verbose_name="Скан.файл программы обучения", upload_to=f"learning/programs/{program_url}")
        return self.doc_scan

    class Meta:
        verbose_name = "Программа обучения"
        verbose_name_plural = "Программы обучения"

    def __str__(self):
        return self.name


class Learner(models.Model):
    """Модель обучаемого"""
    worker = models.OneToOneField(Worker, on_delete=models.SET_NULL, verbose_name="Работник", related_name="learner", **NULLABLE)
    direction = models.ManyToManyField(Direction, verbose_name="Направления обучения", related_name="learner")
    program = models.ManyToManyField(Program, verbose_name="Программа обучения", related_name="learner")

    def knowledge_date(self):
        """Функция создания даты проверки знаний"""
        knowledge_date = {}
        for kn_date in self.objects.direction:
            knowledge_date[str(kn_date)] = date.min
        return knowledge_date


class Protocol(models.Model):
    """Модель протокола проверки знаний"""
    date = models.DateField(verbose_name="Дата протокола проверки знаний")
    program = models.ManyToManyField(Program, verbose_name="Программа обучения", related_name="protocol")
    learner = models.ManyToManyField(Learner, verbose_name="Работники проходящие проверку знаний",  related_name="protocol")
    pass

