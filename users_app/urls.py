from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LogoutView
from django.urls import path

from users_app import views

app_name = 'users'

urlpatterns = [
    # path('login/', views.login, name='login'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('registration/', views.UserRegistrationView.as_view(), name='registration'),
    path('verify/<str:username>/<uuid:user_uuid>/', views.verify_email, name='verify_email'),
    path('logout/', login_required(LogoutView.as_view()), name='logout'),
    path('profile/', views.profile, name='profile'),
    path('orders/', login_required(views.OrdersView.as_view()), name='orders'),
    path('order/<int:order_id>/', views.order, name='order')

]
