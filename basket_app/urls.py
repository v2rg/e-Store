from django.urls import path

from basket_app import views

app_name = 'basket'

urlpatterns = [
    path('', views.basket, name='basket'),
    path('add/<int:category_id>/<int:product_sku>/', views.basket_add, name='basket_add'),
    path('remove/<int:product_sku>/', views.basket_remove, name='basket_remove'),
    path('update/<int:product_sku>/<slug:slug>/', views.basket_update, name='basket_update'),
    path('confirmation/', views.order_confirmation, name='order_confirmation'),

]
