import django_filters
from api.models import Product, Order
from rest_framework import filters

class ProductFilter(django_filters.FilterSet):
    class Meta:
        model = Product
        fields = {
            'name': ['iexact', 'icontains'], # iexact: case-insensitive exact match, icontains: case-insensitive contains
            'price': ['exact', 'lt', 'gt','range'], #lt: less than, gt: greater than, lte: less than or equal to, gte: greater than or equal to, 
        }


class InStockFilterBackend(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view): 
        return queryset.filter(stock__gt=0)
    
class OrderFilter(django_filters.FilterSet):
    created_at = django_filters.DateTimeFilter(field_name='created_at__date')
    class Meta:
        model = Order
        fields = {
            'status': ['iexact'],  # contains: case-insensitive partial match, exact: exact match
            'created_at': ['exact', 'lt', 'gt'], 
        }