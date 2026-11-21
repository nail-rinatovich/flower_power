import os

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction


class Command(BaseCommand):
    help = 'Создаёт администратора из переменных окружения без интерактивного Shell.'

    @transaction.atomic
    def handle(self, *args, **options):
        username = os.environ.get('DJANGO_SUPERUSER_USERNAME', '').strip()
        if not username:
            raise CommandError('Set DJANGO_SUPERUSER_USERNAME in Render Environment.')

        User = get_user_model()
        existing = User.objects.filter(username=username).first()
        if existing:
            if not (existing.is_active and existing.is_staff and existing.is_superuser):
                raise CommandError('The chosen username belongs to an inactive or non-admin account. Choose another username.')
            self.stdout.write('Administrator already exists; password unchanged.')
            return

        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', '')
        if not password:
            raise CommandError('Set DJANGO_SUPERUSER_PASSWORD in Render Environment.')
        user = User(username=username, email='')
        try:
            user.full_clean(exclude=['password'])
            validate_password(password, user)
        except ValidationError:
            raise CommandError('Invalid administrator username or weak password. Use a valid username and a strong unique password.') from None
        User.objects.create_superuser(username=username, email='', password=password)
        self.stdout.write(self.style.SUCCESS('Administrator created.'))
