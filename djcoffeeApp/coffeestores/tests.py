from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth.models import Group

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

    def register_shopowner(self):
        owner_group = Group(name='shop owner')
        owner_group.save()
        url = reverse('auth-register')
        data = {'username': 'test',
                 'password': 'test'}
        response = self.client.post(url, data, format='json')
        self.access = response.data['access']
        self.refresh = response.data['refresh']
        shop_owner = models.CoffeeDrinker.objects.get(username='test')
        shop_owner.save()
        shop_owner.groups.add(owner_group)
        shop_owner.save()

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

    def test_coffeeshop_create(self):
        url = reverse('shops')

        self.register_shopowner()

        # Not authorized
        response = self.client.post(url, format='json')
        self.assertEqual(response.status_code, 401)

        # Wrong token
        headers = {'Authorization': 'Bearer test'}
        response = self.client.post(url, headers=headers, format='json')
        self.assertEqual(response.status_code, 401)
        # No query
        headers = {'Authorization': 'Bearer ' + self.access}
        response = self.client.post(url, headers=headers, format='json')
        self.assertEqual(response.status_code, 400)
        # Invalid query
        headers = {'Authorization': 'Bearer ' + self.access}
        query = {'test': 'test'}
        response = self.client.post(url, query, headers=headers, format='json')
        self.assertEqual(response.status_code, 400)
        # Successful request
        query = {'name': 'test',
                 'address': 'test1'}
        headers = {'Authorization': 'Bearer ' + self.access}
        response = self.client.post(url, query, headers=headers, format='json')
        self.assertEqual(response.status_code, 201)
        data = response.data
        assert 'id' in list(data)
        assert 'name' in list(data)
        assert 'address' in list(data)
        self.assertEqual(data['name'], 'test')
        self.assertEqual(data['address'], 'test1')

    def test_coffeeshop_update(self):
        url = reverse('shops')

        self.register_shopowner()

        # Not authorized
        response = self.client.put(url, format='json')
        self.assertEqual(response.status_code, 401)

        # Wrong token
        headers = {'Authorization': 'Bearer test'}
        response = self.client.put(url, headers=headers, format='json')
        self.assertEqual(response.status_code, 401)
        # No query
        headers = {'Authorization': 'Bearer ' + self.access}
        response = self.client.put(url, headers=headers, format='json')
        self.assertEqual(response.status_code, 400)
        # Invalid query
        headers = {'Authorization': 'Bearer ' + self.access}
        query = {'test': 'test'}
        response = self.client.put(url, query, headers=headers, format='json')
        self.assertEqual(response.status_code, 400)
        # Invalid id
        headers = {'Authorization': 'Bearer ' + self.access}
        query = {'id': 111}
        response = self.client.put(url, query, headers=headers, format='json')
        self.assertEqual(response.status_code, 404)
        # Invalid id type
        headers = {'Authorization': 'Bearer ' + self.access}
        query = {'id': 'test'}
        response = self.client.put(url, query, headers=headers, format='json')
        self.assertEqual(response.status_code, 400)
        # Successful request
        headers = {'Authorization': 'Bearer ' + self.access}
        query = {'id': 1,
                 'name': 'test11',
                 'address': 'test111'}
        response = self.client.put(url, query, headers=headers, format='json')
        self.assertEqual(response.status_code, 200)
        data = response.data
        assert 'id' in list(data)
        assert 'name' in list(data)
        assert 'address' in list(data)
        self.assertEqual(data['name'], 'test11')
        self.assertEqual(data['address'], 'test111')


class CoffeeDrinkViewSetTestCase(APITestCase):
    def setUp(self):
        shop_one = models.CoffeeShop(name='test1',
                                     address='test_addr1')
        shop_one.save()
        drink_one = models.CoffeeDrink(name='test1',
                                       price='99.99',
                                       volume=300)
        drink_one.shop = shop_one
        drink_one.save()
        
    def register_shopowner(self):
        owner_group = Group(name='shop owner')
        owner_group.save()
        url = reverse('auth-register')
        data = {'username': 'test',
                 'password': 'test'}
        response = self.client.post(url, data, format='json')
        self.access = response.data['access']
        self.refresh = response.data['refresh']
        shop_owner = models.CoffeeDrinker.objects.get(username='test')
        shop_owner.save()
        shop_owner.groups.add(owner_group)
        shop_owner.save()

    def test_coffeedrink_get(self):
        url = reverse('drink')

        # Id not a number
        query = {'id': 'test'}
        response = self.client.get(url, query, format='json')
        self.assertEqual(response.status_code, 400)

        # Invalid shop id
        query = {'id': 1111}
        response = self.client.get(url, query, format='json')
        self.assertEqual(response.status_code, 404)

        # Successful request
        query = {'id': 1}
        response = self.client.get(url, query, format='json')
        self.assertEqual(response.status_code, 200)
        data = response.data
        assert 'name' in list(data)
        assert 'price' in list(data)
        assert 'volume' in list(data)
        self.assertEqual(data['name'], 'test1')
        self.assertEqual(data['price'], '99.99')
        self.assertEqual(data['volume'], 300)

    def test_coffeedrink_create(self):
        url = reverse('drink')

        self.register_shopowner()

        # Not authorized
        response = self.client.post(url, format='json')
        self.assertEqual(response.status_code, 401)

        # Wrong token
        headers = {'Authorization': 'Bearer test'}
        response = self.client.post(url, headers=headers, format='json')
        self.assertEqual(response.status_code, 401)
        # No query
        headers = {'Authorization': 'Bearer ' + self.access}
        response = self.client.post(url, headers=headers, format='json')
        self.assertEqual(response.status_code, 400)
        # Invalid query
        headers = {'Authorization': 'Bearer ' + self.access}
        query = {'test': 'test'}
        response = self.client.post(url, query, headers=headers, format='json')
        self.assertEqual(response.status_code, 400)
        # Successful request
        query = {'shop': 1,
                 'name': 'test',
                 'price': '0.00',
                 'volume': 100}
        headers = {'Authorization': 'Bearer ' + self.access}
        response = self.client.post(url, query, headers=headers, format='json')
        self.assertEqual(response.status_code, 201)
        data = response.data
        assert 'id' in list(data)
        assert 'name' in list(data)
        assert 'price' in list(data)
        assert 'volume' in list(data)
        self.assertEqual(data['name'], 'test')
        self.assertEqual(data['price'], '0.00')
        self.assertEqual(data['volume'], 100)

    def test_coffeedrink_update(self):
        url = reverse('drink')

        self.register_shopowner()

        # Not authorized
        response = self.client.put(url, format='json')
        self.assertEqual(response.status_code, 401)

        # Wrong token
        headers = {'Authorization': 'Bearer test'}
        response = self.client.put(url, headers=headers, format='json')
        self.assertEqual(response.status_code, 401)
        # No query
        headers = {'Authorization': 'Bearer ' + self.access}
        response = self.client.put(url, headers=headers, format='json')
        self.assertEqual(response.status_code, 400)
        # Invalid query
        headers = {'Authorization': 'Bearer ' + self.access}
        query = {'test': 'test'}
        response = self.client.put(url, query, headers=headers, format='json')
        self.assertEqual(response.status_code, 400)
        # Invalid id
        headers = {'Authorization': 'Bearer ' + self.access}
        query = {'id': 111}
        response = self.client.put(url, query, headers=headers, format='json')
        self.assertEqual(response.status_code, 404)
        # Invalid id type
        headers = {'Authorization': 'Bearer ' + self.access}
        query = {'id': 'test'}
        response = self.client.put(url, query, headers=headers, format='json')
        self.assertEqual(response.status_code, 400)
        # Successful request
        headers = {'Authorization': 'Bearer ' + self.access}
        query = {'id': 1,
                 'name': 'test11'}
        response = self.client.put(url, query, headers=headers, format='json')
        self.assertEqual(response.status_code, 200)
        data = response.data
        assert 'id' in list(data)
        assert 'name' in list(data)
        assert 'price' in list(data)
        assert 'volume' in list(data)
        self.assertEqual(data['name'], 'test11')
        self.assertEqual(data['price'], '99.99')
        self.assertEqual(data['volume'], 300)


class ReviewViewSetTestCase(APITestCase):
    def setUp(self):
        shop_one = models.CoffeeShop(name='test1',
                                     address='test_addr1')
        shop_one.save()
        drink_one = models.CoffeeDrink(name='test1',
                                       price='99.99',
                                       volume=300)
        drink_one.shop = shop_one
        drink_one.save()
        review_one = models.Review(notes='test1',
                                   descriptors=[1,2],
                                   overall_rating=1.1)
        review_one.drink = drink_one
        review_one.save()
        
    def register(self):
        url = reverse('auth-register')
        data = {'username': 'test',
                 'password': 'test'}
        response = self.client.post(url, data, format='json')
        self.access = response.data['access']
        self.refresh = response.data['refresh']

        review_one = models.Review.objects.get(id=1)
        drinker = models.CoffeeDrinker.objects.get(id=1)
        review_one.author = drinker
        review_one.save()

    def test_reviews_list(self):
        url = reverse('reviews')

        # Id not a number
        query = {'id': 'test'}
        response = self.client.get(url, query, format='json')
        self.assertEqual(response.status_code, 400)

        # Invalid shop id
        query = {'id': 1111}
        response = self.client.get(url, query, format='json')
        self.assertEqual(response.status_code, 200)

        # Successful request
        query = {'id': 1}
        response = self.client.get(url, query, format='json')
        self.assertEqual(response.status_code, 200)
        data = response.data
        # Check Pagination
        assert 'count' in list(data)
        assert 'next' in list(data)
        assert 'previous' in list(data)
        assert 'results' in list(data)

        self.assertEqual(data['count'], 1)
        data = data['results'][0]
        assert 'drink' in list(data)
        assert 'id' in list(data)
        assert 'notes' in list(data)
        assert 'descriptors' in list(data)
        assert 'overall_rating' in list(data)
        self.assertEqual(data['drink'], 1)
        self.assertEqual(data['notes'], 'test1')
        self.assertEqual(data['descriptors'], [1,2])
        self.assertEqual(data['overall_rating'], '1.1')

    def test_reviews_create(self):
        url = reverse('reviews')

        self.register()

        # Not authorized
        response = self.client.post(url, format='json')
        self.assertEqual(response.status_code, 401)

        # Wrong token
        headers = {'Authorization': 'Bearer test'}
        response = self.client.post(url, headers=headers, format='json')
        self.assertEqual(response.status_code, 401)
        # No query
        headers = {'Authorization': 'Bearer ' + self.access}
        response = self.client.post(url, headers=headers, format='json')
        self.assertEqual(response.status_code, 400)
        # Invalid query
        headers = {'Authorization': 'Bearer ' + self.access}
        query = {'test': 'test'}
        response = self.client.post(url, query, headers=headers, format='json')
        self.assertEqual(response.status_code, 400)
        # Successful request
        query = {'notes': 'test2',
                 'drink': 1,
                 'descriptors': [1],
                 'overall_rating': 2.2}
        headers = {'Authorization': 'Bearer ' + self.access}
        response = self.client.post(url, query, headers=headers, format='json')
        self.assertEqual(response.status_code, 201)
        data = response.data
        assert 'drink' in list(data)
        assert 'id' in list(data)
        assert 'notes' in list(data)
        assert 'descriptors' in list(data)
        assert 'overall_rating' in list(data)
        self.assertEqual(data['drink'], 1)
        self.assertEqual(data['notes'], 'test2')
        self.assertEqual(data['descriptors'], [1])
        self.assertEqual(data['overall_rating'], '2.2')

    def test_reviews_update(self):
        url = reverse('reviews')

        self.register()

        # Not authorized
        response = self.client.put(url, format='json')
        self.assertEqual(response.status_code, 401)

        # Wrong token
        headers = {'Authorization': 'Bearer test'}
        response = self.client.put(url, headers=headers, format='json')
        self.assertEqual(response.status_code, 401)
        # No query
        headers = {'Authorization': 'Bearer ' + self.access}
        response = self.client.put(url, headers=headers, format='json')
        self.assertEqual(response.status_code, 400)
        # Invalid query
        headers = {'Authorization': 'Bearer ' + self.access}
        query = {'test': 'test'}
        response = self.client.put(url, query, headers=headers, format='json')
        self.assertEqual(response.status_code, 400)
        # Invalid id
        headers = {'Authorization': 'Bearer ' + self.access}
        query = {'id': 111}
        response = self.client.put(url, query, headers=headers, format='json')
        self.assertEqual(response.status_code, 404)
        # Invalid id type
        headers = {'Authorization': 'Bearer ' + self.access}
        query = {'id': 'test'}
        response = self.client.put(url, query, headers=headers, format='json')
        self.assertEqual(response.status_code, 400)
        # Successful request
        headers = {'Authorization': 'Bearer ' + self.access}
        query = {'id': 1,
                 'notes': 'test2',
                 'drink': 1,
                 'descriptors': [1],
                 'overall_rating': 2.2}
        response = self.client.put(url, query, headers=headers, format='json')
        self.assertEqual(response.status_code, 200)
        data = response.data
        assert 'drink' in list(data)
        assert 'id' in list(data)
        assert 'notes' in list(data)
        assert 'descriptors' in list(data)
        assert 'overall_rating' in list(data)
        self.assertEqual(data['drink'], 1)
        self.assertEqual(data['notes'], 'test2')
        self.assertEqual(data['descriptors'], [1])
        self.assertEqual(data['overall_rating'], '2.2')
        # Check the changes
        query = {'id': 1}
        response = self.client.get(url, query, format='json')
        data = response.data['results'][0]
        self.assertEqual(data['notes'], 'test2')

        
class AuthViewSetTestCase(APITestCase):
    def register(self):
        url = reverse('auth-register')
        data = {'username': 'test',
                 'password': 'test'}
        response = self.client.post(url, data, format='json')
        self.access = response.data['access']
        self.refresh = response.data['refresh']

    def test_register(self):
        url = reverse('auth-register')

        # Empty request
        response = self.client.post(url, format='json')
        self.assertEqual(response.status_code, 400)
        # No username
        data = {'password': 'test'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)
        # No password
        data = {'username': 'test'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)
        # Successful request
        data = {'username': 'test',
                 'password': 'test'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)
        assert 'refresh' in list(response.data)
        assert 'access' in list(response.data)

        # User already exists
        data = {'username': 'test',
                 'password': 'test'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_login(self):
        self.register()
        url = reverse('auth-login')

        # No data provided
        response = self.client.post(url, format='json')
        self.assertEqual(response.status_code, 400)
        # No password provided
        data = {'username': 'test'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)
        # User doesn't exist
        data = {'username': 'test1',
                 'password': 'test1'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 404)
        # Wrong password
        data = {'username': 'test',
                 'password': 'test1'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 401)

        # Successful login
        data = {'username': 'test',
                 'password': 'test'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 200)
        assert 'refresh' in list(response.data)
        assert 'access' in list(response.data)

    def test_refresh(self):
        self.register()
        url = reverse('auth-refresh')

        # Invlid token
        data = {'refresh': 'test'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)

        # Valid token
        data = {'refresh': self.refresh}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 200)
        assert 'refresh' in list(response.data)
        assert 'access' in list(response.data)


class UsersMeViewSetTestCase(APITestCase):
    def register(self):
        url = reverse('auth-register')
        data = {'username': 'test',
                 'password': 'test'}
        response = self.client.post(url, data, format='json')
        self.access = response.data['access']
        self.refresh = response.data['refresh']

    def test_userme_get(self):
        self.register()
        url = reverse('users-me')

        # Anonymous (No token provided)
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 401)

        # Wrong token
        headers = {'Authorization': 'Bearer test'}
        response = self.client.get(url, headers=headers, format='json')
        self.assertEqual(response.status_code, 401)

        # Successful
        headers = {'Authorization': 'Bearer ' + self.access}
        response = self.client.get(url, headers=headers, format='json')
        self.assertEqual(response.status_code, 200)

        assert 'id' in list(response.data)
        assert 'username' in list(response.data)
        self.assertEqual(response.data['id'], 1)
        self.assertEqual(response.data['username'], 'test')


    def test_userme_update(self):
        self.register()
        url = reverse('users-me')

        # Anonymous
        response = self.client.put(url, format='json')
        self.assertEqual(response.status_code, 401)
        # Wrong token
        headers = {'Authorization': 'Bearer test'}
        response = self.client.put(url, headers=headers, format='json')
        self.assertEqual(response.status_code, 401)

        headers = {'Authorization': 'Bearer ' + self.access}

        # No data provided
        response = self.client.put(url, headers=headers, format='json')
        self.assertEqual(response.status_code, 200)

        # Firstname successful
        data = {'first_name': 'test'}
        response = self.client.put(url, data, headers=headers, format='json')
        self.assertEqual(response.status_code, 200)
        assert 'first_name' in list(response.data)
        self.assertEqual(response.data['first_name'], 'test')

        # Firstname too long
        data = {'education': 'test'*100}
        response = self.client.put(url, data, headers=headers, format='json')
        self.assertEqual(response.status_code, 400)

        # A few fields at once:
        data = {'first_name': 'fn',
                'last_name': 'ln',
                'education': 'edu',
                'email': 'e@ma.il'}
        response = self.client.put(url, data, headers=headers, format='json')
        self.assertEqual(response.status_code, 200)
        assert 'first_name' in list(response.data)
        assert 'last_name' in list(response.data)
        assert 'education' in list(response.data)
        assert 'email' in list(response.data)
        self.assertEqual(response.data['first_name'], 'fn')
        self.assertEqual(response.data['last_name'], 'ln')
        self.assertEqual(response.data['education'], 'edu')
        self.assertEqual(response.data['email'], 'e@ma.il')


    def test_userme_delete(self):
        self.register()
        url = reverse('users-me')

        # Invlid token
        headers = {'Authorization': 'Bearer test'}
        response = self.client.delete(url, headers=headers, format='json')
        self.assertEqual(response.status_code, 401)

        # Valid token
        headers = {'Authorization': 'Bearer ' + self.access}
        response = self.client.delete(url, headers=headers, format='json')
        self.assertEqual(response.status_code, 200)

        # Check user was deleted:
        drinkers = models.CoffeeDrinker.objects.all()
        self.assertEqual(len(drinkers), 0)
