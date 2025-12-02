from django.db import models
from datetime import date
from learning.services import add_doc_url
from organization.models import Position, Worker, Organization, Branch, Division, District, Group, StaffUnit
from organization.services import NULLABLE


class Direction(models.Model):
    """Модель направления обучения"""
    name = models.CharField(max_length=150, verbose_name="Направление обучения", unique=True)
    periodicity = models.PositiveIntegerField(verbose_name="Периодичность обучения")

    class Meta:
        verbose_name = "Направление обучения"
        verbose_name_plural = "Направления обучения"

    def __str__(self):
        return f"{self.name}"


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
    replacement = models.ForeignKey("self", on_delete=models.SET_NULL, verbose_name="Замена программы", related_name="program", **NULLABLE)
    is_active = models.BooleanField(verbose_name="Актуальность", default=True)
    doc_scan = models.FileField(verbose_name="Скан-копия программы обучения",
                                upload_to=add_doc_url, **NULLABLE)

    def save(self, *args, **kwargs):
        if self.replacement is None:
            self.is_active = True
        else:
            self.is_active = False

        return super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Программа обучения"
        verbose_name_plural = "Программы обучения"

    def __str__(self):
        return f"{self.name}"


class Learner(models.Model):
    """Модель обучаемого"""
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE, verbose_name="Работник", related_name="learner", **NULLABLE)
    position = models.OneToOneField(Position, on_delete=models.CASCADE, verbose_name="Должность/профессия", related_name="learner")
    direction = models.ManyToManyField(Direction, verbose_name="Направления обучения", related_name="learner")
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Обучаемый"
        verbose_name_plural = "Обучаемые"

    def __str__(self):
        return f"{self.position}, {self.worker}"


class StaffDirection(models.Model):
    """Модель минимальных наборов направлений обучения для профессий"""
    position = models.OneToOneField(StaffUnit, on_delete=models.CASCADE, verbose_name="", related_name="staff_direction")
    direction = models.ManyToManyField("Direction", verbose_name="Направление обучения", related_name="staff_direction")

    class Meta:
        verbose_name = "Набор направлений обучения для профессии"
        verbose_name_plural = "Наборы направлений обучения для профессий"

    def __str__(self):
        directions = []
        for direction in self.direction.all():
            directions.append(str(direction))
        str_directions = ", ".join(directions)
        return f"{self.position}, направления обучения: {str_directions}"

