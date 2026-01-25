from django.core.management import BaseCommand
from users.models import User


class Command(BaseCommand):

    def handle(self, *args, **options):
        user = User.objects.create(
            service_number="00000001",
            is_superuser=True,
            is_staff=True,
        )

        user.set_password("NEFo00000001")
        user.save()
