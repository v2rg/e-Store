from django.urls import path

from products_app import views

app_name = 'products'

urlpatterns = [
    # path('', views.catalog, name='catalog'),
    path('', views.CatalogView.as_view(), name='catalog'),
    path('<int:category_id>/', views.CatalogView.as_view(), name='catalog_category'),
    path('<int:category_id>/<str:brand_name>/', views.CatalogView.as_view(), name='catalog_category_brand'),
    path('<int:category_id>/<str:brand_name>/<str:line_name>/', views.CatalogView.as_view(),
         name='catalog_category_brand_line'),

    path('<str:method>', views.sorting_method, name='sorting_method'),

    # path('product/<int:category_id>/<int:sku>/', views.product, name='product'),
    path('product/<int:category_id>/<int:sku>/', views.ProductView.as_view(), name='product'),

]
