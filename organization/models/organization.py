from django.db import models
from django.core.exceptions import ValidationError
from organization.services import NULLABLE


class BaseNamedEntity(models.Model):
    """
    Абстрактный базовый класс для всех именованных сущностей.
    Содержит общие поля: название, полное название, аббревиатура.
    """
    name = models.CharField(
        max_length=150,
        verbose_name="Наименование",
        help_text="Краткое официальное название",
        unique=True
    )
    full_name = models.CharField(
        max_length=250,
        verbose_name="Полное наименование",
        blank=True,
        help_text="Полное официальное название (если отличается от краткого)"
    )
    abbreviation = models.CharField(
        max_length=50,
        verbose_name="Аббревиатура",
        blank=True,
        help_text="Сокращённое обозначение"
    )

    class Meta:
        abstract = True
        ordering = ['name']

    def __str__(self):
        return f'{self.abbreviation}' if self.abbreviation else f'{self.name}'

    def clean(self):
        """Базовая валидация именованных сущностей."""
        if not self.name:
            raise ValidationError("Наименование не может быть пустым")


class Organization(BaseNamedEntity):
    """Класс ОСТ"""

    is_main = models.BooleanField(verbose_name="Признак основной ОСТ", default=False)
    is_transit = models.BooleanField(verbose_name="Транспортная ОСТ", default=False)

    class Meta:
        verbose_name = "ОСТ"
        verbose_name_plural = "ОСТы"

    @staticmethod
    def return_parent():
        parent_list = []
        return parent_list


class Branch(BaseNamedEntity):
    """Класс филиала ОСТ"""

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        verbose_name="ОСТ",
        related_name="branch",
        **NULLABLE
    )

    class Meta:
        verbose_name = "Филиал"
        verbose_name_plural = "Филиалы"

    def return_parent(self):
        parent_list = [self.organization]
        return parent_list

    def __str__(self):
        return f"{self.name}"


class Group(BaseNamedEntity):
    """Класс группы участка"""

    district = models.ForeignKey(
        "District",
        on_delete=models.CASCADE,
        verbose_name="Участок",
        related_name="group",
        **NULLABLE)

    class Meta:
        verbose_name = "Группа"
        verbose_name_plural = "Группы"

    def return_parent(self):
        parent_list = [self.district.division.branch.organization,
                       self.district.division.branch,
                       self.district.division,
                       self.district,
                       ]
        return parent_list

    def __str__(self):
        return f"{self.name}"


class District(BaseNamedEntity):
    """Класс участка"""

    division = models.ForeignKey(
        "Division",
        on_delete=models.CASCADE,
        verbose_name="Наименование структурного подразделения",
        related_name="district",
        **NULLABLE
    )

    class Meta:
        verbose_name = "Участок"
        verbose_name_plural = "Участки"

    def return_parent(self):
        parent_list = [self.division.branch.organization,
                       self.division.branch,
                       self.division,
                       ]
        return parent_list

    def __str__(self):
        return f"{self.name}"


class Division(BaseNamedEntity):
    """Класс структурного подразделения"""

    branch = models.ForeignKey(
        Branch, on_delete=models.CASCADE, verbose_name="филиал", related_name="division", **NULLABLE
    )

    class Meta:
        verbose_name = "Структурное подразделение"
        verbose_name_plural = "Структурные подразделения"

    def __str__(self):
        return f"{self.name}"

    def return_parent(self):
        parent_list = [self.branch.organization,
                       self.branch,
                       ]
        return parent_list
