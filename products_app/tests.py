from django.test import TestCase
from django.urls import reverse


# Create your tests here.


class IndexTestCase(TestCase):
    fixtures = ['categories.json', 'brands.json', 'sockets.json', 'memory_types.json', 'cpu_lines.json',
                'gpu_pci_versions.json', 'gpu_models.json', 'mb_form_factors.json', 'mb_chipsets.json',
                'products_images.json', 'list_rams.json', 'list_videocards.json', 'list_motherboards.json',
                'list_processors.json']

    def setUp(self) -> None:
        self.path = reverse('index')
        self.response = self.client.get(self.path)

    def test_index_template(self):
        self.assertTemplateUsed(self.response, 'products_app/index.html')
        self.assertEqual(self.response.status_code, 200, 'Статус код НЕ 200')

    def test_index_title(self):
        self.assertEqual(self.response.context_data['title'], 'e-Store - Главная')

    def test_index_queryset(self):
        self.assertEqual(len(self.response.context_data['random_products']), 8, 'len queryset < 8')
        self.assertEqual(len([x for x in self.response.context_data['random_products'] if x.category_id == 1]), 2,
                         'len queryset Processor < 2')
        self.assertEqual(len([x for x in self.response.context_data['random_products'] if x.category_id == 2]), 2,
                         'len queryset Videocard < 2')
        self.assertEqual(len([x for x in self.response.context_data['random_products'] if x.category_id == 3]), 2,
                         'len queryset Motherboard < 2')
        self.assertEqual(len([x for x in self.response.context_data['random_products'] if x.category_id == 4]), 2,
                         'len queryset Ram < 2')


class CatalogTestCase(TestCase):
    ...
