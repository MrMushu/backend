from django.urls import path
from rest_framework_simplejwt import views as jwt_views
from django.conf.urls import url, include
from rest_framework_jwt.views import ObtainJSONWebToken, RefreshJSONWebToken
from.views import getMails, getMail

urlpatterns = [

    path('', getMails.as_view(), name='Get Mails'),
    path('mail/', getMail.as_view(), name='Get Mail')
]

# path '/login'
# path '/update_mail

# mock.onPost('/api/mail-app/update-mail').reply((request) => {
#    const mail = JSON.parse(request.data);
#    mailDB.mails = mailDB.mails.map((_mail) => {
#        if ( _mail.id === mail.id )
#        {
#            return mail;
#        }
#        return _mail;
#    });##
#
#    return [200, mail];
