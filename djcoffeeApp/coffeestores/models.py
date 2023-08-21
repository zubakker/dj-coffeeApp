from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class CoffeeDrinker(User):
    education = models.CharField(max_length=63)
    ...

class Descriptor(models.Model):
    name = models.CharField(max_length=31)
    description = models.CharField(max_length=127)
    color = models.CharField(max_length=7)

    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True)
    ...

class CoffeeShop(models.Model):
    name = models.CharField(max_length=63)
    address = models.CharField(max_length=255)
    ...

class CoffeeDrink(models.Model):
    name = models.CharField(max_length=31)
    # coffee_type - ? e.g. espresso, latte, ... 
    price = models.DecimalField(max_digits=6, decimal_places=2)
    shop = models.ForeignKey(CoffeeShop, on_delete=models.CASCADE)
    volume = models.SmallIntegerField()
    ...

class Review(models.Model):
    author = models.ForeignKey(CoffeeDrinker, on_delete=models.SET_NULL, null=True)
    notes = models.TextField(blank=True, null=True)
    descriptors = models.JSONField(default=list, blank=True, null=True)
    overall_rating = models.DecimalField(max_digits=2, decimal_places=1)
