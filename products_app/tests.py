from django.test import TestCase
from django.urls import reverse


# Create your tests here.


class IndexTestCase(TestCase):
    fixtures = ['categories.json', 'brands.json', 'sockets.json',
                'memory_types.json', 'test_cpu_lines.json', 'gpu_pci_versions.json',
                'gpu_models.json', 'mb_form_factors.json', 'mb_chipsets.json',
                'products_images.json', 'test_list_rams.json', 'test_list_videocards.json',
                'test_list_motherboards.json', 'test_list_processors.json']

    def setUp(self) -> None:
        self.path = reverse('index')
        self.response = self.client.get(self.path)

    def test_index_template(self):  # шаблон и статус код
        self.assertTemplateUsed(self.response, 'products_app/index.html')
        self.assertEqual(self.response.status_code, 200, 'Статус код НЕ 200')

    def test_index_title(self):  # заголовок
        self.assertEqual(self.response.context_data['title'], 'e-Store - Главная')

    def test_index_queryset(self):  # queryset на главной (по 2 из каждой категории)
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
    fixtures = ['categories.json', 'brands.json', 'sockets.json',
                'memory_types.json', 'test_cpu_lines.json', 'gpu_pci_versions.json',
                'gpu_models.json', 'mb_form_factors.json', 'mb_chipsets.json',
                'products_images.json', 'test_list_rams.json', 'test_list_videocards.json',
                'test_list_motherboards.json', 'test_list_processors.json']

    def setUp(self) -> None:
        self.path = reverse('products:catalog')
        self.response = self.client.get(self.path)

    def test_catalog_template(self):
        self.assertTemplateUsed(self.response, 'products_app/catalog.html')
        self.assertEqual(self.response.status_code, 200)

    '''catalog_category'''

    def test_catalog_queryset_processors(self):  # тест первой страницы (5 элементов) каталога (processor)
        self.response = self.client.get(reverse('products:catalog_category', kwargs={'category_id': 1}))

        first_page_cpus = [str(x) for x in self.response.context_data['page_obj']]
        test_obj = ['88888885 | Intel | test_name_processor5', '88888884 | Intel | test_name_processor4',
                    '88888883 | Intel | test_name_processor3', '88888882 | Intel | test_name_processor2',
                    '88888881 | Intel | test_name_processor1']

        self.assertEqual(first_page_cpus, test_obj)

    def test_catalog_queryset_videocards(self):  # тест первой страницы (5 элементов) каталога (videocard)
        self.response = self.client.get(reverse('products:catalog_category', kwargs={'category_id': 2}))

        first_page_videocards = [str(x) for x in self.response.context_data['page_obj']]
        test_obj = ['77777775 | ASRock | test_name_videocard5', '77777774 | ASRock | test_name_videocard4',
                    '77777773 | ASRock | test_name_videocard3', '77777772 | ASRock | test_name_videocard2',
                    '77777771 | ASRock | test_name_videocard1']

        self.assertEqual(first_page_videocards, test_obj)

    def test_catalog_queryset_motherboards(self):  # тест первой страницы (5 элементов) каталога (motherboard)
        self.response = self.client.get(reverse('products:catalog_category', kwargs={'category_id': 3}))

        first_page_motherboards = [str(x) for x in self.response.context_data['page_obj']]
        test_obj = ['66666665 | MSI | test_name_motherboard5', '66666664 | MSI | test_name_motherboard4',
                    '66666663 | MSI | test_name_motherboard3', '66666662 | MSI | test_name_motherboard2',
                    '66666661 | MSI | test_name_motherboard1']

        self.assertEqual(first_page_motherboards, test_obj)

    def test_catalog_queryset_rams(self):  # тест первой страницы (5 элементов) каталога (ram)
        self.response = self.client.get(reverse('products:catalog_category', kwargs={'category_id': 4}))

        first_page_rams = [str(x) for x in self.response.context_data['page_obj']]
        test_obj = ['99999995 | Kingston | test_name_ram5', '99999994 | Kingston | test_name_ram4',
                    '99999993 | Kingston | test_name_ram3', '99999992 | Kingston | test_name_ram2',
                    '99999991 | Kingston | test_name_ram1']

        self.assertEqual(first_page_rams, test_obj)

    '''catalog_category_brand'''

    def test_catalog_brand_queryset(self):
        self.response = self.client.get(
            reverse('products:catalog_category_brand', kwargs={'category_id': 1, 'brand_name': 'Intel'})
        )

        first_page_processors = [str(x) for x in self.response.context_data['page_obj']]
        test_obj = ['88888885 | Intel | test_name_processor5', '88888884 | Intel | test_name_processor4',
                    '88888883 | Intel | test_name_processor3', '88888882 | Intel | test_name_processor2',
                    '88888881 | Intel | test_name_processor1']

        self.assertEqual(first_page_processors, test_obj)

    '''catalog_category_brand_line'''

    def test_catalog_brand_line_queryset(self):
        self.response = self.client.get(
            reverse('products:catalog_category_brand_line',
                    kwargs={'category_id': 1, 'brand_name': 'Intel', 'line_name': 'Test line'})
        )

        first_page_processors = [str(x) for x in self.response.context_data['page_obj']]
        test_obj = ['88888885 | Intel | test_name_processor5', '88888884 | Intel | test_name_processor4',
                    '88888883 | Intel | test_name_processor3', '88888882 | Intel | test_name_processor2',
                    '88888881 | Intel | test_name_processor1']

        self.assertEqual(first_page_processors, test_obj)
