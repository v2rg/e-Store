from django.urls import path

from products_app import views

app_name = 'products'

urlpatterns = [
    path('', views.index, name='index'),

    path('catalog/', views.catalog, name='catalog'),
    path('catalog/<int:category_id>/', views.catalog, name='catalog_category'),
    path('catalog/<int:category_id>/<str:brand_name>/', views.catalog, name='catalog_category_brand'),
    path('catalog/<int:category_id>/<str:brand_name>/<str:line_name>/', views.catalog,
         name='catalog_category_brand_line'),

    path('product/<int:sku>/', views.product, name='product'),

]
