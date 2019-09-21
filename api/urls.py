from django.urls import path
from rest_framework_simplejwt import views as jwt_views
from .views import AnalyticsAPI
from django.conf.urls import url, include
from rest_framework_jwt.views import ObtainJSONWebToken, RefreshJSONWebToken


urlpatterns = [

    path('', AnalyticsAPI.as_view(),
         name='Analytics API'),

]
