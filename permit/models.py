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


class Group(models.Model):
    """Класс группы участка"""

    name = models.CharField(max_length=150, verbose_name="Наименование группы")

    class Meta:
        verbose_name = "Группа"
        verbose_name_plural = "Группа"


class District(models.Model):
    """Класс участка"""

    name = models.CharField(max_length=150, verbose_name="Наименование участка")
    group = models.ManyToManyField(
        Group, verbose_name="группа участка", related_name="district"
    )

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
    branch = models.ForeignKey(
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


class Worker(models.Model):
    """Класс работника"""

    surname = models.CharField(max_length=50, verbose_name="Фамилия")
    name = models.CharField(max_length=50, verbose_name="Имя")
    patronymic = models.CharField(max_length=50, verbose_name="Отчество", **NULLABLE)

    organization = models.ForeignKey(
        Organization,
        on_delete=models.SET_NULL,
        **NULLABLE,
        verbose_name="ОСТ",
        related_name="worker"
    )
    branch = models.ForeignKey(
        Branch,
        on_delete=models.SET_NULL,
        **NULLABLE,
        verbose_name="Филиал",
        related_name="worker"
    )
    division = models.ForeignKey(
        Division,
        on_delete=models.SET_NULL,
        **NULLABLE,
        verbose_name="Структурное подразделение",
        related_name="worker"
    )
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
    main_position = models.ForeignKey(
        Position,
        on_delete=models.SET_NULL,
        **NULLABLE,
        verbose_name="Основная должность/профессия",
        related_name="worker"
    )
    combined_position = models.ForeignKey(
        Position,
        on_delete=models.SET_NULL,
        **NULLABLE,
        verbose_name="Совмещаемая должность/профессия",
        related_name="combined_worker"
    )
