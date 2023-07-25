from django.test import TestCase
from django.urls import reverse

# Create your tests here.
from products_app.models import ProcessorList, VideoCardList, MotherboardList, MemoryList


class IndexTestCase(TestCase):
    # def setUp(self):  # создаем тестовую запись в таблице
    #     ProcessorList.objects.create(
    #         sku='555',
    #         category_id=1,
    #         brand_id=61,
    #         name='test_processor_name',
    #         description='test_processor_description',
    #         short_description='test_processor_short_description',
    #         thumbnail='static/img/test-photo.png',
    #         price='555',
    #         quantity='555',
    #         active=False,
    #         line_id=29,
    #         socket_id=7,
    #         cores='555',
    #         base_frequency='555',
    #         max_frequency='555',
    #         memory_type_id=12,
    #         tdp='555'
    #     )
    #     print('Processor test created')

    def test_index_view(self):
        path = reverse('index')
        response = self.client.get(path)

        self.assertEqual(response.status_code, 200)
        # print(response.)
        # self.assertEqual(response., 'qwe')