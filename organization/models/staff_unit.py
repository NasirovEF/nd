from django.db import models
from organization.models import Organization, Branch, Division, District, Group
from organization.services import NULLABLE
from smart_selects.db_fields import ChainedForeignKey


class Affiliation(models.Model):
    organization = models.ForeignKey(Organization, verbose_name="ОСТ", on_delete=models.SET_NULL, **NULLABLE)
    branch = ChainedForeignKey(
        Branch,
        chained_field="organization",
        chained_model_field="organization",
        show_all=False,
        auto_choose=False,
        sort=True,
        verbose_name="Филиал",
        on_delete=models.SET_NULL,
        **NULLABLE
    )

    division = ChainedForeignKey(
        Division,
        chained_field="branch",
        chained_model_field="branch",
        show_all=False,
        auto_choose=False,
        sort=True,
        verbose_name="Структурное подразделение",
        on_delete=models.SET_NULL,
        **NULLABLE
    )
    district = ChainedForeignKey(
        District,
        chained_field="division",
        chained_model_field="division",
        show_all=False,
        auto_choose=False,
        sort=True,
        verbose_name="Участок",
        on_delete=models.SET_NULL,
        **NULLABLE)
    group = ChainedForeignKey(
        Group,
        chained_field="district",
        chained_model_field="district",
        show_all=False,
        auto_choose=False,
        sort=True,
        verbose_name="Группа",
        on_delete=models.SET_NULL,
        **NULLABLE)

    @property
    def return_str_affiliation(self):
        fields = [self.organization, self.branch, self.division, self.district, self.group]
        return " ".join(str(field) for field in fields if field)

    class Meta:
        verbose_name = "Организационная принадлежность"
        verbose_name_plural = "Организационные принадлежности"
        abstract = True


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


class Worker(Affiliation):
    """Класс работника"""

    surname = models.CharField(max_length=50, verbose_name="Фамилия")
    name = models.CharField(max_length=50, verbose_name="Имя")
    patronymic = models.CharField(max_length=50, verbose_name="Отчество", **NULLABLE)
    image = models.ImageField(upload_to="organization/worker/", verbose_name="Фотография работника",  **NULLABLE)
    service_number = models.CharField(max_length=30, verbose_name="Табельный номер", unique=True)
    dismissed = models.BooleanField(verbose_name="Уволен", default=False)

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
