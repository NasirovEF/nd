from django.core.management import BaseCommand
from user.models import User


class Command(BaseCommand):

    def handle(self, *args, **options):
        user = User.objects.create(
            email="admin@admin.com",
            is_superuser=True,
            is_staff=True,
            phone_number="1234567890",
            country="Russia",
        )

        user.set_password("123456")
        user.save()
