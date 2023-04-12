from django.db import models


# Create your models here.

class Brand(models.Model):  # таблица брендов
    brand = models.CharField(max_length=128, unique=True, verbose_name='Название бренда')
    description = models.TextField(blank=True, verbose_name='Описание бренда')

    class Meta:
        ordering = ['brand']

    def __str__(self):
        return self.brand


class Socket(models.Model):  # таблица сокетов
    socket = models.CharField(max_length=64, unique=True, verbose_name='Тип сокета')
    description = models.TextField(blank=True, verbose_name='Описание сокета')

    def __str__(self):
        return self.socket


class MemoryType(models.Model):
    type = models.CharField(max_length=10, unique=True, verbose_name='Тип памяти')
    description = models.TextField(blank=True, verbose_name='Описание')

    def __str__(self):
        return self.type


class PciVersion(models.Model):
    version = models.CharField(max_length=10, unique=True, verbose_name='Версия PCI')
    description = models.TextField(blank=True, verbose_name='Описание')

    def __str__(self):
        return self.version


def user_directory_path(instance, image):  # динамический путь до изображения товара (в папку sku)
    return f'products_images/{instance.sku}/{image}'


class ProductImage(models.Model):  # таблица с изображениями товара
    sku = models.CharField(max_length=50, db_index=True, verbose_name='Артикул')
    image = models.ImageField(upload_to=user_directory_path, verbose_name='Изображение товара')

    def __str__(self):
        return f'{self.sku} | {self.image}'


class Product(models.Model):  # абстрактный класс товара
    CATEGORIES = [
        ('1', 'Процессоры'), ('2', 'Видеокарты'),
        ('3', 'Материнские платы'), ('4', 'Оперативная память')
    ]

    sku = models.PositiveIntegerField(unique=True, db_index=True, verbose_name='Артикул')
    category = models.CharField(max_length=100, choices=CATEGORIES, verbose_name='Категория')
    brand = models.ForeignKey(to=Brand, on_delete=models.CASCADE, verbose_name='Бренд')
    name = models.CharField(max_length=128, unique=True, verbose_name='Наименование товара')
    description = models.TextField(verbose_name='Описание товара')
    short_description = models.CharField(max_length=256, verbose_name='Краткое описание товара (256 символов)')
    # image в отдельной таблице
    price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='Цена')
    quantity = models.PositiveSmallIntegerField(default=0, verbose_name='Количество')

    class Meta:
        abstract = True


class Processor(Product):
    socket = models.ForeignKey(to=Socket, on_delete=models.CASCADE, verbose_name='Сокет')
    cores = models.PositiveSmallIntegerField(verbose_name='Количество ядер')
    base_frequency = models.PositiveSmallIntegerField(verbose_name='Базовая частота процессора')
    max_frequency = models.PositiveSmallIntegerField(verbose_name='Максимальная частота процессора')
    memory_type = models.ForeignKey(to=MemoryType, on_delete=models.CASCADE, verbose_name='Тип памяти')
    tdp = models.PositiveSmallIntegerField(verbose_name='Тепловыделение')

    def __str__(self):
        return f'{self.sku} | {self.brand} | {self.name}'


class Motherboard(Product):
    FORM_FACTOR = [
        ('E-ATX', 'E-ATX'), ('XL-ATX', 'XL-ATX'),
        ('Standard-ATX', 'Standard-ATX')
    ]

    CHIPSET = [
        (
            'Intel',
            (
                ('Z790', 'Z790'), ('Z690', 'Z690'),
                ('B760', 'B760'), ('H670', 'H670'))
        ),
        (
            'AMD',
            (
                ('X670', 'X670'), ('X570', 'X570'),
                ('B650', 'B650'), ('A520', 'A520'))
        )
    ]

    socket = models.ForeignKey(to=Socket, on_delete=models.CASCADE, verbose_name='Сокет процессора')
    form_factor = models.CharField(max_length=50, choices=FORM_FACTOR, verbose_name='Форм-фактор')
    chipset = models.CharField(max_length=10, choices=CHIPSET, verbose_name='Чипсет')
    memory_type = models.ForeignKey(to=MemoryType, on_delete=models.CASCADE, verbose_name='Тип памяти')
    memory_slots = models.PositiveSmallIntegerField(verbose_name='Количество слотов памяти')
    pci_version = models.ForeignKey(to=PciVersion, on_delete=models.CASCADE, verbose_name='Версия PCI')

    def __str__(self):
        return f'{self.sku} | {self.brand} | {self.name}'


class VideoCard(Product):
    GPU = [
        (
            'GeForce',
            (
                ('4090', 'RTX 4090'), ('4080', 'RTX 4080'),
                ('3080ti', 'RTX 3080ti'), ('3070ti', 'RTX 3070'),
            )
        ),
        (
            'Radeon',
            (
                ('7900XTX', 'RX 7900 XTX'), ('7900XT', 'RX 7900 XT'),
                ('6950XT', 'RX 6950 XT'), ('6900XT', 'RX 6900 XT'),
            )
        )
    ]

    gpu = models.CharField(max_length=128, choices=GPU, verbose_name='Графический процессор')
    gpu_frequency = models.SmallIntegerField(verbose_name='Частота работы видеочипа')
    memory_size = models.SmallIntegerField(verbose_name='Объем видеопамяти')
    memory_frequency = models.SmallIntegerField(verbose_name='Частота работы памяти')
    pci_version = models.ForeignKey(to=PciVersion, on_delete=models.CASCADE, verbose_name='Версия PCI')
    length = models.SmallIntegerField(verbose_name='Длина видеокарты')

    def __str__(self):
        return f'{self.sku} | {self.brand} | {self.name}'


class Memory(Product):
    type = models.ForeignKey(to=MemoryType, on_delete=models.CASCADE, verbose_name='Тип памяти')
    size = models.PositiveSmallIntegerField(verbose_name='Объем памяти')
    frequency = models.PositiveSmallIntegerField(verbose_name='Тактовая частота')

    class Meta:
        verbose_name_plural = 'Memory'

    def __str__(self):
        return f'{self.sku} | {self.brand} | {self.name}'
