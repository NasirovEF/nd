from django.db import models
from django.core.exceptions import ValidationError
from organization.models import Organization, Branch, Division, District, Group
from organization.services import NULLABLE


class StaffUnit(models.Model):
    """Класс штатной единицы"""

    name = models.CharField(
        max_length=150, verbose_name="Сокращенное наименование должности (профессии)", unique=True
    )
    full_name = models.CharField(
        max_length=150, verbose_name="Полное наименование должности (профессии)", unique=True
    )
    position_group = models.ManyToManyField("PositionGroup", verbose_name="Группа работников", related_name="staffunit")

    class Meta:
        verbose_name = "Штатная единица"
        verbose_name_plural = "Штатные единицы"

    def __str__(self):
        return f'{self.name}'


class PositionGroup(models.Model):
    """Класс группы работников"""
    name = models.CharField(
        max_length=100, verbose_name="Наименование группы"
    )

    class Meta:
        verbose_name = "Группа должностей"
        verbose_name_plural = "Группы должностей"

    def __str__(self):
        return f'{self.name}'


class Position(models.Model):
    """Класс профессии/должности"""
    name = models.ForeignKey(StaffUnit, on_delete=models.CASCADE, verbose_name="Профессия/должность", related_name="position", null=True)
    worker = models.ForeignKey("Worker", on_delete=models.CASCADE, verbose_name="", related_name="position", null=True)
    is_main = models.BooleanField(verbose_name="Основная профессия", default=False)

    class Meta:
        verbose_name = "Профессия/должность"
        verbose_name_plural = "Профессии/должности"
        ordering = ["is_main"]

    def __str__(self):
        return f'{self.name}'


class Worker(models.Model):
    """Класс работника"""

    surname = models.CharField(max_length=50, verbose_name="Фамилия")
    name = models.CharField(max_length=50, verbose_name="Имя")
    patronymic = models.CharField(max_length=50, verbose_name="Отчество", **NULLABLE)
    image = models.ImageField(upload_to="organization/worker/", verbose_name="Фотография работника",  **NULLABLE)
    service_number = models.CharField(max_length=30, verbose_name="Табельный номер", unique=True)
    dismissed = models.BooleanField(verbose_name="Уволен", default=False)

    district = models.ForeignKey(
        District,
        on_delete=models.SET_NULL,
        **NULLABLE,
        verbose_name="Участок",
        related_name="worker"
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        **NULLABLE,
        verbose_name="Группа участка",
        related_name="worker"
    )

    @property
    def organization(self):
        return self.district.division.branch.organization if self.district else None

    @property
    def branch(self):
        return self.district.division.branch if self.district else None

    @property
    def division(self):
        return self.district.division if self.district else None

    class Meta:
        verbose_name = "Работник"
        verbose_name_plural = "Работники"

    def __str__(self):
        return f'{self.name[:1]}.{self.patronymic[:1]}. {self.surname}'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if hasattr(self, 'user'):
            if self.dismissed:
                self.user.is_active = False
                self.user.save(update_fields=['is_active'])
            else:
                self.user.is_active = True
                self.user.save(update_fields=['is_active'])
