from django.db import models
from django.core.exceptions import ValidationError
from learning.services import add_doc_url, get_current_date
from organization.models import Position, Worker, StaffUnit
from organization.models.staff_unit import Affiliation
from organization.services import NULLABLE
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
import os
from django.utils.deconstruct import deconstructible


@deconstructible
class ProgramUploadPath:
    def __init__(self, subfolder):
        self.subfolder = subfolder

    def __call__(self, instance, filename):
        program = instance.content_object
        if program.__class__.__name__ == 'Program':
            program_type = 'program'
        elif program.__class__.__name__ == 'ProgramBriefing':
            program_type = 'briefing'
        else:
            raise ValueError(f"Неподдерживаемый тип: {program.__class__.__name__}")

        return os.path.join(
            'learning',
            f'{program_type}_{program.pk}',
            self.subfolder,
            filename
        )


doc_upload_path = ProgramUploadPath('docs')
poster_upload_path = ProgramUploadPath('posters')


class Direction(models.Model):
    """Модель направления обучения"""
    name = models.CharField(max_length=150, verbose_name="Направление обучения", unique=True)
    description = models.TextField(verbose_name="Описание", **NULLABLE)
    periodicity = models.PositiveIntegerField(verbose_name="Периодичность обучения в днях")
    have_sub_direction = models.BooleanField(verbose_name="Имеет поднаправления", default=False, help_text="Только для 'В'")

    class Meta:
        verbose_name = "Направление обучения"
        verbose_name_plural = "Направления обучения"

    def __str__(self):
        return f"{self.name}"

    def save(self, *args, **kwargs):
        is_creating = not self.pk
        super().save(*args, **kwargs)

        if is_creating:
            from learning.models import Test
            if not Test.objects.filter(
                    direction=self,
                    sub_direction__isnull=True
            ).exists():
                Test.objects.create(
                    direction=self
                )


class SubDirection(models.Model):
    """Класс поднаправлений для программы В"""

    name = models.CharField(verbose_name="Направления обучения по программе В", max_length=250)
    direction = models.ForeignKey(Direction, on_delete=models.CASCADE, verbose_name="Направление обучения", related_name="sub_direction")

    class Meta:
        verbose_name = "Поднаправление обучения для программы В"
        verbose_name_plural = "Поднаправления обучения для программы В"

    def __str__(self):
        return f"{self.name}"

    def clean(self):
        if not self.direction.have_sub_direction:
            raise ValidationError("Данное направление обучение только для программы 'B'")


    def save(self, *args, **kwargs):
        is_creating = not self.pk
        super().save(*args, **kwargs)  # Сохраняем поднаправление

        # Если это создание — создаём тест
        if is_creating:
            from learning.models import Test
            if not Test.objects.filter(sub_direction=self).exists():
                Test.objects.create(
                    direction=self.direction,
                    sub_direction=self
                )


class BaseProgram(Affiliation):
    """Базовая модель программы обучения/инструктажа"""
    name = models.CharField(max_length=150, verbose_name="Наименование программы")
    duration = models.PositiveIntegerField(verbose_name="Продолжительность обучения (часов)")
    staffunit = models.ForeignKey(StaffUnit, on_delete=models.SET_NULL, verbose_name="Наименование профессии", **NULLABLE)
    position_group = models.ForeignKey("organization.PositionGroup", on_delete=models.SET_NULL, verbose_name="Наименование группы работников", **NULLABLE)
    approve = models.CharField(max_length=150, verbose_name="Программа утверждена", help_text="Введите должность, И.О. Фамилию лица утвердившего программу")
    approval_date = models.DateField(verbose_name="Дата утверждения программы", default=get_current_date, help_text="Введите дату в формате ДД.ММ.ГГГГ")
    replacement = models.ForeignKey("self", on_delete=models.SET_NULL, verbose_name="Замена программы", help_text="Выберите программу, которую эта программа заменяет (не может быть самой собой)", **NULLABLE)
    is_active = models.BooleanField(verbose_name="Актуальность", default=True)
    doc_scan = models.FileField(verbose_name="Скан-копия программы обучения",
                                upload_to=add_doc_url, **NULLABLE)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

        if self.replacement:
            try:
                # Получаем модель текущего объекта (Program или ProgramBriefing)
                current_model = self.__class__

                # Ищем замещённую программу ТОГО ЖЕ ТИПА
                replaced_program = current_model.objects.get(pk=self.replacement.pk)

                if replaced_program.is_active:
                    replaced_program.is_active = False
                    replaced_program.save(update_fields=['is_active'])

                    # Если у модели есть связанное поле 'exams' — обновляем
                    if hasattr(replaced_program, 'exams'):
                        replaced_program.exams.update(is_active=False)

            except current_model.DoesNotExist:
                raise ValidationError(f"Программа с ID {self.replacement.pk} не найдена.")

    def get_learning_docs(self):
        """Возвращает все LearningDoc, связанные с этим Program"""
        content_type = ContentType.objects.get_for_model(self)
        return LearningDoc.objects.filter(
            content_type=content_type,
            object_id=self.pk
        )

    def get_learning_posters(self):
        """Возвращает все LearningPoster, связанные с этим Program"""
        contenttype = ContentType.objects.get_for_model(self)
        return LearningPoster.objects.filter(
            content_type=contenttype,
            object_id=self.pk
        )

    def __str__(self):
        return f"{self.name}"


class Program(BaseProgram):
    """Модель программы обучения"""
    direction = models.ManyToManyField(Direction, related_name="program", verbose_name="Направление обучения")
    subdirection = models.ManyToManyField(SubDirection, related_name="program", verbose_name="Поднаправление обучения", blank=True, help_text="В случае если выбрано направление обучения 'В'")

    class Meta:
        verbose_name = "Программа обучения"
        verbose_name_plural = "Программы обучения"

    def str_direction(self):
        directions = self.direction.all()
        if not directions:
            return "Направления не указаны"
        return ", ".join(str(direction) for direction in directions)

    def str_subdirection(self):
        subdirections = self.subdirection.all()
        if not subdirections:
            return ""
        return ", ".join(str(subdirection) for subdirection in subdirections)


class LearningDoc(models.Model):
    """Модель документов для обучения"""
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    name = models.CharField(verbose_name="Наименование документа", max_length=250)
    doc = models.FileField(verbose_name="Файл документа", upload_to=doc_upload_path)

    class Meta:
        verbose_name = "Документ для обучения"
        verbose_name_plural = "Документы для обучения"


class LearningPoster(models.Model):
    """Модель плаката обучения"""
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    name = models.CharField(verbose_name="Наименование плаката", max_length=250)
    image = models.ImageField(verbose_name="Картинка плаката", upload_to=poster_upload_path)

    class Meta:
        verbose_name = "Плакат для обучения"
        verbose_name_plural = "Плакаты для обучения"


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
        return f"{self.position}, {self.worker.return_fio}"


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

