from rest_framework import serializers

from coffeestores import models


class CoffeeDrinkerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CoffeeDrinker
        fields = ['id', 'username', 'password']


class DescriptorSeralizer(serializers.ModelSerializer):
    queryset = models.Descriptor.objects.all()
    parent = serializers.PrimaryKeyRelatedField(queryset=queryset)

    class Meta:
        model = models.Descriptor
        fields = ['id', 'name', 'description', 'color', 'parent']


class CoffeeDrinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CoffeeDrink
        fields = ['id', 'name', 'price', 'shop', 'volume']


class CoffeeShopSerializer(serializers.ModelSerializer):
    drinks = CoffeeDrinkSerializer(default=None)
    class Meta:
        model = models.CoffeeShop
        fields = ['id', 'name', 'address', 'drinks']


class ReviewSerializer(serializers.ModelSerializer):
    descriptors = DescriptorSeralizer()

    class Meta:
        model = models.Review
        fields = ['id', 'author', 'notes', 'descriptors', 'overall_rating']


class TokenSerializer(serializers.Serializer):
    refresh = serializers.CharField(max_length=255)
    access = serializers.CharField(max_length=255)
