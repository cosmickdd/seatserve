"""
Tests for accounts app
"""
from django.test import TestCase
from accounts.models import User


class UserModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )

    def test_user_creation(self):
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertTrue(self.user.check_password('testpass123'))

    def test_user_role(self):
        self.assertEqual(self.user.role, 'CUSTOMER')

    def test_superuser_creation(self):
        admin = User.objects.create_superuser(
            email='admin@example.com',
            password='admin123'
        )
        self.assertEqual(admin.role, 'SUPER_ADMIN')
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)
