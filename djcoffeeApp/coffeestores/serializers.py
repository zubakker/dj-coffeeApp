from rest_framework import serializers

from coffeestores import models


class CoffeeDrinkerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CoffeeDrinker
        fields = ['username', 'education']


class DescriptorSeralizer(serializers.ModelSerializer):
    queryset = models.Descriptor.objects.all()
    parent = serializers.PrimaryKeyRelatedField(queryset=queryset)

    class Meta:
        model = models.Descriptor
        fields = ['id', 'name', 'description', 'color', 'parent']


class CoffeeShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CoffeeShop
        fields = ['name', 'address']


class CoffeeDrinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CoffeeDrink
        fields = ['name', 'price', 'shop__name', 'volume']


class ReviewSerializer(serializers.ModelSerializer):
    descriptors = DescriptorSeralizer()

    class Meta:
        model = models.Review
        fields = ['author', 'notes', 'descriptors', 'overall_rating']

