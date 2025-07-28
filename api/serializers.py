from rest_framework import serializers
from .models import Product, Order, OrderItem,User, Files
from django.db import transaction

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    class Meta:
        model = User
        #exclude = ('password', 'last_login', 'is_active', 'date_joined')  # Exclude sensitive fields
        fields = ('id', 'username', 'email','password', 'is_staff', 'is_superuser','orders')
        #fields = '__all__' # if exclude is used, fields cannot be used together with it
        read_only_fields = ('id','is_staff', 'is_superuser','orders')

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email'),
            password=validated_data['password']
        )
        return user


class FilesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Files  
        fields = '__all__'  
        extra_kwargs = {
            'product': {'read_only': True}
        }


class ProductSerializer(serializers.ModelSerializer):
    files = FilesSerializer(many=True, read_only=True)
    class Meta:
        model = Product
        fields = (
            "id",
            'name',
            'description',
            'price',
            'stock',
            'files',
        )         

    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError("Price must be a positive number.")
        return value          

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name')
    product_price = serializers.DecimalField(max_digits=10, decimal_places=2, source='product.price')

    class Meta:
        model = OrderItem
        fields = (
            'product_name',
            'product_price',
            'quantity',
            'item_subtotal',
        ) 

class OrderCreateSerializer(serializers.ModelSerializer):
    class OrderItemCreateSerializer(serializers.ModelSerializer):
        class Meta:
            model = OrderItem
            fields = ('product', 'quantity')

    items = OrderItemCreateSerializer(many=True, required=False)

    def create(self, validated_data):
        order_item_data = validated_data.pop('items')

        with transaction.atomic():
            order = Order.objects.create(**validated_data)
            for item_data in order_item_data:
                OrderItem.objects.create(order=order, **item_data)
        return order
    
    def update(self, instance, validated_data):
        order_item_data = validated_data.pop('items')

        with transaction.atomic():
            instance = super().update(instance, validated_data)

            if order_item_data is not None:
                instance.items.all().delete()  # Clear existing items

                for item_data in order_item_data:
                    OrderItem.objects.create(order=instance, **item_data)
        return instance 

    class Meta:
        model = Order
        fields = (
            'order_id',
            'created_at',
            'user',
            'status',
            'items', 
            'total_price' 
        )
        read_only_fields = ('order_id', 'created_at', 'total_price')
        extra_kwargs = {
            'user': {'read_only': True},
        }

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField(method_name='total')

    def total(self, obj):
        order_items = obj.items.all()
        return sum(order_item.item_subtotal for order_item in order_items) 

    class Meta:
        model = Order
        fields = (
            'order_id',
            'created_at',
            'user',
            'status',
            'items', 
            'total_price'
        )                        

class ProductInfoSerializer(serializers.Serializer):
    # get all products, count of products, max price
 
    products = ProductSerializer(many=True)
    count = serializers.IntegerField()
    max_price = serializers.FloatField()


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, min_length=6)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email'),
            password=validated_data['password']
        )
        return user