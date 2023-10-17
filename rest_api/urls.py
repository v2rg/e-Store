from django.urls import path, include
from rest_framework import routers

from rest_api import views
from rest_api.views import ProductUserReviewViewSet

app_name = 'api'

router = routers.SimpleRouter()
router.register(r'product-review', ProductUserReviewViewSet, basename='queryset')

urlpatterns = [
    path('test/', views.TestAPIView.as_view(), name='test'),

    path('random-list/', views.index_random_api, name='random_list'),  # 1-3 queries
    path('random-list2/', views.IndexRandomAPIList.as_view(), name='random_list'),  # 1-3 queries
    path('processor-list/', views.ProcessorListAPIView.as_view(), name='processor_list'),
    path('videocard-list/', views.VideocardListAPIView.as_view(), name='videocard_list'),
    path('motherboard-list/', views.MotherboardListAPIView.as_view(), name='motherboard_list'),
    path('memory-list/', views.MemoryListAPIView.as_view(), name='memory_list'),
    path('product/<int:sku>/', views.product_api, name='product'),
    path('product-reviews/<int:sku>/', views.ProductReviewsAPIView.as_view(), name='product_review'),
    path('', include(router.urls)),  # отзывы о товаре

    path('user-registration/', views.UserRegistrationAPI.as_view(), name='user_registration'),
    path('user-profile/', views.UserProfileAPI.as_view(), name='user_profile'),
    path('user-address/', views.UserAddressAPI.as_view(), name='user_address'),
    path('user-orders/', views.UserOrdersAPI.as_view(), name='user_orders'),
    path('user-order/<int:order_id>/', views.UserOrderAPI.as_view(), name='user_order'),

]
