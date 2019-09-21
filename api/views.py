from django.shortcuts import render
from rest_framework.views import APIView
from django.http import HttpResponse
from backend import settings
import jwt
import json
from users.models import CustomUser
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from pymongo import MongoClient
import datetime
import requests
import time
import json
from .models import AnalyticsDashboard


class AnalyticsAPI(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):

        # token = request.META.get('HTTP_AUTHORIZATION')
        # decoded = jwt.decode(token[7:], settings.SECRET_KEY, 'UTF-8')

        # email = decoded['email']
        # store = decoded['store']

        token = '6061373e-a84e-4f12-4988-acb1fb9a92e9'
        merchant = 'DGE0FMKHHSBCE'

        dash = AnalyticsDashboard()

        result = {
            'widgets': {
                'sales_widget': dash.get_sales_widget(),
                'top_categories_widget': dash.top_categories_widget(),
                'payment_tender_widget': dash.payment_tender_widget(),
                'top_items_widget': dash.top_items_widget(),
            }
        }

        return Response(
            json.dumps(result)
        )
