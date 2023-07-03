from django.contrib import admin

# Register your models here.
from reviews_app.models import ProductReview, AvgReview

admin.site.register(ProductReview)
admin.site.register(AvgReview)
