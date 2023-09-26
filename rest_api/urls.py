from django.urls import path

from rest_api import views

app_name = 'api'

urlpatterns = [
    path('test/', views.TestAPIView.as_view(), name='test'),
    path('random-list/', views.index_random_api, name='random_list'),  # 1-3 queries
    path('random-list2/', views.IndexRandomAPIList.as_view(), name='random_list'),  # 1-3 queries
    path('processor-list/', views.ProcessorListAPIView.as_view(), name='processor_list'),  # 2-4 queries
    path('videocard-list/', views.VideocardListAPIView.as_view(), name='videocard_list'),
    path('motherboard-list/', views.MotherboardListAPIView.as_view(), name='motherboard_list'),
    path('memory-list/', views.MemoryListAPIView.as_view(), name='memory_list'),
    path('product/<int:sku>/', views.product_api, name='product'),

]
