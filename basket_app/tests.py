from django.test import TestCase
from django.urls import reverse


# Create your tests here.


class BasketViewTestCase(TestCase):
    fixtures = [
        'category.json',
        'brand.json',
        'socket.json',
        'cpuline.json',
        'gpumodel.json',
        'gpupciversion.json',
        'mbformfactor.json',
        'mbchipset.json',
        'memorytype.json',
        'ProcessorList.json',
        'VideoCardList.json',
        'MotherboardList.json',
        'MemoryList.json',
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

        '''Проверяем, есть ли добавленный товар в корзине'''
        # в тестах нет доступа до middleware, корзина хранится в context_processors
        # RequestFactory, @override_settings
