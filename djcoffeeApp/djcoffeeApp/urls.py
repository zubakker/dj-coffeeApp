from django.contrib import admin
from django.urls import path, include, re_path

from rest_framework import permissions

from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from coffeestores import views, consumers



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

    path('shops/', views.CoffeeShopViewSet.as_view(actions={'get': 'list', 
                                                            'post': 'create',
                                                            'put': 'update'}), 
         name='shops'),
    path('auth/register', views.AuthViewSet.as_view(actions={'post': 'register'}), 
         name='auth-register'),
    path('auth/login', views.AuthViewSet.as_view(actions={'post': 'login'}), 
         name='auth-login'),
    path('auth/refresh', views.AuthViewSet.as_view(actions={'post': 'refresh'}), 
         name='auth-refresh'),
    path('drink/', views.CoffeeDrinkViewSet.as_view(actions={'get': 'get',
                                                             'post': 'create',
                                                             'put': 'update'}),
         name='drink'),
    path('drink/upload', views.CoffeeDrinkViewSet.as_view(actions={'post': 'upload'}),
         name='drink-upload'),
    path('reviews/', views.ReviewViewSet.as_view(actions={'get': 'list',
                                                          'post': 'create',
                                                          'put': 'update'}),
         name='reviews'),
    path('users/me', views.UsersMeViewSet.as_view(actions={'get': 'get',
                                                           'put': 'update',
                                                           'delete': 'delete'}),
         name='users-me'),
    path('users/me/upload', views.UsersMeViewSet.as_view(actions={'post': 'upload'}),
         name='users-me-upload'),
    path('admin/', admin.site.urls),
]

websocket_urlpatterns = [
    re_path('send', consumers.MyConsumer.as_asgi()),
]
