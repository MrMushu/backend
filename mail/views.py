from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import login, get_mails, get_mail

import json


class getMails(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        folders = [
            {
                'id': 0,
                'handle': 'inbox',
                'title': 'Inbox',
                'icon': 'inbox'
            },
            {
                'id': 1,
                'handle': 'sent',
                'title': 'Sent',
                'icon': 'send'
            },
            {
                'id': 2,
                'handle': 'drafts',
                'title': 'Drafts',
                'icon': 'email_open'
            },
            {
                'id': 3,
                'handle': 'spam',
                'title': 'Spam',
                'icon': 'error'
            },
            {
                'id': 4,
                'handle': 'trash',
                'title': 'Trash',
                'icon': 'delete'
            }
        ]
        filters = [
            {
                'id': 0,
                'handle': 'starred',
                'title': 'Starred',
                'icon': 'star'
            },
            {
                'id': 1,
                'handle': 'important',
                'title': 'Important',
                'icon': 'label'
            }
        ]
        labels = [
            {
                'id': 0,
                'handle': 'note',
                'title': 'Note',
                'color': '#7cb342'
            },
            {
                'id': 1,
                'handle': 'paypal',
                'title': 'Paypal',
                'color': '#d84315'
            },
            {
                'id': 2,
                'handle': 'invoice',
                'title': 'Invoice',
                'color': '#607d8b'
            },
            {
                'id': 3,
                'handle': 'amazon',
                'title': 'Amazon',
                'color': '#03a9f4'
            }
        ]

        emails = get_mails(login())

        labelHandle = request.GET.dict().get('labelHandle')
        folderHandle = request.GET.dict().get('folderHandle')
        filterHandle = request.GET.dict().get('filterHandle')
        if labelHandle:
            label = list(
                filter(lambda label: label['handle'] == labelHandle, labels))
            result = list(
                filter(lambda email: email['labels'] == label[0]['id'], emails))

        elif filterHandle:

            result = list(
                filter(lambda email: email[filterHandle] == True, emails))

        else:
            if not folderHandle:
                folderHnale = 'inbox'

            folder = list(
                filter(lambda folder: folder['handle'] == folderHandle, folders))
            result = list(
                filter(lambda email: email['folder'] == folder[0]['id'], emails))

        return Response(
            result
        )


class getMail(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):

        mailId = request.GET.dict().get('mailId')

        result = get_mail(login(), mailId)

        return Response(
            result
        )
