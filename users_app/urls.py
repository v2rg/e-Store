from django.urls import path

from users_app import views

app_name = 'users'

urlpatterns = [
    path('login/', views.login, name='login'),
    path('registration/', views.registration, name='registration'),
    path('verify/<str:username>/<uuid:user_uuid>/', views.verify_email, name='verify_email'),
    path('logout/', views.logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('orders/', views.orders, name='orders'),
    path('order/<int:order_id>/', views.order, name='order')

]
