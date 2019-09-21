from django.urls import path
from rest_framework_simplejwt import views as jwt_views
from .views import Login, HelloView, TestView, TokenLogin
from django.conf.urls import url, include
from rest_framework_jwt.views import ObtainJSONWebToken, RefreshJSONWebToken


urlpatterns = [

    path('token/', jwt_views.TokenObtainPairView.as_view(),
         name='token_obtain_pair'),
    path('token/refresh/', jwt_views.TokenRefreshView.as_view(),
         name='token_refresh'),

    path('login/', Login.as_view()),
    path('hello/', HelloView.as_view(), name='hello'),
    path('tokenlogin/', TokenLogin.as_view(), name='token login')
]
