from django.db import models

from organization.models import Organization
from organization.services import NULLABLE
from learning.services import get_current_date


class AccidentСategory(models.Model):
    name = models.CharField(max_length=150, verbose_name="Категория НС")
    
    class Meta:
        verbose_name = "Категория НС"
        verbose_name_plural = "Категории НС"

    def __str__(self):
        return f"{self.name}"


class Accident(models.Model):
    order = models.CharField(max_length=350, verbose_name="№ и дата информационного письма")
    title = models.CharField(max_length=350, verbose_name="Титул", **NULLABLE)
    scene = models.CharField(max_length=350, verbose_name="Место происшествия", **NULLABLE)
    date = models.DateField(verbose_name="Дата происшествия", default=get_current_date)
    organization = models.ForeignKey(
        Organization,
        on_delete=models.SET_NULL,
        verbose_name="ОСТ",
        related_name="accident",
        **NULLABLE
    )
    contractor = models.CharField(
        max_length=250, verbose_name="Подрядная организация", **NULLABLE
    )
    category = models.ForeignKey(
        AccidentСategory,
        on_delete=models.SET_NULL,
        verbose_name="Категория НС",
        related_name="accident",
        **NULLABLE
    )
    victim = models.CharField(max_length=350, verbose_name="Пострадавший", **NULLABLE)
    victims_count = models.PositiveIntegerField(verbose_name="Количество пострадавших")
    is_death = models.BooleanField(default=False, verbose_name="Смертельный")
    description = models.TextField(verbose_name="Краткие обстоятельства")
    image = models.ImageField(
        upload_to="accident/photo", verbose_name="Фото", **NULLABLE
    )
    cause = models.TextField(verbose_name="Причины несчастного случая", **NULLABLE)
    safety_requirements = models.TextField(verbose_name="Требования безопасности", **NULLABLE)

    class Meta:
        verbose_name = "Несчастный случай"
        verbose_name_plural = "Несчастные случаи"
        ordering = ("-date",)

    def __str__(self):
        return self.order


class DangerCategory(models.Model):
    """Категория опасности"""
    name = models.CharField("Название категории", max_length=255)
    order = models.PositiveIntegerField("Порядок сортировки", default=0)

    class Meta:
        verbose_name = "Категория опасности"
        verbose_name_plural = "Категории опасностей"
        ordering = ("order",)

    def __str__(self):
        return self.name


class DangerType(models.Model):
    """Тип опасности"""
    category = models.ForeignKey(
        DangerCategory,
        verbose_name='Категория опасности',
        on_delete=models.CASCADE,
        related_name='types'
    )
    description = models.TextField("Описание типа опасности")
    order = models.PositiveIntegerField("Порядок сортировки", default=0)

    class Meta:
        verbose_name = "Тип опасности"
        verbose_name_plural = "Типы опасности"
        ordering = ("order",)

    def __str__(self):
        return f"{self.category.name} - {self.description}"


class DangerEvent(models.Model):
    """Опасное событие"""
    type = models.ForeignKey(
        DangerType,
        verbose_name='Тип опасности',
        on_delete=models.CASCADE,
        related_name='events'
    )
    order = models.PositiveIntegerField("Порядок сортировки", default=0)
    code = models.CharField("Код события", max_length=10, unique=True, **NULLABLE)
    event_description = models.TextField("Описание события")

    class Meta:
        verbose_name = "Опасное событие"
        verbose_name_plural = "Опасные события"
        ordering = ("code",)

    def __str__(self):
        return f"{self.code} - {self.event_description}"

    def save(self, *args, **kwargs):
        self.code = f'{self.type.category.order}.{self.type.order}.{self.order}'
        self.clean()
        super().save(*args, **kwargs)
