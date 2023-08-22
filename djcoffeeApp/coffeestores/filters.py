from django_filters import rest_framework as filters

from coffeestores import models


class CoffeeShopFilterSet(filters.FilterSet):
    class Meta:
        model = models.CoffeeShop
        fields = ['name', 'address']

