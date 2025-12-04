from django.utils import timezone
from django.apps import apps


def get_current_date():
    return timezone.now().date()


def add_doc_url(instance, filename):
    """
    Функция для upload_to в FileField.
    Формирует путь с префиксом по названию приложения.
    """
    # Получаем название приложения модели
    app_label = instance._meta.app_label

    path_parts = [
        app_label,
        instance.__class__.__name__,
        str(instance.organization.pk)
    ]

    if instance.branch:
        path_parts.append(str(instance.branch.pk))
    if instance.division:
        path_parts.append(str(instance.division.pk))
    if instance.district:
        path_parts.append(str(instance.district.pk))
    if instance.group:
        path_parts.append(str(instance.group.pk))

    path_parts.append(filename)

    return '/'.join(path_parts)


def add_prot_url(instance, file_name):
    return f"learning/{instance.__class__.__name__}/{instance.division.branch.organization.pk}/{instance.division.branch.pk}/{instance.division.pk}/{file_name}"
