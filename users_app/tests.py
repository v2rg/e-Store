import datetime

from django.test import TestCase
from django.urls import reverse

from basket_app.models import Order, OrderItem
from products_app.models import Category
from users_app.models import User


# Create your tests here.

class UserLoginViewTestCase(TestCase):  # авторизация пользователя
    fixtures = ['test_users.json']
    fixtures += ['categories.json', 'brands.json', 'sockets.json',
                 'memory_types.json', 'test_cpu_lines.json', 'gpu_pci_versions.json',
                 'gpu_models.json', 'mb_form_factors.json', 'mb_chipsets.json',
                 'products_images.json', 'test_list_rams.json', 'test_list_videocards.json',
                 'test_list_motherboards.json']  # фикстуры для редиректа

    def setUp(self) -> None:
        self.path = reverse('users:login')
        self.test_user = {'username': 'test', 'password': 'qwe!@#123'}

    def test_User_login_get(self):
        response = self.client.get(self.path)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['title'], 'e-Store - Авторизация')  # заголовок
        self.assertTemplateUsed(response, 'users_app/login.html')  # шаблон

    def test_User_login_post(self):
        response = self.client.post(self.path, data=self.test_user)

        self.assertEqual(response.status_code, 302)  # редирект после удачной авторизации
        self.assertRedirects(response, expected_url=reverse('index'))  # редирект на index

    def test_User_login_errors(self):
        response = self.client.post(self.path, data={'username': 'test', 'password': 'qwe'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            'Пожалуйста, введите правильные имя пользователя и пароль. Оба поля могут быть чувствительны к регистру.',
            html=True
        )  # error message


class UserRegistrationViewTestCase(TestCase):  # регистрация нового пользователя
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

    def test_Users_registration_post(self):  # создание нового пользователя
        self.assertFalse(User.objects.filter(username=self.new_user['username']).exists())  # user НЕ существует

        response = self.client.post(self.path, data=self.new_user)  # регистрируем нового пользователя

        self.assertRedirects(response, expected_url=reverse('users:login'))  # редирект на login, после создания
        self.assertTrue(User.objects.filter(username=self.new_user['username']).exists())  # user существует
        self.assertFalse(
            User.objects.get(username=self.new_user['username']).is_verified_email)  # почта НЕ подтверждена

    def test_Users_registrations_errors(self):  # ошибки при регистрации
        User.objects.create(username='test123', password='qwe!@#123')  # создаем user

        response = self.client.post(self.path, data=self.new_user)  # повторно создаем user через шаблон

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Пользователь с таким именем уже существует.', html=True)  # error message


class ProfileTestCase(TestCase):  # профиль пользователя
    fixtures = ['test_users.json']

    def setUp(self) -> None:
        self.path_profile = reverse('users:profile')
        self.user = {'username': 'test', 'password': 'qwe!@#123'}

    def test_Profile_not_login(self):  # редирект из профиля, если не авторизован
        response = self.client.get(self.path_profile)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, expected_url='/users/login/?next=/users/profile/')

    def test_Profile_form(self):
        login = self.client.login(username='test', password='qwe!@#123')  # авторизация
        self.assertEqual(login, True)  # успешная авторизация

        post_user = self.client.post(
            self.path_profile,
            data={
                'first_name': 'test_name_updated',
                'last_name': 'test_last_name_updated',
                'user': 'test_user'
            }
        )  # post user
        self.assertEqual(post_user.status_code, 302)  # редирект после обновления User

        post_address = self.client.post(
            self.path_profile,
            data={
                'postcode': '123',
                'city': 'test_city_updated',
                'street': 'test_street_updated',
                'building': 'test_building_updated',
                'address': 'test_address'
            }
        )  # post address
        self.assertEqual(post_address.status_code, 302)  # редирект после обновления UserAddress

        response = self.client.get(self.path_profile)

        self.assertEqual(response.status_code, 200)  # нет редиректа при переходе в профиль
        self.assertTemplateUsed(response, 'users_app/profile.html')
        self.assertEqual(response.context['title'], 'e-Store - Профиль')

        self.assertTrue(response.context['profile_form'])  # наличие формы в контексте
        self.assertContains(response, 'Адрес электронной почты', html=True)  # поле email в шаблоне
        self.assertContains(response, 'Улица', html=True)  # поле street в шаблоне

        # обновленные данные форм
        self.assertEqual(response.context['profile_form'].initial['first_name'], 'test_name_updated')
        self.assertEqual(response.context['profile_form'].initial['last_name'], 'test_last_name_updated')
        self.assertEqual(response.context['profile_form_address'].initial['city'], 'test_city_updated')
        self.assertEqual(response.context['profile_form_address'].initial['building'], 'test_building_updated')


class OrdersViewTestCase(TestCase):  # история заказов
    test_user = None
    fixtures = ['test_users.json']

    @classmethod
    def setUpTestData(cls):
        cls.test_user = User.objects.get(username='test')

        Order.objects.bulk_create(
            [Order(user_id=cls.test_user,
                   first_name='test_name',
                   last_name='test_last_name',
                   postcode='123',
                   city='test_city',
                   street='test_street',
                   building='test_building',
                   floor='123',
                   apartment='123',
                   created_datetime='',
                   total_quantity='3',
                   total_sum='12345',
                   comment='test_comment'),
             Order(user_id=cls.test_user,
                   first_name='test_name2',
                   last_name='test_last_name2',
                   postcode='321',
                   city='test_city2',
                   street='test_street2',
                   building='test_building2',
                   floor='321',
                   apartment='321',
                   status='shipping',
                   paid=True,
                   total_quantity='5',
                   total_sum='512345',
                   comment='test_comment2'),
             ]
        )  # добавляем 2 записи в таблицу Order

    def setUp(self) -> None:
        self.login = self.client.login(username='test', password='qwe!@#123')
        self.response = self.client.get(reverse('users:orders'))

    def test_Orders_get(self):
        self.assertTrue(self.login)  # пользователь авторизован
        self.assertEqual(self.response.status_code, 200)
        self.assertTemplateUsed(self.response, 'users_app/orders.html')

    def test_Orders_queryset(self):  # у пользователя есть история заказов
        orders_queryset = Order.objects.filter(user_id=self.test_user.pk)

        self.assertEqual(orders_queryset.count(), 2)  # количество элементов queryset
        self.assertContains(self.response, '12345 ₽', html=True)  # поле total_sum из тестовой записи
        self.assertContains(self.response, '512345 ₽', html=True)  # поле total_sum из тестовой записи
        self.assertContains(self.response, 'Оплатить', html=True)
        self.assertContains(self.response, 'Оплачены', html=True)

    def test_Orders_no_queryset(self):  # у пользователя НЕТ истории заказов
        Order.objects.filter(user_id=self.test_user.pk).delete()
        orders_queryset = Order.objects.filter(user_id=self.test_user)
        response = self.client.get(reverse('users:orders'))

        self.assertEqual(orders_queryset.count(), 0)  # количество элементов queryset
        self.assertQuerysetEqual(orders_queryset, [])  # queryset пустой
        self.assertContains(response, 'Заказов нет', html=True)  # заголовок при отсутствии заказов


class OrderTestCase(TestCase):
    test_order_id = None
    test_user = None
    fixtures = [
        'categories.json', 'brands.json', 'sockets.json', 'cpu_lines.json',
        'gpu_models.json', 'gpu_pci_versions.json', 'mb_form_factors.json',
        'mb_chipsets.json', 'memory_types.json', 'list_processors.json',
        'list_videocards.json', 'list_motherboards.json', 'list_rams.json',
        'test_users.json'
    ]

    @classmethod
    def setUpTestData(cls):
        cls.test_user = User.objects.get(username='test')

        Order.objects.create(
            user_id=cls.test_user,
            first_name='test_name',
            last_name='test_last_name',
            postcode='123',
            city='test_city',
            street='test_street',
            building='test_building',
            floor='123',
            apartment='123',
            created_datetime='',
            total_quantity='3',
            total_sum='12345',
            comment='test_comment'
        )  # заполняем таблицу Order

        cls.test_order_id = Order.objects.get(user_id=cls.test_user)

        OrderItem.objects.bulk_create(
            [OrderItem(order_id=cls.test_order_id,
                       user_id=cls.test_user,
                       product_category=Category.objects.get(category_name='Процессоры'),
                       product_sku=5074936,
                       quantity=1,
                       price=56999),
             OrderItem(order_id=cls.test_order_id,
                       user_id=cls.test_user,
                       product_category=Category.objects.get(category_name='Видеокарты'),
                       product_sku=5096481,
                       quantity=1,
                       price=112999),
             OrderItem(order_id=cls.test_order_id,
                       user_id=cls.test_user,
                       product_category=Category.objects.get(category_name='Материнские платы'),
                       product_sku=5079550,
                       quantity=1,
                       price=63999),
             OrderItem(order_id=cls.test_order_id,
                       user_id=cls.test_user,
                       product_category=Category.objects.get(category_name='Оперативная память'),
                       product_sku=5096548,
                       quantity=1,
                       price=29999),
             ]
        )  # заполняем таблицу OrderItem

    def setUp(self) -> None:
        self.login = self.client.login(username='test', password='qwe!@#123')
        self.response = self.client.get(reverse('users:order', kwargs={'order_id': 1}))

    def test_Order_get(self):
        self.assertEqual(self.response.status_code, 200)  # пользователь авторизован
        self.assertEqual(self.response.context['title'], 'Содержимое заказа')
        self.assertTemplateUsed(self.response, 'users_app/order.html')

        self.client.logout()  # логаут
        self.response = self.client.get(reverse('users:order', kwargs={'order_id': 1}))
        self.assertEqual(self.response.status_code, 302)  # редирект, если пользователь НЕ авторизован
        self.assertRedirects(self.response, expected_url='/users/login/?next=/users/order/1/')

    def test_Order_queryset(self):
        order_queryset = OrderItem.objects.filter(order_id=self.test_order_id, user_id=self.test_user)
        test_obj = ['<OrderItem: 1 | test | 5074936>', '<OrderItem: 1 | test | 5096481>',
                    '<OrderItem: 1 | test | 5079550>', '<OrderItem: 1 | test | 5096548>']

        self.assertTrue(order_queryset)  # queryset не пустой
        self.assertQuerysetEqual(list(order_queryset), test_obj)
        self.assertContains(
            self.response, ('Заказ № 1 от ' + datetime.date.strftime(datetime.date.today(), '%d.%m.%Y')), html=True
        )  # наличие заголовка с текущей датой
        self.assertContains(self.response, '<a href="/products/product/1/5074936/">5074936</a>',
                            html=True)  # наличие ссылки на товарную карточку
