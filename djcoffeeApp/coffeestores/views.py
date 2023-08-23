from django.shortcuts import render, get_object_or_404
from django.contrib.auth.hashers import check_password, make_password


import rest_framework.filters
from rest_framework import status, viewsets, permissions
from rest_framework.response import Response
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
        serializer = self.serializer_class()
        shop = serializer.update(shop, request.data)

        data = self.serializer_class(shop).data
        return Response(data, status=200)


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
                                    401: 'Unauthorized or dont have the permission'},
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
                                    404: 'Drink not found'},
                         request_body=serializers.CoffeeDrinkPutSerializer)
    def update(self, request):
        user = request.user
        if user.is_anonymous or not user.groups.filter(name='shop owner').exists():
            return Response('Unauthorized or dont have the permission', status=401)
        if 'id' not in list(request.data) or not str(request.data['id']).isdigit():
            return Response('No shop id provided', status=400)
        shop = get_object_or_404(self.queryset, id=request.data['id'])
        serializer = self.serializer_class()
        shop = serializer.update(shop, request.data)

        data = self.serializer_class(shop).data
        return Response(data, status=200)


# TEMP, just for testing
class CoffeeDrinkerViewSet(viewsets.ModelViewSet):
    queryset = models.CoffeeDrinker.objects.all()
    serializer_class = serializers.CoffeeDrinkerSerializer


class DescriptorViewSet(viewsets.ModelViewSet):
    queryset = models.Descriptor.objects.all()
    serializer_class = serializers.DescriptorSeralizer


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = models.Review.objects.all()
    serializer_class = serializers.ReviewSerializer

