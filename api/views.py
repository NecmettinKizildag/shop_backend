from django.shortcuts import get_object_or_404
from api.serializers import (
    ProductSerializer, 
    OrderSerializer, 
    OrderItemSerializer, 
    ProductInfoSerializer,
    OrderCreateSerializer,
    UserSerializer,
    FilesSerializer,
    UserRegisterSerializer
    )
from api.models import (
    Product,
    Order, 
    OrderItem, 
    User,
    Files
    )
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.db.models import Max
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.views import APIView
from .filters import ProductFilter, InStockFilterBackend, OrderFilter
from rest_framework import filters 
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination
from rest_framework import viewsets
from rest_framework.decorators import action
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie, vary_on_headers
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.exceptions import ValidationError

"""
@api_view(['GET'])
def product_list(request):
    products = Product.objects.all()
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)

"""
class ProductAPIView(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing product instances.
    """
    #throttle_scope = 'products'
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filterset_class = ProductFilter
    filter_backends = [
        DjangoFilterBackend, 
        filters.SearchFilter,
        filters.OrderingFilter,
        InStockFilterBackend
    ]
    search_fields = ['name', 'description']  # if there is "=" symbol before search fields, only exact match will be used
    ordering_fields = ['name', 'price', 'stock']
    
    pagination_class = None  # Disable pagination for this viewset

    def get_permissions(self):
        self.permission_classes = [AllowAny]
        if self.request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            self.permission_classes = [IsAdminUser]
        return super().get_permissions()

class ProductListCreateAPIView(generics.ListCreateAPIView):
    #throttle_scope = 'products'
    queryset = Product.objects.all()
    serializer_class = ProductSerializer    
    filterset_class = ProductFilter
    filter_backends = [
        DjangoFilterBackend, 
        filters.SearchFilter,
        filters.OrderingFilter,
        InStockFilterBackend
    ]
    search_fields = ['name', 'description'] # if there is "=" symbol before search fields, only exact match will be used
    ordering_fields = ['name', 'price','stock']

    pagination_class = None
    """
    pagination_class.page_size = 5 
    pagination_class.page_query_param = 'pagenum'  # allow you to use ?pagenum=1, ?pagenum=2, etc.
    pagination_class.page_size_query_param = 'pagesize'  # allow you to use ?pagesize=10, ?pagesize=20, etc.
    pagination_class.max_page_size = 100  # maximum number of items per page
    """
    def get_permissions(self):
        self.permission_classes = [AllowAny]
        if self.request.method == 'POST':
            self.permission_classes = [IsAdminUser]
        return super().get_permissions() 
    """
    @method_decorator(cache_page(60 * 15, key_prefix='product_list'))
    def list(self, request, *args, **kwargs):
        
        # Cache the product list for 15 minutes.
        
        return super().list(request, *args, **kwargs)
    
    def get_queryset(self):
        
        #O verride the default queryset to apply the filter.
        
        import time
        time.sleep(2)  # Simulate a slow database query
        return super().get_queryset()  # This will apply the filter defined in the filterset
    """
"""
@api_view(['GET'])
def product_detail(request,pk):
    product = get_object_or_404(Product, pk=pk)
    serializer = ProductSerializer(product)
    return Response(serializer.data)
"""

class ProductDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    def get_permissions(self):
        self.permission_classes = [AllowAny]
        if self.request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            self.permission_classes = [IsAdminUser]
        return super().get_permissions() 
"""
@api_view(['GET'])
def order_list(request):
    orders = Order.objects.prefetch_related('items__product').all()
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)
"""

"""
class OrderListAPIView(generics.ListAPIView):
    queryset = Order.objects.prefetch_related('items__product').all()
    serializer_class = OrderSerializer
"""
class OrderViewSet(viewsets.ModelViewSet):
    #throttle_scope = 'orders'
    queryset = Order.objects.prefetch_related('items__product').all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None  # Disable pagination for this viewset
    filter_backends = [DjangoFilterBackend]
    filterset_class = OrderFilter

    def perform_create(self, serializer):
        user = self.request.user

        if Order.objects.filter(user=user).count() > 0:
            raise ValidationError("You can only create one order at a time.")
        serializer.save(user=self.request.user) 
        #return super().perform_create(serializer)

    def get_serializer_class(self):
        if self.action == 'create':
            return OrderCreateSerializer
        elif self.action in ['retrieve', 'list']:
            return OrderSerializer
        elif self.action == 'update' or self.action == 'partial_update':
            return OrderCreateSerializer
        elif self.action == 'destroy':
            return OrderSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        qs =  super().get_queryset()
        if not self.request.user.is_staff:
            qs = qs.filter(user=self.request.user)
        return qs
    
    @action(detail=True, methods=['post'], url_path='purchase')
    def purchase_order(self, request, pk=None):
        order = self.get_object()

        # Kullanıcının kendisine ait mi?
        if order.user != request.user and not request.user.is_staff:
            return Response({'detail': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)

        # Zaten tamamlanmış mı?
        if order.status == Order.StatusChoices.COMPLETED:
            raise ValidationError("This order has already been purchased.")

        # Siparişi satın alınmış olarak işaretle
        order.status = Order.StatusChoices.COMPLETED
        order.save()

        return Response({'detail': 'Order purchased successfully.'})
    
    @action(detail=True, methods=['post'], url_path='cancel')
    def cancel_order(self, request, pk=None):
        order = self.get_object()

        # Kullanıcının kendisine ait mi?
        if order.user != request.user and not request.user.is_staff:
            return Response({'detail': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)

        # Zaten tamamlanmış mı?
        if order.status == Order.StatusChoices.CANCELLED:
            raise ValidationError("This order has already been canceled.")

        # Siparişi satın alınmış olarak işaretle
        order.status = Order.StatusChoices.CANCELLED
        order.save()
        order.delete()  # Optional: Delete the order if you want to remove it from the database

        return Response({'detail': 'Order cancelled successfully.'})

    @action(
            detail=False, 
            methods=['get'], 
            url_path='user-orders',
            )
    def user_orders(self, request):
        user = request.user
        orders = self.get_queryset().filter(user=user)
        serializer = self.get_serializer(orders, many=True)
        return Response(serializer.data)
    """
    @method_decorator(cache_page(60 * 15, key_prefix='order_list'))
    @method_decorator(vary_on_headers("Authorization"))
    def list(self, request, *args, **kwargs):
        
        # Cache the product list for 15 minutes.
        
        return super().list(request, *args, **kwargs)
"""
"""
class UserOrderListAPIView(generics.ListAPIView):
    queryset = Order.objects.prefetch_related('items__product').all()
    serializer_class = OrderSerializer
    permission_classes = [
        IsAuthenticated,
    ] 

    # dinamic filtering based on the user
    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()
        return qs.filter(user=user)
"""

"""
@api_view(['GET'])
def product_info(request):
    products = Product.objects.all()
    serializer = ProductInfoSerializer({
        'products': products,
        'count': len(products),
        'max_price': products.aggregate(max_price = Max('price'))['max_price']
    })

    return Response(serializer.data)
"""
class ProductInfoAPIView(APIView):

    def get(self, request):
        products = Product.objects.all()
        serializer = ProductInfoSerializer({
            'products': products,
            'count': len(products),
            'max_price': products.aggregate(max_price=Max('price'))['max_price']
        })
        return Response(serializer.data)
    

class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = None
    #permission_classes = [IsAdminUser]

class FileViewSet(viewsets.ModelViewSet):
    serializer_class = FilesSerializer
    parser_classes = [MultiPartParser, FormParser]
    pagination_class = None

    def get_queryset(self):
        return Files.objects.filter(product_id=self.kwargs['product_pk'])

    def perform_create(self, serializer):
        product_id = self.kwargs['product_pk']
        if product_id is None:
            raise ValidationError("Missing product ID in URL.")
        product = get_object_or_404(Product, pk=product_id)
        serializer.save(product=product)

    def get_permissions(self):
        self.permission_classes = [AllowAny]
        if self.request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            self.permission_classes = [IsAdminUser]
        return super().get_permissions()
    

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action == 'make_admin':
            permission_classes = [IsAdminUser]  
        elif self.request.method in ['GET', 'PUT', 'PATCH', 'DELETE']:
         permission_classes = [IsAdminUser]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def make_admin(self, request, pk=None):
        user = self.get_object()
        if user.is_staff:
            return Response({'status': 'user is already staff'})
        user.is_staff = True
        user.save()
        return Response({'status': 'user is now staff'})