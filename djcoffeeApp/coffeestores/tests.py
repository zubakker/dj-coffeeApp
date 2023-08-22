from rest_framework.test import APITestCase
from django.urls import reverse

from coffeestores import models, serializers


class CoffeeShopViewSetTestCase(APITestCase):
    def setUp(self):
        shop_one = models.CoffeeShop(name='test1',
                                     address='test_addr1')
        shop_one.save()
        shop_two = models.CoffeeShop(name='test2',
                                     address='test_addr2')
        shop_two.save()
        shop_thr = models.CoffeeShop(name='test3',
                                     address='test_addr1')
        shop_thr.save()

        drink_one = models.CoffeeDrink(name='test1',
                                       price='99.99',
                                       volume=300)
        drink_one.shop = shop_one
        drink_one.save()
        drink_two = models.CoffeeDrink(name='test2',
                                       price='19.99',
                                       volume=100)
        drink_two.shop = shop_one
        drink_two.save()


    def test_coffeeshop_list(self):
        url = reverse('shops')

        # Test resulting parameters
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 3)

        results = response.data['results']
        assert 'id' in list(results[0])
        assert 'name' in list(results[0])
        assert 'address' in list(results[0])
        assert 'drinks' in list(results[0])

        # --- Test filtering: ---
        # Invalid name
        query = {'name': 'test1111'}
        response = self.client.get(url, query, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 0)

        # One parameter
        query = {'name': 'test1'}
        response = self.client.get(url, query, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)

        # Two parameters
        query = {'name': 'test1', 
                 'address': 'test_addr1'}
        response = self.client.get(url, query, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)

        query = {'name': 'test1', 
                 'address': 'test_addr2'}
        response = self.client.get(url, query, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 0)

        # Test ordering
        query = {'ordering': '-name'}
        response = self.client.get(url, query, format='json')
        self.assertEqual(response.status_code, 200)
        results = response.data['results']
        self.assertEqual(results[0]['name'], 'test3')

        # Test combination
        query = {'address': 'test_addr1',
                 'ordering': '-name'}
        response = self.client.get(url, query, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 2)
        results = response.data['results']
        self.assertEqual(results[0]['name'], 'test3')

    def test_coffeeshop_one_shop(self):
        url = reverse('shops')

        # Id not a number
        query = {'id': 'test'}
        response = self.client.get(url, query, format='json')
        self.assertEqual(response.status_code, 400)

        # Invalid shop id
        query = {'id': 1111}
        response = self.client.get(url, query, format='json')
        self.assertEqual(response.status_code, 404)

        # A shop without drinks
        query = {'id': 2}
        response = self.client.get(url, query, format='json')
        self.assertEqual(response.status_code, 200)
        data_list = list(response.data)
        assert 'id' in data_list
        assert 'name' in data_list
        assert 'address' in data_list
        assert 'drinks' in data_list
        self.assertEqual(response.data['name'], 'test2')

        # A shop with drinks
        query = {'id': 1}
        response = self.client.get(url, query, format='json')
        self.assertEqual(response.status_code, 200)
        drinks = response.data['drinks']
        self.assertEqual(len(response.data['drinks']), 2)
        assert 'name' in list(drinks[0])
        assert 'price' in list(drinks[0])
        assert 'volume' in list(drinks[0])
        self.assertEqual(drinks[0]['name'], 'test1')
        self.assertEqual(drinks[0]['price'], '99.99')
        self.assertEqual(drinks[0]['volume'], 300)

        
class AuthViewSetTestCase(APITestCase):
    def register(self):
        url = reverse('auth-register')
        query = {'username': 'test',
                 'password': 'test'}
        response = self.client.post(url, query, format='json')

    def test_register(self):
        url = reverse('auth-register')

        # Empty request
        response = self.client.post(url, format='json')
        self.assertEqual(response.status_code, 400)
        # No username
        query = {'password': 'test'}
        response = self.client.post(url, query, format='json')
        self.assertEqual(response.status_code, 400)
        # No password
        query = {'username': 'test'}
        response = self.client.post(url, query, format='json')
        self.assertEqual(response.status_code, 400)
        # Successful request
        query = {'username': 'test',
                 'password': 'test'}
        response = self.client.post(url, query, format='json')
        self.assertEqual(response.status_code, 201)
        assert 'refresh' in list(response.data)
        assert 'access' in list(response.data)

        # User already exists
        query = {'username': 'test',
                 'password': 'test'}
        response = self.client.post(url, query, format='json')
        self.assertEqual(response.status_code, 400)

    def test_login(self):
        self.register()
        url = reverse('auth-login')

        # No query provided
        response = self.client.post(url, format='json')
        self.assertEqual(response.status_code, 400)
        # No password provided
        query = {'username': 'test'}
        response = self.client.post(url, query, format='json')
        self.assertEqual(response.status_code, 400)
        # User doesn't exist
        query = {'username': 'test1',
                 'password': 'test1'}
        response = self.client.post(url, query, format='json')
        self.assertEqual(response.status_code, 404)
        # Wrong password
        query = {'username': 'test',
                 'password': 'test1'}
        response = self.client.post(url, query, format='json')
        self.assertEqual(response.status_code, 401)

        # Successful login
        query = {'username': 'test',
                 'password': 'test'}
        response = self.client.post(url, query, format='json')
        self.assertEqual(response.status_code, 200)
        assert 'refresh' in list(response.data)
        assert 'access' in list(response.data)





