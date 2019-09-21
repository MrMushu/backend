from django.db import models
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
import json
import requests
# Create your models here.


class Oauth(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        client_id = request.query_params.get('client_id', None)
        client_secret = 'e5973e5b-1ee9-b82a-de5f-86453dd40731'
        code = request.query_params.get('code', None)

        get_token = requests.get(
            'https://sandbox.dev.clover.com/oauth/token?client_id={}&client_secret={}&code={}'.format(client_id, client_secret, code)).text
        token_json = json.loads(get_token)
        try:
            return Response(token_json['access_token'])
        except:
            return Response('invalid token')
