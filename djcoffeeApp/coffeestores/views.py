from django.shortcuts import render, get_object_or_404
from django.contrib.auth.hashers import check_password, make_password


import rest_framework.filters
from rest_framework import status, viewsets, permissions
from rest_framework.response import Response
from rest_framework.parsers import FormParser, MultiPartParser, JSONParser
from rest_framework_simplejwt.tokens import RefreshToken, Token
from rest_framework_simplejwt.exceptions import TokenError


from django_filters.rest_framework import DjangoFilterBackend

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
# Create your views here.
from coffeestores import serializers, models, paginators, filters



class CoffeeShopViewSet(viewsets.ModelViewSet):
    queryset = models.CoffeeShop.objects.all()
    serializer_class = serializers.CoffeeShopSerializer
    put_serializer_class = serializers.CoffeeShopPutSerializer
    paginator = paginators.CoffeeShopPaginator()
    filter_backends = [DjangoFilterBackend, rest_framework.filters.OrderingFilter]
    filterset_class = filters.CoffeeShopFilterSet

    shop_id = openapi.Parameter('id', openapi.IN_QUERY, 
                                description="Id of a shop to get details of", 
                                type=openapi.TYPE_INTEGER)
    @swagger_auto_schema(responses={200: serializers.CoffeeShopSerializer,
                                    400: 'Shop id is not a number',
                                    404: 'Invalid shop id'},
                         manual_parameters=[shop_id])
    def list(self, request):
        coffeeshop_id = request.GET.get('id')
        if not coffeeshop_id:
            queryset = self.filter_queryset(self.get_queryset())
            shops_data = self.serializer_class(queryset, many=True).data
                
            result_page = self.paginator.paginate_queryset(queryset, request)
            serializer = self.serializer_class(result_page, many=True,
                                               context={'request': request})

            return self.paginator.get_paginated_response(serializer.data)

        if not coffeeshop_id.isdigit():
            return Response('Shop id is not a number', status=400)
        shop = get_object_or_404(self.queryset, id=coffeeshop_id)
        shop_data = self.serializer_class(shop).data
        drinks = models.CoffeeDrink.objects.filter(shop=coffeeshop_id)
        drinks_data = serializers.CoffeeDrinkSerializer(drinks, many=True).data

        shop_data['drinks'] = drinks_data
        return Response(shop_data)

    @swagger_auto_schema(responses={201: serializers.CoffeeShopSerializer,
                                    400: 'Invalid shop data',
                                    401: 'Unauthorized or dont have the permission'})
    def create(self, request):
        user = request.user
        if user.is_anonymous or not user.groups.filter(name='shop owner').exists():
            return Response('Unauthorized or dont have the permission', status=401)
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        serializer.save()
        return Response(serializer.data, status=201)

    @swagger_auto_schema(responses={200: serializers.CoffeeShopSerializer,
                                    400: 'Invalid shop data or shop id',
                                    401: 'Unauthorized or dont have the permission',
                                    404: 'Shop not found'},
                         request_body=serializers.CoffeeShopPutSerializer)
    def update(self, request):
        user = request.user
        if user.is_anonymous or not user.groups.filter(name='shop owner').exists():
            return Response('Unauthorized or dont have the permission', status=401)
        if 'id' not in list(request.data) or not str(request.data['id']).isdigit():
            return Response('No shop id provided', status=400)
        shop = get_object_or_404(self.queryset, id=request.data['id'])
        serializer = self.serializer_class(shop, data=request.data, partial=True) 
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        serializer.save()
        return Response(serializer.data, status=200)


class AuthViewSet(viewsets.ModelViewSet):
    queryset = models.CoffeeDrinker.objects.all()
    serializer_class = serializers.CoffeeDrinkerSerializer

    @swagger_auto_schema(responses={201: serializers.TokenSerializer,
                                    400: 'Invalid username or password'})
    def register(self, request):
        if 'username' not in list(request.data) or 'password' not in list(request.data):
            return Response('Username or password not provided', status=400)
        password = make_password(request.data['password'])
        request.data['password'] = password
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        user = serializer.save()
        token = RefreshToken.for_user(user)
        return Response({'refresh': str(token),
                         'access': str(token.access_token)}, status=201)
    
    @swagger_auto_schema(responses={200: serializers.TokenSerializer,
                                    400: 'Username or password not provided',
                                    401: 'Wrong password',
                                    404: 'User not found'})
    def login(self, request):
        if 'username' not in list(request.data) or 'password' not in list(request.data):
            return Response('Username or password not provided', status=400)
        user = get_object_or_404(self.queryset, username=request.data['username'])
        if not check_password(request.data['password'], user.password):
            return Response('Wrong password', status=401)
        token = RefreshToken.for_user(user)
        return Response({'refresh': str(token),
                         'access': str(token.access_token)})
    
    @swagger_auto_schema(responses={200: serializers.TokenSerializer,
                                    400: 'Invalid or expired token'},
                         request_body=serializers.RefreshTokenSerializer)
    def refresh(self, request):
        try:
            token = RefreshToken(request.data['refresh'])
        except TokenError:
            return Response('Invalid or expired token', status=400)

        return Response({'refresh': str(token),
                         'access': str(token.access_token)}, status=200)


class CoffeeDrinkViewSet(viewsets.ModelViewSet):
    queryset = models.CoffeeDrink.objects.all()
    serializer_class = serializers.CoffeeDrinkSerializer
    put_serializer_class = serializers.CoffeeDrinkPutSerializer
    parser_classes = (FormParser, MultiPartParser, JSONParser)

    drink_id = openapi.Parameter('id', openapi.IN_QUERY, 
                                 description="Id of a drink to get details of", 
                                 type=openapi.TYPE_INTEGER)
    @swagger_auto_schema(responses={200: serializers.CoffeeDrinkerSerializer,
                                    400: 'Id not provided or invalid',
                                    404: 'Invalid drink id'},
                         manual_parameters=[drink_id])
    def get(self, request):
        id = request.GET.get('id')
        if not id or not str(id).isdigit():
            return Response('Id not provided or invalid', status=400)
        drink = get_object_or_404(self.queryset, id=id)
        drink_data = self.serializer_class(drink).data

        return Response(drink_data)

    @swagger_auto_schema(responses={201: serializers.CoffeeDrinkerSerializer,
                                    400: 'Invalid drink data',
                                    401: 'Unauthorized or dont have the permission',
                                    415: 'Invalid parameters provided'},
                         request_body=serializers.CoffeeDrinkSerializer)
    def create(self, request):
        user = request.user
        if user.is_anonymous or not user.groups.filter(name='shop owner').exists():
            return Response('Unauthorized or dont have the permission', status=401)
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        serializer.save()
        return Response(serializer.data, status=201)

    @swagger_auto_schema(responses={200: serializers.CoffeeDrinkSerializer,
                                    400: 'Invalid drink data or drink id',
                                    401: 'Unauthorized or dont have the permission',
                                    404: 'Drink not found',
                                    415: 'Invalid parameters provided'},
                         request_body=serializers.CoffeeDrinkPutSerializer)
    def update(self, request):
        user = request.user
        if user.is_anonymous or not user.groups.filter(name='shop owner').exists():
            return Response('Unauthorized or dont have the permission', status=401)
        if 'id' not in list(request.data) or not str(request.data['id']).isdigit():
            return Response('No shop id provided', status=400)
        
        drink = get_object_or_404(self.queryset, id=request.data['id'])
        serializer = self.serializer_class(drink, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        serializer.save()
        return Response(serializer.data, status=200)

    @swagger_auto_schema(responses={200: serializers.CoffeeDrinkSerializer,
                                    400: 'Invalid drink id',
                                    401: 'Unauthorized or dont have the permission',
                                    404: 'Drink not found'},
                         operation_description='Upload image with a key "photo"',
                         request_body=serializers.ImageSerializer)
    def upload(self, request):
        user = request.user
        if user.is_anonymous or not user.groups.filter(name='shop owner').exists():
            return Response('Unauthorized or dont have the permission', status=401)
        if 'id' not in list(request.data) or not str(request.data['id']).isdigit():
            return Response('No shop id provided', status=400)

        shop = get_object_or_404(self.queryset, id=request.data['id'])
        photo = request.FILES.get('photo', None)

        serializer = self.serializer_class()
        shop = serializer.upload(shop, photo)
        data = self.serializer_class(shop).data
        return Response(data, status=200)


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = models.Review.objects.all()
    serializer_class = serializers.ReviewSerializer
    put_serializer_class = serializers.ReviewSerializer
    paginator = paginators.CoffeeShopPaginator()

    review_id = openapi.Parameter('id', openapi.IN_QUERY, 
                                 description="Id of a review to get details of", 
                                 type=openapi.TYPE_INTEGER)
    @swagger_auto_schema(responses={200: serializers.ReviewSerializer,
                                    400: 'Invalid drink id'},
                         manual_parameters=[review_id])
    def list(self, request):
        coffeedrink_id = request.GET.get('id')
        if not coffeedrink_id:
            return Response('No drink id provided', status=400)
        if not coffeedrink_id.isdigit():
            return Response('Drink id is not a number', status=400)
        reviews = self.queryset.filter(id=coffeedrink_id)
        drinks_data = self.serializer_class(reviews, many=True).data

        result_page = self.paginator.paginate_queryset(reviews, request)
        serializer = self.serializer_class(result_page, many=True,
                                           context={'request': request})

        return self.paginator.get_paginated_response(serializer.data)

    @swagger_auto_schema(responses={200: serializers.ReviewSerializer,
                                    400: 'Invalid review data or drink id',
                                    401: 'Unauthorized',
                                    404: 'Drink not found'},
                         request_body=serializers.ReviewSerializer)
    def create(self, request):
        user = request.user
        if user.is_anonymous:
            return Response('Unauthorized', status=401)
        if 'drink' not in list(request.data) or not str(request.data['drink']).isdigit():
            return Response('No drink id provided', status=400)
        drink = get_object_or_404(models.CoffeeDrink.objects.all(), 
                                  id=request.data['drink'])
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        instance = serializer.save()
        drinker = models.CoffeeDrinker.objects.get(id=user.id)
        serializer.set_author(instance, drinker)
        return Response(serializer.data, status=201)

    @swagger_auto_schema(responses={200: serializers.ReviewSerializer,
                                    400: 'Invalid review data or review id',
                                    401: 'Unauthorized or not the review author',
                                    404: 'Review not found'},
                         request_body=serializers.ReviewPutSerializer)
    def update(self, request):
        user = request.user
        if user.is_anonymous:
            return Response('Unauthorized', status=401)
        if 'id' not in list(request.data) or not str(request.data['id']).isdigit():
            return Response('No review id provided', status=400)
        review = get_object_or_404(self.queryset, id=request.data['id'])
        if review.author.id != user.id:
            return Response('Not the review author', status=401)

        serializer = self.serializer_class(review, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        serializer.save()
        return Response(serializer.data, status=200)


class UsersMeViewSet(viewsets.ModelViewSet):
    queryset = models.CoffeeDrinker.objects.all()
    serializer_class = serializers.CoffeeDrinkerSerializer
    put_serializer_class = serializers.CoffeeDrinkerSerializer
    parser_classes = (FormParser, MultiPartParser, JSONParser)

    @swagger_auto_schema(responses={200: serializers.CoffeeDrinkerSerializer,
                                    401: 'Unauthorized'})
    def get(self, request):
        user = request.user
        if user.is_anonymous:
            return Response('Unauthorized', status=401)
        drinker = self.queryset.get(id=user.id)
        serializer = self.serializer_class(drinker)
        return Response(serializer.data)

    @swagger_auto_schema(responses={200: serializers.CoffeeDrinkerSerializer,
                                    401: 'Unauthorized',
                                    415: 'Invalid data provided'},
                         request_body=serializers.CoffeeDrinkerPutSerializer)
    def update(self, request):
        user = request.user
        if user.is_anonymous:
            return Response('Unauthorized', status=401)
        drinker = self.queryset.get(id=user.id)
        serializer = self.serializer_class(request.user, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        serializer.save()
        return Response(serializer.data, status=200)

    @swagger_auto_schema(responses={200: 'Successfully deleted user',
                                    401: 'Unauthorized'})
    def delete(self, request):
        user = request.user
        if user.is_anonymous:
            return Response('Unauthorized', status=401)
        drinker = self.queryset.get(id=user.id)
        drinker.delete()
        return Response('Successfully deleted user', status=200)

    @swagger_auto_schema(responses={200: serializers.CoffeeDrinkerSerializer,
                                    401: 'Unauthorized'},
                         request_body=serializers.ImageSerializer)
    def upload(self, request):
        user = request.user
        if user.is_anonymous:
            return Response('Unauthorized', status=401)
        drinker = self.queryset.get(id=user.id)
        serializer = self.serializer_class()
        photo = request.FILES.get('photo', None)

        drinker = serializer.upload(drinker, photo)
        data = self.serializer_class(drinker).data
        return Response(data, status=200)
    

