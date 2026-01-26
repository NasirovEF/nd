from django.db import models
from organization.models import Organization, Branch, Division, District, Group
from organization.services import NULLABLE
from smart_selects.db_fields import ChainedForeignKey
from django.core.exceptions import ValidationError


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
    def get_last_filled(self):
        fields = [
            self.organization,
            self.branch,
            self.division,
            self.district,
            self.group
        ]
        last_filled = None
        for field in fields:
            if field is not None:
                last_filled = field
        return last_filled

    @property
    def return_affiliation(self):
        list_fields = [self.organization, self.branch, self.division, self.district, self.group]
        affiliation_list = []
        for field in list_fields:
            if field:
                affiliation_list.append(field)
        return affiliation_list


    @property
    def return_str_affiliation(self):
        fields = [self.organization, self.branch, self.division, self.district, self.group]
        return " ".join(str(field) for field in fields if field)

    class Meta:
        verbose_name = "Организационная принадлежность"
        verbose_name_plural = "Организационные принадлежности"


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

    @property
    def return_fio(self):
        if self.patronymic:
            return f'{self.name[:1]}.{self.patronymic[:1]}. {self.surname}'
        else:
            return f'{self.name[:1]}. {self.surname}'

    def __str__(self):
        if self.patronymic:
            return f'{self.position.get(is_main=True)} {self.name[:1]}.{self.patronymic[:1]}. {self.surname}'
        else:
            return f'{self.position.get(is_main=True)} {self.name[:1]}. {self.surname}'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if hasattr(self, 'user'):
            if self.dismissed:
                self.user.is_active = False
                self.user.save(update_fields=['is_active'])
            else:
                self.user.is_active = True
                self.user.save(update_fields=['is_active'])

    def clean(self):
        super().clean()
        # Проверяем согласованность связей
        if self.division and self.branch and self.division.branch != self.branch:
            raise ValidationError("Подразделение не принадлежит указанному филиалу")

        if self.district and self.division and self.district.division != self.division:
            raise ValidationError("Участок не принадлежит указанному подразделению")

        if self.group and self.district and self.group.district != self.district:
            raise ValidationError("Группа не принадлежит указанному участку")


class ResponsibilityLevel(models.Model):
    """Уровни ответственности (перечислитель)"""
    LEVEL_CHOICES = [
        ('organization', 'Организация'),
        ('branch', 'Филиал'),
        ('division', 'Структурное подразделение'),
        ('district', 'Участок'),
        ('group', 'Группа'),
    ]
    code = models.CharField(max_length=20, choices=LEVEL_CHOICES, unique=True)
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name = "Уровень ответственности"
        verbose_name_plural = "Уровни ответственности"

    def __str__(self):
        return self.name


class ResponsibleForTraining(Affiliation):
    """Ответственный за инструктаж/обучение"""
    responsible_worker = models.ForeignKey(
        Worker,
        on_delete=models.CASCADE,
        verbose_name="Ответственный работник",
        related_name="responsibilities"
    )
    level = models.ForeignKey(
        ResponsibilityLevel,
        on_delete=models.CASCADE,
        verbose_name="Уровень ответственности"
    )

    # Привязка к группам работников (PositionGroup)
    position_groups = models.ManyToManyField(
        PositionGroup,
        verbose_name="Группы работников",
        blank=True
    )

    is_active = models.BooleanField(verbose_name="Активно", default=True)
    start_date = models.DateField(verbose_name="Дата назначения", auto_now_add=True)
    end_date = models.DateField(verbose_name="Дата окончания", null=True, blank=True)

    class Meta:
        verbose_name = "Ответственный за обучение"
        verbose_name_plural = "Ответственные за обучение"

    def __str__(self):
        return f"{self.worker} ({self.level})"

    def clean(self):
        # Валидация: заполняем только те поля, которые соответствуют уровню
        level_code = self.level.code
        fields = {
            'organization': self.organization,
            'branch': self.branch,
            'division': self.division,
            'district': self.district,
            'group': self.group
        }
        for code, value in fields.items():
            if code == level_code and not value:
                raise ValidationError(f"Для уровня '{level_code}' необходимо указать сущность.")
            if code != level_code and value:
                raise ValidationError(f"Для уровня '{level_code}' поле '{code}' должно быть пустым.")
