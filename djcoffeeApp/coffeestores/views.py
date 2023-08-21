from django.shortcuts import render

from rest_framework import status, viewsets
# Create your views here.
from coffeestores import serializers, models


# TEMP, just testing
class CoffeeDrinkerViewSet(viewsets.ModelViewSet):
    queryset = models.CoffeeDrinker.objects.all()
    serializer_class = serializers.CoffeeDrinkerSerializer


class DescriptorViewSet(viewsets.ModelViewSet):
    queryset = models.Descriptor.objects.all()
    serializer_class = serializers.DescriptorSeralizer


class CoffeeShopViewSet(viewsets.ModelViewSet):
    queryset = models.CoffeeShop.objects.all()
    serializer_class = serializers.CoffeeShopSerializer


class CoffeeDrinkViewSet(viewsets.ModelViewSet):
    queryset = models.CoffeeDrink.objects.all()
    serializer_class = serializers.CoffeeDrinkSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = models.Review.objects.all()
    serializer_class = serializers.ReviewSerializer

