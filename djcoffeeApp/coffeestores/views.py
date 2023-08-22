from django.shortcuts import render, get_object_or_404
from django.contrib.auth.hashers import check_password, make_password


import rest_framework.filters
from rest_framework import status, viewsets, permissions
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken, Token


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

    def create(self, request):
        ...

    def update(self, request):
        ...


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


# TEMP, just testing
class CoffeeDrinkerViewSet(viewsets.ModelViewSet):
    queryset = models.CoffeeDrinker.objects.all()
    serializer_class = serializers.CoffeeDrinkerSerializer


class DescriptorViewSet(viewsets.ModelViewSet):
    queryset = models.Descriptor.objects.all()
    serializer_class = serializers.DescriptorSeralizer




class CoffeeDrinkViewSet(viewsets.ModelViewSet):
    queryset = models.CoffeeDrink.objects.all()
    serializer_class = serializers.CoffeeDrinkSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = models.Review.objects.all()
    serializer_class = serializers.ReviewSerializer

