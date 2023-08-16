from django.test import TestCase
from django.urls import reverse

from users_app.models import User, EmailVerification


# Create your tests here.

class UserRegistrationViewTestCase(TestCase):  # регистрация нового пользователя
    ...


class UserLoginViewTestCase(TestCase):
    def setUp(self):
        self.path = reverse('users:registration')
        self.new_user = {
            'first_name': 'test_name',
            'last_name': 'test_last_name',
            'username': 'test123',
            'email': 'qwasdaw@adadw.ey',
            'password1': 'qwe!@#123',
            'password2': 'qwe!@#123'
        }

    def test_Users_registration_get(self):
        response = self.client.get(self.path)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['title'], 'e-Store - Регистрация')
        self.assertTemplateUsed(response, 'users_app/registration.html')

    def test_Users_registration_post(self):
        self.assertFalse(User.objects.filter(username=self.new_user['username']).exists())  # user НЕ существует

        response = self.client.post(self.path, data=self.new_user)  # регистрируем нового пользователя

        self.assertRedirects(response, expected_url=reverse('users:login'))  # редирект на login, после создания
        self.assertTrue(User.objects.filter(username=self.new_user['username']).exists())  # user существует
        self.assertFalse(
            User.objects.get(username=self.new_user['username']).is_verified_email)  # почта НЕ подтверждена

    def test_Users_registrations_errors(self):
        User.objects.create(username='test123', password='qwe!@#123')  # создаем user

        response = self.client.post(self.path, data=self.new_user)  # повторно создаем user через шаблон

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'A user with that username already exists.', html=True)  # error message
