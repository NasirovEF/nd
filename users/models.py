from django.db import models
from django.contrib.auth.models import AbstractUser
from transliterate import translit

NULLABLE = {"null": True, "blank": True}


class User(AbstractUser):
    username = models.CharField(max_length=20, verbose_name="Имя пользователя")
    email = models.EmailField(unique=True, verbose_name="Почта", **NULLABLE)
    worker = models.OneToOneField(
        "organization.Worker",
        verbose_name="Работник",
        on_delete=models.CASCADE,
        related_name="user", **NULLABLE)
    service_number = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Табельный номер",
        **NULLABLE
    )

    USERNAME_FIELD = "service_number"
    REQUIRED_FIELDS = []

    @property
    def get_login_name(self):
        surname = self.worker.surname or ""
        name_initial = (self.worker.name or "")[:1]
        patronymic_initial = (self.worker.patronymic or "")[:1]
        login_ru = surname + name_initial + patronymic_initial
        login_en = translit(login_ru, 'ru', reversed=True)
        return login_en

    def save(self, *args, **kwargs):
        if self.worker and self.worker.service_number:
            self.service_number = self.worker.service_number
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return f'{self.worker}'

