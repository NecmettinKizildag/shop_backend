from django.test import TestCase
from api.models import User, Product, Order, OrderItem
from django.urls import reverse
from rest_framework import status

# Create your tests here.
class UserOrderTestCase(TestCase):
    def setUp(self):
        user1 = User.objects.create_user(username='user1', password='password123')
        user2 = User.objects.create_user(username='user2', password='password123')
        Order.objects.create(user=user1, status=Order.StatusChoices.PENDING, total_price=100.00)
        Order.objects.create(user=user2, status=Order.StatusChoices.COMPLETED, total_price=200.00)
        Order.objects.create(user=user1, status=Order.StatusChoices.CANCELLED, total_price=50.00)       
        Order.objects.create(user=user2, status=Order.StatusChoices.CONFIRMED, total_price=150.00)

    def test_user_order_endpoint_retrivies_only_authentcated_user_orders(self):
        user = User.objects.get(username='user2')
        self.client.force_login(user)
        response = self.client.get(reverse('user_orders'))

        assert response.status_code == status.HTTP_200_OK
        orders = response.json()
        print(orders)

        assert len(orders) == 2  

        self.assertTrue(all(order['user'] == user.id for order in orders))  # all orders should belong to user2
        # usttekinin aynisi
        for order in orders:
            assert order['user'] == user.id

    def test_user_order_list_authenticated(self):
        response = self.client.get(reverse('user_orders'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)  
