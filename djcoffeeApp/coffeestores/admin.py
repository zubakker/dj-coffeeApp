from django.contrib import admin

from coffeestores import models
# Register your models here.
admin.site.register(models.CoffeeDrinker)
admin.site.register(models.Descriptor)
admin.site.register(models.CoffeeShop)
admin.site.register(models.CoffeeDrink)
admin.site.register(models.Review)
