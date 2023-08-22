"""
URL configuration for djcoffeeApp project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from rest_framework import permissions
from rest_framework.routers import DefaultRouter

from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from coffeestores import views

router = DefaultRouter()
# router.register(r'drinker', views.CoffeeDrinkerViewSet, basename='drinker')
router.register(r'desciptors', views.DescriptorViewSet, basename='descriptor')
# router.register(r'shops', views.CoffeeShopViewSet, basename='shop')
router.register(r'drinks', views.CoffeeDrinkViewSet, basename='drink')
router.register(r'reviews', views.ReviewViewSet, basename='review')
router.register(r'drinker', views.AuthViewSet, basename='auth')


schema_view = get_schema_view(
   openapi.Info(
      title='Django CoffeeApp API',
      default_version='v1',
      description='Test description',
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    path('', include(router.urls)),
    path('shops/', views.CoffeeShopViewSet.as_view(actions={'get': 'list'}), 
         name='shops'),
    path('auth/register', views.AuthViewSet.as_view(actions={'post': 'register'}), 
         name='auth-register'),
    path('auth/login', views.AuthViewSet.as_view(actions={'post': 'login'}), 
         name='auth-login'),
    path('admin/', admin.site.urls),
]
