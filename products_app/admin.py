from django.contrib import admin

# Register your models here.
from products_app.models import (Category, Brand, Socket, MemoryType, GpuPciVersion, GpuModel, CpuLine, MbChipset,
                                 MbFormFactor, ProductImage, ProcessorList, VideoCardList, MotherboardList, MemoryList)

admin.site.register(Category)
admin.site.register(Brand)
admin.site.register(Socket)
admin.site.register(MemoryType)
admin.site.register(GpuPciVersion)
admin.site.register(GpuModel)
admin.site.register(CpuLine)
admin.site.register(MbChipset)
admin.site.register(MbFormFactor)

admin.site.register(ProductImage)

admin.site.register(ProcessorList)
admin.site.register(VideoCardList)
admin.site.register(MotherboardList)
admin.site.register(MemoryList)
