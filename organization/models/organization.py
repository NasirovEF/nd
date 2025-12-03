from django.db import models

from organization.services import NULLABLE


class Organization(models.Model):
    """Класс ОСТ"""

    name = models.CharField(max_length=150, verbose_name="Наименование ОСТ", unique=True)
    full_name = models.CharField(max_length=250, verbose_name="Полное наименование ОСТ")
    abbreviation = models.CharField(max_length=50, verbose_name="Аббревиатура ОСТ")
    is_main = models.BooleanField(verbose_name="Признак основной ОСТ", default=False)

    class Meta:
        verbose_name = "ОСТ"
        verbose_name_plural = "ОСТы"

    def __str__(self):
        return f"{self.name}"


class Branch(models.Model):
    """Класс филиала ОСТ"""

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        verbose_name="ОСТ",
        related_name="branch",
        **NULLABLE
    )
    name = models.CharField(max_length=150, verbose_name="Наименование филиала", unique=True)
    full_name = models.CharField(max_length=250, verbose_name="Полное наименование филиала")
    abbreviation = models.CharField(max_length=50, verbose_name="Аббревиатура филиала")

    class Meta:
        verbose_name = "Филиал"
        verbose_name_plural = "Филиалы"

    def __str__(self):
        return f"{self.name}"


class Group(models.Model):
    """Класс группы участка"""

    district = models.ForeignKey("District", on_delete=models.CASCADE, verbose_name="Участок", related_name="group", **NULLABLE)
    name = models.CharField(max_length=150, verbose_name="Наименование группы")
    abbreviation = models.CharField(max_length=50, verbose_name="Аббревиатура")

    class Meta:
        verbose_name = "Группа"
        verbose_name_plural = "Группа"

    def __str__(self):
        return f"{self.name}"


class District(models.Model):
    """Класс участка"""

    name = models.CharField(max_length=150, verbose_name="Наименование участка")
    abbreviation = models.CharField(max_length=50, verbose_name="Аббревиатура")
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

    def __str__(self):
        return f"{self.name}"


class Division(models.Model):
    """Класс структурного подразделения"""

    name = models.CharField(
        max_length=150, verbose_name="Наименование структурного подразделения", unique=True
    )
    abbreviation = models.CharField(max_length=50, verbose_name="Аббревиатура")

    branch = models.ForeignKey(
        Branch, on_delete=models.CASCADE, verbose_name="филиал", related_name="division", **NULLABLE
    )

    class Meta:
        verbose_name = "Структурное подразделение"
        verbose_name_plural = "Структурные подразделения"

    def __str__(self):
        return f"{self.name}"
