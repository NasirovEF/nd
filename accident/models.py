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
    date = models.DateField(verbose_name="Дата НС", default=get_current_date)
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
    victims_count = models.PositiveIntegerField(verbose_name="Количество пострадавших")
    is_death = models.BooleanField(default=False, verbose_name="Смерть")
    description = models.TextField(verbose_name="Описание НС")
    image = models.ImageField(
        upload_to="accident/photo", verbose_name="Фото", **NULLABLE
    )

    class Meta:
        verbose_name = "Несчастный случай"
        verbose_name_plural = "Несчастные случаи"
        ordering = ("-date",)

    def __str__(self):
        return self.order
