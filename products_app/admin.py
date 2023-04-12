from django.contrib import admin

# Register your models here.
from products_app import models

admin.site.register(models.Brand)
admin.site.register(models.Socket)
admin.site.register(models.MemoryType)
admin.site.register(models.PciVersion)

admin.site.register(models.ProductImage)

admin.site.register(models.Processor)
admin.site.register(models.Motherboard)
admin.site.register(models.VideoCard)
admin.site.register(models.Memory)
