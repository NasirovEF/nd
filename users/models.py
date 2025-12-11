from django.db import models
from django.contrib.auth.models import AbstractUser


NULLABLE = {"null": True, "blank": True}


class User(AbstractUser):
    username = models.CharField(max_length=50, verbose_name="Имя пользователя")
    email = models.EmailField(unique=True, verbose_name="Почта")
    service_number = models.CharField(max_length=30, verbose_name="Табельный номер")
    worker = models.OneToOneField("organization.Worker", verbose_name="Работник", on_delete=models.CASCADE, related_name="user")

    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.email

