from django.urls import path

from products_app import views

app_name = 'products'

urlpatterns = [
    path('', views.index, name='index'),
    path('catalog/', views.catalog, name='catalog'),

]
