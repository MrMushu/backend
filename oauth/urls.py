from django.urls import path
from rest_framework_simplejwt import views as jwt_views
from .models import Oauth
from django.conf.urls import url, include
from rest_framework_jwt.views import ObtainJSONWebToken, RefreshJSONWebToken


urlpatterns = [

    path('', Oauth.as_view(),
         name='oauth'),

]
