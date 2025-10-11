from django.db import models

from permit.services import NULLABLE


class Organization(models.Model):
    """Класс ОСТ"""

    name = models.CharField(max_length=150, verbose_name="Наименование ОСТ")

    class Meta:
        verbose_name = "ОСТ"
        verbose_name_plural = "ОСТы"

    def __str__(self):
        return self.name


class Branch(models.Model):
    """Класс филиала ОСТ"""

    name = models.CharField(max_length=150, verbose_name="Наименование филиала")
    name_ost = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        verbose_name="ОСТ",
        related_name="branch",
    )

    class Meta:
        verbose_name = "Филиал"
        verbose_name_plural = "Филиалы"

    def __str__(self):
        return self.name


class District(models.Model):
    """Класс участка"""

    name = models.CharField(max_length=150, verbose_name="Наименование участка")

    class Meta:
        verbose_name = "Участок"
        verbose_name_plural = "Участки"

    def __str__(self):
        return self.name


class Division(models.Model):
    """Класс структурного подразделения"""

    name = models.CharField(
        max_length=150, verbose_name="Наименование структурного подразделения"
    )
    district = models.ManyToManyField(
        District, verbose_name="Участок", related_name="division"
    )
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        verbose_name="ОСТ",
        related_name="devision",
    )
    branhc = models.ForeignKey(
        Branch, on_delete=models.CASCADE, verbose_name="филиал", related_name="division"
    )

    class Meta:
        verbose_name = "Структурное подразделение"
        verbose_name_plural = "Структурные подразделения"

    def __str__(self):
        return self.name


class Position(models.Model):
    """Класс должности/профессии"""

    name = models.CharField(
        max_length=150, verbose_name="Наименование должности (профессии)"
    )

    class Meta:
        verbose_name = "Должность"
        verbose_name_plural = "Должности"

    def __str__(self):
        return self.name

