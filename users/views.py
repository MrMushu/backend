from django.shortcuts import render
from django.shortcuts import render
from django.http import HttpResponse
from passlib.hash import pbkdf2_sha256

from rest_framework import generics, permissions, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from pymongo import MongoClient
from rest_framework import views
from .models import CustomUser, JWTAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from rest_framework_jwt.utils import jwt_payload_handler
from backend import settings
import jwt
import json
from .models import ItemsTab, line_item_table
# Create your views here.
from django.contrib.auth.hashers import make_password, check_password


class Login(views.APIView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):

        password = request.POST.dict().get('password')

        user = CustomUser.objects.get(
            email=request.POST.get('email'),
        )

        if not check_password(password, user.password):

            return Response({'Error': "Invalid email/password"}, status='400')

        else:
            if user:

                payload = {

                    'email': user.email,
                    'store': user.store,


                }

                jwt_token = {}
                jwt_token['access_token'] = jwt.encode(
                    payload, settings.SECRET_KEY).decode('UTF-8')
                jwt_token['user'] = user.email
                jwt_token['email'] = user.email

                client = MongoClient(
                    "mongodb+srv://aaokura:29teem782xx@ff-fdwa5.mongodb.net/test?retryWrites=true&w=majority")

                db = client['sales_data']
                finder = db['store_api']
                result = finder.find_one({'store': user.store})
                result = result['analytics_widgets']

                jwt_token['analyticsAPI'] = result

                token = '6061373e-a84e-4f12-4988-acb1fb9a92e9'
                merchant = 'DGE0FMKHHSBCE'

                widget = {
                    'widget8': {
                        'title': 'Sales by Category',
                'mainChart': {
                    'labels': ['Custom',
                    'Drinks',
                    'Sides',
                    'Party Paks',
                    'Entrees',
                    'Chicken',
                    'Meals'],
                'datasets': [{'data': [0, 31.72, 202.81, 878.0, 85.33, 551.16, 640.9],
                    'backgroundColor': ['#f44336',
                    '#9c27b0',
                    '#03a9f4',
                    '#e91e63',
                    '#ffc107'],
                    'hoverBackgroundColor': ['#f45a4d',
                    '#a041b0',
                    '#25b6f4',
                    '#e9487f',
                    '#ffd341']}],
                'options': {'cutoutPercentage': 0,
                    'spanGaps': False,
                    'legend': {'display': True,
                    'position': 'bottom',
                    'labels': {'padding': 16, 'usePointStyle': True}},
                    'maintainAspectRatio': False}}},
                    'BarWidget': {
                        'labels': ['1/4 Dark', '1/4 White', '1/2 Chicken Meal'],
                        'options': {"spanGaps": False,
                                    "legend": {"display": False},
                                    "maintainAspectRatio": False,
                                    "tooltips": {"position": "nearest",
                                                 "mode": "index",
                                                 "intersect": False},
                                    "layout": {"padding": {"left": 24,
                                                           "right": 32}},
                                    "elements": {"point": {"radius": 4,
                                                           "borderWidth": 2,
                                                           "hoverRadius": 4,
                                                           "hoverBorderWidth": 2}},
                                    "scales": {"xAxes": [{"gridLines": {"display": False},
                                                          "ticks": {"fontColor": "rgba(0,0,0,0.54)"}}],
                                               "yAxes": [{"gridLines": {"tickMarkLength": 5},
                                                          "ticks": {"minStepSize": 5}}]},
                                    "plugins": {"filler": {"propagate": False}}},
                        'datasets':[[199,104,250],[251,352,123],[234,152,535]]
                                     
                    },
                    'widget10': {'title': 'Category Breakdown',
            'table': {'columns': [{'id': 'category', 'title': 'Category'},
                {'id': 'quantity sold', 'title': 'Quantity Sold'},
                {'id': 'sales', 'title': 'Sales'},
                {'id': 'modifiers', 'title': 'Modifiers'},
                {'id': 'tax', 'title': 'Tax'},
                {'id': 'discounts', 'title': 'Discounts'},
                {'id': 'refunds', 'title': 'Refunds'},
                {'id': 'inventory', 'title': 'Inventory'},
                {'id': 'cost', 'title': 'Cost'},
                {'id': 'net', 'title': 'Net'},
                {'id': 'profit', 'title': 'Profit'}],
            'rows': [{'id': 6,
                'cells': [{'id': 'category',
                'value': 'Custom',
                'classes': '',
                'icon': ''},
                {'id': 'quantity sold', 'value': 0, 'classes': '', 'icon': ''},
                {'id': 'sales', 'value': 0, 'classes': '', 'icon': ''},
                {'id': 'modifiers', 'value': 0, 'classes': '', 'icon': ''},
                {'id': 'tax', 'value': 0.0, 'classes': '', 'icon': ''},
                {'id': 'discounts', 'value': 0, 'classes': '', 'icon': ''},
                {'id': 'refunds', 'value': 0, 'classes': '', 'icon': ''},
                {'id': 'inventory', 'value': 0, 'classes': '', 'icon': ''},
                {'id': 'cost', 'value': 0, 'classes': '', 'icon': ''},
                {'id': 'net', 'value': 0, 'classes': '', 'icon': ''},
                {'id': 'profit', 'value': 0, 'classes': '', 'icon': ''}]},
                {'id': 5,
                'cells': [{'id': 'category',
                'value': 'Drinks',
                'classes': '',
                'icon': ''},
                {'id': 'quantity sold', 'value': 3, 'classes': '', 'icon': ''},
                {'id': 'sales', 'value': 31.719999999999988,
                    'classes': '', 'icon': ''},
                {'id': 'modifiers', 'value': 0.0, 'classes': '', 'icon': ''},
                {'id': 'tax', 'value': 2.46, 'classes': '', 'icon': ''},
                {'id': 'discounts', 'value': 0, 'classes': '', 'icon': ''},
                {'id': 'refunds', 'value': 0, 'classes': '', 'icon': ''},
                {'id': 'inventory', 'value': 0, 'classes': '', 'icon': ''},
                {'id': 'cost', 'value': 0, 'classes': '', 'icon': ''},
                {'id': 'net', 'value': 31.72, 'classes': '', 'icon': ''},
                {'id': 'profit', 'value': 0, 'classes': '', 'icon': ''}]},
                {'id': 4,
                'cells': [{'id': 'category', 'value': 'Sides', 'classes': '', 'icon': ''},
                {'id': 'quantity sold', 'value': 10, 'classes': '', 'icon': ''},
                {'id': 'sales', 'value': 202.81000000000006,
                    'classes': '', 'icon': ''},
                {'id': 'modifiers', 'value': 0.0, 'classes': '', 'icon': ''},
                {'id': 'tax', 'value': 15.72, 'classes': '', 'icon': ''},
                {'id': 'discounts', 'value': 0, 'classes': '', 'icon': ''},
                {'id': 'refunds', 'value': 0, 'classes': '', 'icon': ''},
                {'id': 'inventory', 'value': 0, 'classes': '', 'icon': ''},
                {'id': 'cost', 'value': 0, 'classes': '', 'icon': ''},
                {'id': 'net', 'value': 202.81, 'classes': '', 'icon': ''},
                {'id': 'profit', 'value': 0, 'classes': '', 'icon': ''}]},
                {'id': 3,
                'cells': [{'id': 'category',
                'value': 'Party Paks',
                'classes': '',
                'icon': ''},
                {'id': 'quantity sold', 'value': 9, 'classes': '', 'icon': ''},
                {'id': 'sales', 'value': 878.0, 'classes': '', 'icon': ''},
                {'id': 'modifiers', 'value': 7.5, 'classes': '', 'icon': ''},
                {'id': 'tax', 'value': 68.63, 'classes': '', 'icon': ''},
                {'id': 'discounts', 'value': 0, 'classes': '', 'icon': ''},
                {'id': 'refunds', 'value': 0, 'classes': '', 'icon': ''},
                {'id': 'inventory', 'value': 0, 'classes': '', 'icon': ''},
                {'id': 'cost', 'value': 0, 'classes': '', 'icon': ''},
                {'id': 'net', 'value': 878.0, 'classes': '', 'icon': ''},
                {'id': 'profit', 'value': 0, 'classes': '', 'icon': ''}]},
                {'id': 2,
                'cells': [{'id': 'category',
                'value': 'Entrees',
                'classes': '',
                'icon': ''},
                {'id': 'quantity sold', 'value': 10, 'classes': '', 'icon': ''},
                {'id': 'sales', 'value': 85.33, 'classes': '', 'icon': ''},
                {'id': 'modifiers', 'value': 0.0, 'classes': '', 'icon': ''},
                {'id': 'tax', 'value': 6.61, 'classes': '', 'icon': ''},
                {'id': 'discounts', 'value': 0, 'classes': '', 'icon': ''},
                {'id': 'refunds', 'value': 0, 'classes': '', 'icon': ''},
                {'id': 'inventory', 'value': 0, 'classes': '', 'icon': ''},
                {'id': 'cost', 'value': 0, 'classes': '', 'icon': ''},
                {'id': 'net', 'value': 85.33, 'classes': '', 'icon': ''},
                {'id': 'profit', 'value': 0, 'classes': '', 'icon': ''}]},
                {'id': 1,
                'cells': [{'id': 'category',
                'value': 'Chicken',
                'classes': '',
                'icon': ''},
                {'id': 'quantity sold', 'value': 11, 'classes': '', 'icon': ''},
                {'id': 'sales', 'value': 551.1600000000001,
                    'classes': '', 'icon': ''},
                {'id': 'modifiers', 'value': 0.0, 'classes': '', 'icon': ''},
                {'id': 'tax', 'value': 42.71, 'classes': '', 'icon': ''},
                {'id': 'discounts', 'value': 0, 'classes': '', 'icon': ''},
                {'id': 'refunds', 'value': 0, 'classes': '', 'icon': ''},
                {'id': 'inventory', 'value': 0, 'classes': '', 'icon': ''},
                {'id': 'cost', 'value': 0, 'classes': '', 'icon': ''},
                {'id': 'net', 'value': 551.16, 'classes': '', 'icon': ''},
                {'id': 'profit', 'value': 0, 'classes': '', 'icon': ''}]},
                {'id': 0,
                'cells': [{'id': 'category', 'value': 'Meals', 'classes': '', 'icon': ''},
                {'id': 'quantity sold', 'value': 27, 'classes': '', 'icon': ''},
                {'id': 'sales', 'value': 575.0, 'classes': '', 'icon': ''},
                {'id': 'modifiers', 'value': 1.5, 'classes': '', 'icon': ''},
                {'id': 'tax', 'value': 44.68, 'classes': '', 'icon': ''},
                {'id': 'discounts', 'value': 0, 'classes': '', 'icon': ''},
                {'id': 'refunds', 'value': 0, 'classes': '', 'icon': ''},
                {'id': 'inventory', 'value': 0, 'classes': '', 'icon': ''},
                {'id': 'cost', 'value': 0, 'classes': '', 'icon': ''},
                {'id': 'net', 'value': 575.0, 'classes': '', 'icon': ''},
                {'id': 'profit', 'value': 0, 'classes': '', 'icon': ''}]}]}}}

                line = line_item_table()
                widget.update(line)
                jwt_token['ProjectsAPI'] = widget

                return Response(
                    json.dumps(jwt_token),
                    status=200,
                    content_type='application/json'
                )
            else:
                return Response(
                    json.dumps({'Error': "Invalid credentials"}),
                    status=400,
                    content_type="application/json"
                )


class TestView(viewsets.ViewSet):
    authentication_classes = (JWTAuthentication, )


class HelloView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        content = {'message': 'Hello, World!'}
        return Response(content)


class TokenLogin(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):

        token = request.POST.get('access_token')
        decoded = jwt.decode(token, settings.SECRET_KEY, 'UTF-8')

        email = decoded['email']
        store = decoded['store']

        payload = {

            'email': email,
            'store': store
        }

        jwt_token = {}
        jwt_token['access_token'] = jwt.encode(
            payload, settings.SECRET_KEY).decode('UTF-8')
        jwt_token['user'] = email
        jwt_token['email'] = email

        return Response(
            json.dumps(jwt_token),
            status=200,
            content_type='application/json'
        )
