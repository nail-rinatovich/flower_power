import os
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.management import call_command, CommandError
from django.test import TestCase


class BootstrapAdminTests(TestCase):
    credentials = {
        'DJANGO_SUPERUSER_USERNAME': 'render-admin',
        'DJANGO_SUPERUSER_PASSWORD': 'Test-Only-Strong-Password-4972',
    }

    def test_creates_admin_without_email_and_can_login(self):
        with patch.dict(os.environ, self.credentials):
            call_command('bootstrap_admin')
        user = get_user_model().objects.get(username='render-admin')
        self.assertTrue(user.is_active and user.is_staff and user.is_superuser)
        self.assertEqual(user.email, '')
        self.assertTrue(self.client.login(username=user.username, password=self.credentials['DJANGO_SUPERUSER_PASSWORD']))
        self.assertEqual(self.client.get('/admin/').status_code, 200)

    def test_restart_does_not_overwrite_password(self):
        with patch.dict(os.environ, self.credentials):
            call_command('bootstrap_admin')
        user = get_user_model().objects.get(username='render-admin')
        original_hash = user.password
        with patch.dict(os.environ, {**self.credentials, 'DJANGO_SUPERUSER_PASSWORD': 'Changed-Env-Secret-7836'}):
            call_command('bootstrap_admin')
        user.refresh_from_db()
        self.assertEqual(user.password, original_hash)
        self.assertEqual(get_user_model().objects.count(), 1)

    def test_missing_or_weak_password_does_not_create_account(self):
        for password in ['', '124']:
            with patch.dict(os.environ, {**self.credentials, 'DJANGO_SUPERUSER_PASSWORD': password}):
                with self.assertRaises(CommandError):
                    call_command('bootstrap_admin')
            self.assertFalse(get_user_model().objects.exists())

    def test_existing_regular_user_is_not_promoted(self):
        user = get_user_model().objects.create_user('render-admin', password='Other-Strong-Secret-6872')
        with patch.dict(os.environ, self.credentials):
            with self.assertRaises(CommandError):
                call_command('bootstrap_admin')
        user.refresh_from_db()
        self.assertFalse(user.is_staff or user.is_superuser)
