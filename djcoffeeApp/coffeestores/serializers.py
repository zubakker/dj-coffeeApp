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

    def update(self, instance, data):
        if 'name' in list(data):
            instance.name = data['name']
        if 'price' in list(data):
            instance.name = data['price']
        if 'volume' in list(data):
            instance.name = data['volume']
        instance.save()
        return instance


class CoffeeDrinkPutSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    name = serializers.CharField(max_length=31, required=False)
    price = serializers.DecimalField(max_digits=6, decimal_places=2, required=False)
    volume = serializers.IntegerField(required=False)
    class Meta:
        model = models.CoffeeShop
        fields = ['id', 'name', 'price', 'volume']


class CoffeeShopSerializer(serializers.ModelSerializer):
    drinks = CoffeeDrinkSerializer(default=None)
    class Meta:
        model = models.CoffeeShop
        fields = ['id', 'name', 'address', 'drinks']

    def create(self, validated_data):
        name = validated_data['name']
        address = validated_data['address']
        instance = self.Meta.model(name=name, address=address)
        instance.save()
        return instance
    def update(self, instance, data):
        if 'name' in list(data):
            instance.name = data['name']
        if 'address' in list(data):
            instance.address = data['address']
        instance.save()
        return instance

class CoffeeShopPutSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    name = serializers.CharField(max_length=63, required=False)
    address = serializers.CharField(max_length=255, required=False)
    class Meta:
        model = models.CoffeeShop
        fields = ['id', 'name', 'address']


class ReviewSerializer(serializers.ModelSerializer):
    descriptors = DescriptorSeralizer()

    class Meta:
        model = models.Review
        fields = ['id', 'author', 'notes', 'descriptors', 'overall_rating']


class TokenSerializer(serializers.Serializer):
    refresh = serializers.CharField(max_length=255)
    access = serializers.CharField(max_length=255)

class RefreshTokenSerializer(serializers.Serializer):
    refresh = serializers.CharField(max_length=255)
