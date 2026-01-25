from django.apps import AppConfig
import django.db.models as models


class LearningConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "learning"

    def ready(self):
        # Импортируем модели после полной загрузки реестра
        from .models import Program, ProgramBriefing

        # Список моделей, для которых нужно настроить related_name
        models_to_fix = [Program, ProgramBriefing]

        for model in models_to_fix:
            for field in model._meta.get_fields():
                if isinstance(field, models.ForeignKey) and field.remote_field:
                    field.remote_field.related_name = f"{model.__name__.lower()}_{field.name}"
