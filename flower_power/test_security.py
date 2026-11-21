import base64
import secrets

from django.core.checks.security.base import check_secret_key
from django.test import SimpleTestCase, override_settings

from .security import normalize_render_secret


class RenderSecretTests(SimpleTestCase):
    def test_generated_render_secret_passes_django_deployment_check(self):
        raw = secrets.token_bytes(32)
        encoded = base64.b64encode(raw).decode('ascii')
        key = normalize_render_secret(encoded)
        self.assertEqual(bytes.fromhex(key), raw)
        self.assertEqual(key, normalize_render_secret(encoded))
        with override_settings(SECRET_KEY=key):
            self.assertEqual(check_secret_key(None), [])

    def test_weak_secrets_are_still_rejected(self):
        for value in ['124', 'a' * 44, 'django-insecure-' + 'x' * 50]:
            with override_settings(SECRET_KEY=normalize_render_secret(value)):
                self.assertEqual(check_secret_key(None)[0].id, 'security.W009')

    def test_long_custom_secret_is_unchanged(self):
        key = secrets.token_urlsafe(50)
        self.assertEqual(normalize_render_secret(key), key)
