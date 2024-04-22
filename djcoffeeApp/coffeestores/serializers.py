from rest_framework import serializers

from coffeestores import models


class CoffeeDrinkerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CoffeeDrinker
        fields = ['id', 'username', 'password', 
                  'first_name', 'last_name', 'email', 'education', 'photo']

    def update(self, instance, data):
        if 'first_name' in list(data):
            instance.first_name = data['first_name']
        if 'last_name' in list(data):
            instance.last_name = data['last_name']
        if 'email' in list(data):
            instance.email = data['email']
        if 'education' in list(data):
            instance.education = data['education']
        instance.save()
        return instance

    def upload(self, instance, file):
        instance.photo = file
        instance.save()
        return instance

class CoffeeDrinkerPutSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CoffeeDrinker
        fields = ['id', 'first_name', 'last_name', 'email', 'education']


class DescriptorSeralizer(serializers.ModelSerializer):
    queryset = models.Descriptor.objects.all()
    parent = serializers.PrimaryKeyRelatedField(queryset=queryset)

    class Meta:
        model = models.Descriptor
        fields = ['id', 'name', 'description', 'color', 'parent']


class CoffeeDrinkSerializer(serializers.ModelSerializer):
    # photo = serializers.ImageField(required=False, null=True)
    class Meta:
        model = models.CoffeeDrink
        fields = ['id', 'name', 'price', 'shop', 'volume', 'photo']
        '''

    def update(self, instance, data):
        if 'name' in list(data):
            instance.name = data['name']
        if 'price' in list(data):
            instance.price = data['price']
        if 'volume' in list(data):
            instance.volume = data['volume']
        instance.save()
        return instance
    '''

    def upload(self, instance, file):
        instance.photo = file
        instance.save()
        return instance

class ImageSerializer(serializers.Serializer):
    photo = serializers.ImageField(required=True)
    class Meta:
        model = models.CoffeeDrink
        fields = ['photo']


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
    '''
    def update(self, instance, data):
        if 'name' in list(data):
            instance.name = data['name']
        if 'address' in list(data):
            instance.address = data['address']
        instance.save()
        return instance
    '''

class CoffeeShopPutSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    name = serializers.CharField(max_length=63, required=False)
    address = serializers.CharField(max_length=255, required=False)
    class Meta:
        model = models.CoffeeShop
        fields = ['id', 'name', 'address']


class ReviewSerializer(serializers.ModelSerializer):
    # descriptors = Jso(required=False)
    author = serializers.IntegerField(required=False, source='author.id')

    class Meta:
        model = models.Review
        fields = ['drink', 'id', 'author', 'notes', 'descriptors', 'overall_rating']

    def set_author(self, instance, user):
        instance.author = user
        instance.save()
        return instance

    '''
    def update(self, instance, data):
        if 'notes' in list(data):
            instance.notes = data['notes']
        if 'descriptors' in list(data):
            instance.descriptors = data['descriptors']
        if 'overall_rating' in list(data):
            instance.overall_rating = data['overall_rating']
        instance.save()
        return instance
    '''


class ReviewPutSerializer(serializers.Serializer):
    notes = serializers.CharField(required=False)
    descriptors = serializers.JSONField(default=dict, required=False)
    overall_rating = serializers.DecimalField(max_digits=2, 
                                              decimal_places=1, required=False)


class TokenSerializer(serializers.Serializer):
    refresh = serializers.CharField(max_length=255)
    access = serializers.CharField(max_length=255)

class RefreshTokenSerializer(serializers.Serializer):
    refresh = serializers.CharField(max_length=255)
