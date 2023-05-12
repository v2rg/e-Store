from django.urls import path

from basket_app import views

app_name = 'basket'

urlpatterns = [
    path('', views.basket, name='basket'),
    path('basket_add/<int:category_id>/<int:product_sku>/', views.basket_add, name='basket_add'),
    path('basket_remove/<int:product_sku>/', views.basket_remove, name='basket_remove'),

]
