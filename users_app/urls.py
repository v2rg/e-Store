from django.urls import path

from users_app import views

app_name = 'users'

urlpatterns = [
    path('login/', views.login, name='login'),

]
