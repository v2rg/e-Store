from django.db import models

# Create your models here.

"""Параметры товаров"""


class AbstractDescription(models.Model):  # АБСТРАКТНЫЙ класс для параметров
    description = models.TextField(blank=True, verbose_name='Описание')

    class Meta:
        abstract = True


class Category(AbstractDescription):  # категории товара

    """
    Процессоры, Видеокарты, Материнские платы, Оперативная память
    """

    category_name = models.CharField(max_length=50, unique=True, verbose_name='Категория')
    category_name_eng = models.CharField(max_length=50, unique=True, verbose_name='Категория на англ. языке')

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return f'{self.id} | {self.category_name}'


class Brand(AbstractDescription):  # бренды
    category = models.ManyToManyField(to=Category, verbose_name='Категории')
    brand_name = models.CharField(max_length=128, unique=True, verbose_name='Название бренда')

    class Meta:
        ordering = ['brand_name']
        verbose_name = 'бренд'
        verbose_name_plural = 'Бренды'

    def __str__(self):
        # return f'{self.brand_name} | ___ | {[cat.category_name for cat in self.category.all()]}'
        return self.brand_name


class Socket(AbstractDescription):  # сокеты

    """
    Intel LGA 1200, LGA 1700
    AMD AM4, AM5
    """

    brand_name = models.ForeignKey(to=Brand, on_delete=models.CASCADE, verbose_name='Бренд')
    socket_name = models.CharField(max_length=64, unique=True, verbose_name='Тип сокета')

    class Meta:
        ordering = ['socket_name']
        verbose_name = 'сокет'
        verbose_name_plural = 'CPU Сокеты'

    def __str__(self):
        return self.socket_name


class MemoryType(AbstractDescription):  # тип оперативной памяти

    """
    DDR4, DDR5
    """

    type_name = models.CharField(max_length=10, unique=True, verbose_name='Тип памяти')

    class Meta:
        ordering = ['type_name']
        verbose_name = 'тип памяти'
        verbose_name_plural = 'RAM Тип памяти'

    def __str__(self):
        return self.type_name


class GpuPciVersion(AbstractDescription):  # версия PCI

    """
    PCI-E 3.0, PCI-E 4.0
    """

    version_name = models.CharField(max_length=10, unique=True, verbose_name='Версия PCI')

    class Meta:
        ordering = ['version_name']
        verbose_name = 'версия PCI'
        verbose_name_plural = 'GPU Версии PCI'

    def __str__(self):
        return self.version_name


class GpuModel(AbstractDescription):  # модель GPU
    """
    GeForce RTX 4090, RTX 4080, RTX 3080ti, RTX 3070
    Radeon RX 7900 XTX, RX 7900 XT, RX 6950 XT, RX 6900 XT
    """
    gpu_brand = models.ForeignKey(to=Brand, on_delete=models.CASCADE, verbose_name='Бренд GPU')
    gpu_name = models.CharField(max_length=50, unique=True, verbose_name='Модель GPU')

    class Meta:
        ordering = ['gpu_name']
        verbose_name = 'модель GPU'
        verbose_name_plural = 'GPU Модели GPU'

    def __str__(self):
        return self.gpu_name


class CpuLine(AbstractDescription):  # линейка процессоров

    """
    Intel Core i9, Core i7, Core i5, Core i3
    AMD Ryzen 9, Ryzen 7, Ryzen 5, Ryzen 3
    """
    cpu_brand = models.ForeignKey(to=Brand, on_delete=models.CASCADE, verbose_name='Бренд CPU')
    line_name = models.CharField(max_length=50, verbose_name='Линейка процессора')

    class Meta:
        ordering = ['line_name']
        verbose_name = 'линейка CPU'
        verbose_name_plural = 'CPU Линейки CPU'

    def __str__(self):
        return self.line_name


class MbFormFactor(AbstractDescription):  # форм-фактор материнской платы
    """
    E-ATX, XL-ATX, Standard-ATX
    """

    formfactor_name = models.CharField(max_length=50, unique=True, verbose_name='Форм-фактор')

    class Meta:
        verbose_name = 'форм-фактор мат. платы'
        verbose_name_plural = 'MB Форм-фактор мат.платы'

    def __str__(self):
        return self.formfactor_name


class MbChipset(AbstractDescription):  # чипсет материнской платы
    """
    INTEL Z790, Z690, B760, H670
    AMD X670, X570, B650, A520
    """

    chipset_name = models.CharField(max_length=50, unique=True, verbose_name='Чипсет')

    class Meta:
        ordering = ['chipset_name']
        verbose_name = 'чипсет мат. платы'
        verbose_name_plural = 'MB Чипсеты мат. плат'

    def __str__(self):
        return self.chipset_name


"""Изображения товара"""


def user_directory_path(instance, image):  # динамический путь до изображения товара (category, sku)
    return f'products_images/{instance.category.category_name_eng}/{instance.sku}/{image}'


class ProductImage(models.Model):  # изображение товара
    sku = models.CharField(max_length=50, db_index=True, verbose_name='Артикул')
    category = models.ForeignKey(to=Category, on_delete=models.CASCADE, verbose_name='Категория товара')
    carousel_id = models.PositiveSmallIntegerField(verbose_name='ID для карусели')
    image = models.ImageField(upload_to=user_directory_path, verbose_name='Изображение товара')

    class Meta:
        ordering = ['category', 'sku', 'carousel_id']
        verbose_name = 'изображение товара'
        verbose_name_plural = 'Изображения товаров'

    def __str__(self):
        return f'{self.sku} | {self.carousel_id} | {self.image}'


"""Товары"""


class AbstractProduct(models.Model):  # АБСТРАКТНЫЙ класс товара
    sku = models.PositiveIntegerField(unique=True, verbose_name='Артикул')
    category = models.ForeignKey(to=Category, on_delete=models.CASCADE, verbose_name='Категория')
    brand = models.ForeignKey(to=Brand, on_delete=models.CASCADE, verbose_name='Бренд')
    name = models.CharField(max_length=128, unique=True, verbose_name='Наименование товара')
    description = models.TextField(verbose_name='Описание товара')
    short_description = models.CharField(max_length=256, verbose_name='Краткое описание товара (256 символов)')
    thumbnail = models.ImageField(upload_to=user_directory_path, max_length=200, null=True,
                                  verbose_name='Превью на карточку товара')
    price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='Цена')
    quantity = models.PositiveSmallIntegerField(default=0, verbose_name='Количество')
    date_added = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')

    class Meta:
        abstract = True


class ProcessorList(AbstractProduct):  # процессоры
    line = models.ForeignKey(to=CpuLine, on_delete=models.CASCADE, verbose_name='Линейка процессора')
    socket = models.ForeignKey(to=Socket, on_delete=models.CASCADE, verbose_name='Сокет')
    cores = models.PositiveSmallIntegerField(verbose_name='Количество ядер')
    base_frequency = models.PositiveSmallIntegerField(verbose_name='Базовая частота процессора')
    max_frequency = models.PositiveSmallIntegerField(verbose_name='Максимальная частота процессора')
    memory_type = models.ForeignKey(to=MemoryType, on_delete=models.CASCADE, verbose_name='Тип памяти')
    tdp = models.PositiveSmallIntegerField(verbose_name='Тепловыделение')

    class Meta:
        ordering = ['-sku']
        verbose_name = 'процессор'
        verbose_name_plural = 'CAT Процессоры'

    def __str__(self):
        return f'{self.sku} | {self.brand} | {self.name}'


class MotherboardList(AbstractProduct):  # материнские платы
    socket = models.ForeignKey(to=Socket, on_delete=models.CASCADE, verbose_name='Сокет процессора')
    form_factor = models.ForeignKey(to=MbFormFactor, on_delete=models.CASCADE, verbose_name='Форм-фактор')
    chipset = models.ForeignKey(to=MbChipset, on_delete=models.CASCADE, verbose_name='Чипсет')
    memory_type = models.ForeignKey(to=MemoryType, on_delete=models.CASCADE, verbose_name='Тип памяти')
    memory_slots = models.PositiveSmallIntegerField(verbose_name='Количество слотов памяти')
    pci_version = models.ForeignKey(to=GpuPciVersion, on_delete=models.CASCADE, verbose_name='Версия PCI')

    class Meta:
        ordering = ['-sku']
        verbose_name = 'материнская плата'
        verbose_name_plural = 'CAT Материнские платы'

    def __str__(self):
        return f'{self.sku} | {self.brand} | {self.name}'


class VideoCardList(AbstractProduct):  # видеокарты
    gpu = models.ForeignKey(to=GpuModel, on_delete=models.CASCADE, verbose_name='Графический процессор')
    gpu_frequency = models.SmallIntegerField(verbose_name='Частота работы видеочипа')
    memory_size = models.SmallIntegerField(verbose_name='Объем видеопамяти')
    memory_frequency = models.SmallIntegerField(verbose_name='Частота работы памяти')
    pci_version = models.ForeignKey(to=GpuPciVersion, on_delete=models.CASCADE, verbose_name='Версия PCI')
    length = models.SmallIntegerField(verbose_name='Длина видеокарты')

    class Meta:
        ordering = ['-sku']
        verbose_name = 'видеокарта'
        verbose_name_plural = 'CAT Видеокарты'

    def __str__(self):
        return f'{self.sku} | {self.brand} | {self.name}'


class MemoryList(AbstractProduct):  # оперативная память
    type = models.ForeignKey(to=MemoryType, on_delete=models.CASCADE, verbose_name='Тип памяти')
    size = models.PositiveSmallIntegerField(verbose_name='Объем памяти')
    frequency = models.PositiveSmallIntegerField(verbose_name='Тактовая частота')

    class Meta:
        ordering = ['-sku']
        verbose_name = 'оперативная память'
        verbose_name_plural = 'CAT Оперативная память'

    def __str__(self):
        return f'{self.sku} | {self.brand} | {self.name}'
