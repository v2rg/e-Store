from django.test import TestCase
from django.urls import reverse


# Create your tests here.

class BasketViewTestCase(TestCase):
    fixtures = [
        'categories.json', 'brands.json', 'sockets.json', 'cpu_lines.json',
        'gpu_models.json', 'gpu_pci_versions.json', 'mb_form_factors.json',
        'mb_chipsets.json', 'memory_types.json', 'list_processors.json',
        'list_videocards.json', 'list_motherboards.json', 'list_rams.json',
        'test_users.json'
    ]

    def setUp(self) -> None:
        self.response = self.client.get(reverse('basket:basket'))

    def test_Basket_user_no_auth_get(self):
        self.assertEqual(self.response.status_code, 200)
        self.assertEqual(self.response.context_data['title'], 'e-Store - Корзина')
        self.assertTemplateUsed(self.response, 'basket_app/basket.html')  # корзину видно БЕЗ авторизации
        self.assertContains(self.response, 'Корзина пуста', html=True)

    def test_Basket_user_auth_get(self):
        login = self.client.login(username='test', password='qwe!@#123')

        self.assertTrue(login)
        self.assertEqual(self.response.status_code, 200)
        self.assertEqual(self.response.context_data['title'], 'e-Store - Корзина')
        self.assertTemplateUsed(self.response, 'basket_app/basket.html')  # корзину видно после авторизации
        self.assertContains(self.response, 'Корзина пуста', html=True)

        '''Добавляем товар в корзину'''
        response = self.client.get(
            reverse('basket:basket_add', kwargs={'category_id': 2, 'product_sku': 5408056})
        )  # добавляем товар в корзину
        self.assertEqual(response.status_code, 302)  # редирект после добавления товара

        response = self.client.get(reverse('basket:basket'))
        self.assertEqual(response.context_data['title'], 'e-Store - Корзина')
        self.assertEqual(response.status_code, 200)

        # self.assertContains(response, 'Корзина 1', html=True)
        # self.assertQuerysetEqual(response, 'qwe')


class BasketAddTestCase(TestCase):
    ...


class BasketRemoveTestCase(TestCase):
    ...


class BasketUpdateTestCase(TestCase):
    ...


class OrderConfirmationTestCase(TestCase):
    ...
