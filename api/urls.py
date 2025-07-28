from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter



router = DefaultRouter()
router.register(r'orders', views.OrderViewSet, basename='order')
router.register(r'products', views.ProductAPIView, basename='products')
router.register(r'users', views.UserViewSet, basename='user')

product_files_router = NestedDefaultRouter(router, r'products', lookup='product')
product_files_router.register(r'files', views.FileViewSet, basename='product-files')



urlpatterns = [
    #path('products/', views.ProductListCreateAPIView.as_view(), name='product_list'),
    #path('products/info/', views.ProductInfoAPIView.as_view(), name='product_info'),
    #path('products/<int:pk>/', views.ProductDetailAPIView.as_view(), name='product_detail'),
    #path('users/', views.UserListView.as_view(), name='user_list'),

    path('', include(router.urls)),
    path('', include(product_files_router.urls)),
]

