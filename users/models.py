from django.contrib.auth.models import (
    AbstractBaseUser, AbstractUser, BaseUserManager, Group, Permission,
    PermissionsMixin, UserManager,
)
from djongo import models
from rest_framework_jwt import authentication
import jwt
import json
import requests
import time
from django.conf import settings

from rest_framework import authentication, exceptions


# The custom user uses email as the unique identifier, and requires
# that every user provide a date of birth. This lets us test
# changes in username datatype, and non-text required fields.


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, store=None, ):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(

            email=self.normalize_email(email),
            store=store,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self,  email, password, store=None):
        u = self.create_user(email, password,
                             store)
        u.is_admin = True
        u.save(using=self._db)
        return u


class CustomUser(AbstractBaseUser):

    _id = models.ObjectIdField()

    email = models.EmailField(
        verbose_name='email address', max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    store = models.CharField(max_length=100)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['store']

    def __str__(self):
        return self.email

    # Maybe required?
    def get_group_permissions(self, obj=None):
        return set()

    def get_all_permissions(self, obj=None):
        return set()

    def has_perm(self, perm, obj=None):
        return True

    def has_perms(self, perm_list, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    # Admin required fields
    @property
    def is_staff(self):
        return self.is_admin


class RemoveGroupsAndPermissions:
    """
    A context manager to temporarily remove the groups and user_permissions M2M
    fields from the AbstractUser class, so they don't clash with the
    related_name sets.
    """

    def __enter__(self):
        self._old_au_local_m2m = AbstractUser._meta.local_many_to_many
        self._old_pm_local_m2m = PermissionsMixin._meta.local_many_to_many
        groups = models.ManyToManyField(Group, blank=True)
        groups.contribute_to_class(PermissionsMixin, "groups")
        user_permissions = models.ManyToManyField(Permission, blank=True)
        user_permissions.contribute_to_class(
            PermissionsMixin, "user_permissions")
        PermissionsMixin._meta.local_many_to_many = [groups, user_permissions]
        AbstractUser._meta.local_many_to_many = [groups, user_permissions]

    def __exit__(self, exc_type, exc_value, traceback):
        AbstractUser._meta.local_many_to_many = self._old_au_local_m2m
        PermissionsMixin._meta.local_many_to_many = self._old_pm_local_m2m


class CustomUserWithoutIsActiveField(AbstractBaseUser):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)

    objects = UserManager()

    USERNAME_FIELD = 'username'


# The extension user is a simple extension of the built-in user class,
# adding a required date_of_birth field. This allows us to check for
# any hard references to the name "User" in forms/handlers etc.
with RemoveGroupsAndPermissions():
    class ExtensionUser(AbstractUser):
        date_of_birth = models.DateField()

        custom_objects = UserManager()

        REQUIRED_FIELDS = AbstractUser.REQUIRED_FIELDS + ['date_of_birth']


class JWTAuthentication(authentication.BaseAuthentication):
    authentication_header_prefix = 'Bearer '

    def authenticate(self, request):
        """
        The `authenticate` method is called on every request regardless of
        whether the endpoint requires authentication. 

        `authenticate` has two possible return values:

        1) `None` - We return `None` if we do not wish to authenticate. Usually
                    this means we know authentication will fail. An example of
                    this is when the request does not include a token in the
                    headers.

        2) `(user, token)` - We return a user/token combination when 
                             authentication is successful.

                            If neither case is met, that means there's an error 
                            and we do not return anything.
                            We simple raise the `AuthenticationFailed` 
                            exception and let Django REST Framework
                            handle the rest.
        """
        request.user = None

        # `auth_header` should be an array with two elements: 1) the name of
        # the authentication header (in this case, "Token") and 2) the JWT
        # that we should authenticate against.
        auth_header = authentication.get_authorization_header(request).split()
        auth_header_prefix = self.authentication_header_prefix.lower()

        if not auth_header:
            return None

        if len(auth_header) == 1:
            # Invalid token header. No credentials provided. Do not attempt to
            # authenticate.
            return None

        elif len(auth_header) > 2:
            # Invalid token header. The Token string should not contain spaces. Do
            # not attempt to authenticate.
            return None

        # The JWT library we're using can't handle the `byte` type, which is
        # commonly used by standard libraries in Python 3. To get around this,
        # we simply have to decode `prefix` and `token`. This does not make for
        # clean code, but it is a good decision because we would get an error
        # if we didn't decode these values.
        prefix = auth_header[0].decode('utf-8')
        token = auth_header[1].decode('utf-8')

        # if prefix.lower() != auth_header_prefix:
        # The auth header prefix is not what we expected. Do not attempt to
        # authenticate.
        # return None

        # By now, we are sure there is a *chance* that authentication will
        # succeed. We delegate the actual credentials authentication to the
        # method below.
        return self.authenticate_credentials(request, token)

    def authenticate_credentials(self, request, token):
        """
        Try to authenticate the given credentials. If authentication is
        successful, return the user and token. If not, throw an error.
        """
        try:
            payload = jwt.decode(token, settings.SECRET_KEY)
        except:
            msg = 'Invalid authentication. Could not decode token.'
            raise exceptions.AuthenticationFailed(msg)

        try:
            user = CustomUser.objects.get(email=payload['email'])
        except:
            msg = 'No user matching this token was found.'
            raise exceptions.AuthenticationFailed(msg)

        if not user.is_active:
            msg = 'This user has been deactivated.'
            raise exceptions.AuthenticationFailed(msg)

        return (user, token)

class ItemsTab():
  
    def __init__(self, merchant, token):
        self.merchant = merchant
        self.token = token
        self.init_category_items()
        self.init_mod_sales()
        self.init_taxes()

    def init_taxes(self):
        taxes = requests.get('https://api.clover.com:443/v3/merchants/{}/tax_rates/?access_token={}'.format(self.merchant,self.token)).text
        taxes = json.loads(taxes)
        for tax in taxes['elements']:
            if tax['isDefault'] == True:
                self.tax = tax['rate']/10000000

    def init_category_items(self):
        
        categories = requests.get('https://api.clover.com:443/v3/merchants/{}/categories?access_token={}&expand=items'.format(self.merchant,self.token)).text
        categories = json.loads(categories)
        self.categories = {}
        for category in categories['elements']:
            update = {category['name']:category}
            self.categories.update(update)
    
        self.item_categories = {}
        for category in self.categories:
            for item in self.categories[category]['items']['elements']:
                
                item_category = {item['id']:category}
                self.item_categories.update(item_category)

    def init_mod_sales(self):

        mods = requests.get('https://api.clover.com:443/v3/merchants/{}/modifier_groups?access_token={}&expand=modifiers,items'.format(self.merchant,self.token)).text
        mods = json.loads(mods)
        self.mod_sales ={}
        for mod in mods['elements']:
            for item in mod['items']['elements']:
                name = item['name']
                if name not in self.mod_sales:
                    self.mod_sales[name] = {}
                for modifier in mod['modifiers']['elements']:
                    self.mod_sales[name][modifier['name']] = {}
                    self.mod_sales[name][modifier['name']]['Quantity Sold'] = 0
                    self.mod_sales[name][modifier['name']]['Amount'] = 0


                
    def get_category_breakdown(self, start, end):
        columns = ['Quantity Sold', 'Sales', 'Modifiers', 'Tax','Discounts','Refunds','Inventory','Cost','Net','Profit']
        self.category_sales = {}

        for category in self.categories:
            self.category_sales[category] = {}
            self.category_sales[category]['Category'] = category
            for column in columns:
                self.category_sales[category][column] = 0

            start_time = start
            end_time = end

        line_item_sales = {}
        columns = ['Stock','Quantity Sold','Sales','Cost','Modifiers','Discounts','Refunds','Tax','Gross','Net','Profit']

        for category in self.categories:
            line_item_sales[category] = {}
            for item in self.categories[category]['items']['elements']:
            
                line_item_sales[category][item['name']] = {}
                for column in columns:
                    line_item_sales[category][item['name']][column] = 0
                
                try:
                    line_item_sales[category][item['name']]['Cost'] = item['cost']
                except:
                    pass
                

        while True:

            orders = requests.get('https://api.clover.com:443/v3/merchants/{}/orders?access_token={}&filter=createdTime>={}&filter=createdTime<{}'.format(self.merchant,self.token,start_time,end_time)).text
            orders = json.loads(orders)

            for order in orders['elements']:

                time.sleep(.4)

                mods = requests.get('https://api.clover.com:443/v3/merchants/{}/orders/{}/line_items?access_token={}&expand=modifications,discounts,refunds'.format(self.merchant, order['id'],self.token)).text
                mods = json.loads(mods)

                ###### LINE ITEMS ######

                for mod in mods['elements']:
                    
                    item_id = mod['item']['id']
                    item_name = mod['name']
                    category = self.item_categories[item_id]

                    line_item_sales[category][item_name]['Quantity Sold'] += 1
                    line_item_sales[category][item_name]['Sales'] += mod['price']/100

                    ### Discounts ###

                    disc = 0

                    if 'discounts' in mod:
                        for discount in mod['discounts']['elements']:
                            if 'amount' in discount['discount']:
                                disc = discount['discount']['amount']
                                self.category_sales[category]['Discounts'] += disc

                    ### Refunds ###

                    if mod['refunded']:
                        self.category_sales[category]['Refunds'] += mod['refund']['amount']/100  
                    
                    ### Price ###
                    self.category_sales[category]['Sales'] += mod['price']/100

                    ###### MODIFIERS ######

                    if 'modifications' in mod:
                        for modifier in mod['modifications']['elements']:
                            # sales total for category
                            self.category_sales[category]['Modifiers'] += modifier['amount']/100

                            line_item_sales[category][item_name]['Modifiers'] += modifier['amount']/100
                            self.mod_sales[item_name][modifier['name']]['Quantity Sold'] += 1
                            self.mod_sales[item_name][modifier['name']]['Amount'] += modifier['amount']/100

                self.category_sales[category]['Quantity Sold'] += 1
        
                if 'cost' in line_item_sales[category][item_name]:
                    self.category_sales[category]['Cost'] += line_item_sales[category][item_name]['cost']
                    
                ### Line Item Sales ###
                # line_item_sales = table breakdown for items sold
                
                
                for category in self.categories:
                    for item in line_item_sales[category]:
                        line = line_item_sales[category][item]
                        
                        line['Net'] = round(line['Sales']+line['Modifiers']-line['Discounts']-line['Refunds'],2)
                        line['Tax'] = round(self.tax*(line['Sales']+line['Modifiers']-line['Discounts']-line['Refunds']),2)
                        line['Gross'] = round(line['Net'] + line['Tax'],2)
                        line['Profit'] = round(line['Net'] - line['Cost'],2)
                ### Mod Sales ###
                # mod_sales = table breakdwon for modifiers sold


                ### Category Sales ###
                # category sales = table breakdown of categories #
                
                for category in self.category_sales:
                    cat = self.category_sales[category]
                    cat['Net'] = cat['Sales'] - cat['Discounts'] - cat['Refunds']
                    cat['Tax'] = self.tax*(cat['Sales'] + cat['Modifiers'] - cat['Discounts'] - cat['Refunds'])
                    cat['Gross'] = cat['Net'] + cat['Tax']
                
            
            if orders['elements'] == []:
                return ('yes')
               
            
            end_time = orders['elements'][-1]['createdTime']
            
    def widget10(self):
        cats = ['Category', 'Quantity Sold', 'Sales', 'Modifiers', 'Tax','Discounts','Refunds','Inventory','Cost','Net','Profit']
        columns = []
        rows = []

        for table_column in cats:
            column = {
                'id': table_column.lower(),
                'title': table_column
            }
            columns.append(column)

        num = 0
        for category in self.category_sales:
            cells = []
            for table_column in cats:
                
                cell = {
                    'id':table_column.lower(),
                    'value':self.category_sales[category][table_column],
                    'classes': '',
                    'icon': '',
                }
                cells.append(cell)
                
            rows.append({
                'id':num,
                'cells': cells
            })
            num += 1
            
        widget = {
            'widget10': {
                'title': 'Category Breakdown',
                'table': {
                    'columns': columns,
                    'rows': rows
                }
            }
        }
        
        return widget

def line_item_table():
    return({'line_items': {'table':[{'Category': 'Meals',
  'Quantity Sold': 72,
  'Sales': 1437.850000000001,
  'Modifiers': 14.5,
  'Tax': 112.56,
  'Discounts': 0,
  'Refunds': 0,
  'Inventory': 0,
  'Cost': 0,
  'Net': 1437.85,
  'Profit': 0,
  'Gross': 1550.41,
  'id': 0},
 {'Category': 'Chicken',
  'Quantity Sold': 24,
  'Sales': 806.1900000000002,
  'Modifiers': 0.0,
  'Tax': 62.48,
  'Discounts': 0,
  'Refunds': 0,
  'Inventory': 0,
  'Cost': 0,
  'Net': 806.19,
  'Profit': 0,
  'Gross': 868.67,
  'id': 1},
 {'Category': 'Entrees',
  'Quantity Sold': 23,
  'Sales': 196.60000000000008,
  'Modifiers': 3.0,
  'Tax': 15.47,
  'Discounts': 0,
  'Refunds': 0,
  'Inventory': 0,
  'Cost': 0,
  'Net': 196.6,
  'Profit': 0,
  'Gross': 212.07,
  'id': 2},
 {'Category': 'Party Paks',
  'Quantity Sold': 10,
  'Sales': 908.0,
  'Modifiers': 7.5,
  'Tax': 70.95,
  'Discounts': 0,
  'Refunds': 0,
  'Inventory': 0,
  'Cost': 0,
  'Net': 908.0,
  'Profit': 0,
  'Gross': 978.95,
  'id': 3},
 {'Category': 'Sides',
  'Quantity Sold': 14,
  'Sales': 280.6400000000001,
  'Modifiers': 0.0,
  'Tax': 21.75,
  'Discounts': 0,
  'Refunds': 0,
  'Inventory': 0,
  'Cost': 0,
  'Net': 280.64,
  'Profit': 0,
  'Gross': 302.39,
  'id': 4},
 {'Category': 'Drinks',
  'Quantity Sold': 6,
  'Sales': 52.2,
  'Modifiers': 0.0,
  'Tax': 4.05,
  'Discounts': 0,
  'Refunds': 0,
  'Inventory': 0,
  'Cost': 0,
  'Net': 52.2,
  'Profit': 0,
  'Gross': 56.25,
  'id': 5},
 {'Category': 'Custom',
  'Quantity Sold': 0,
  'Sales': 3.5,
  'Modifiers': 0,
  'Tax': 0.27,
  'Discounts': 0,
  'Refunds': 0,
  'Inventory': 0,
  'Cost': 0,
  'Net': 3.5,
  'Profit': 0,
  'Gross': 3.77,
  'id': 6}],
  'rows':[{'id': 'Category',
  'align': 'left',
  'disablePadding': False,
  'label': 'Category',
  'sort': True},
 {'id': 'Quantity_Sold',
  'align': 'left',
  'disablePadding': False,
  'label': 'Quantity Sold',
  'sort': True},
 {'id': 'Sales',
  'align': 'left',
  'disablePadding': False,
  'label': 'Sales',
  'sort': True},
 {'id': 'Modifiers',
  'align': 'left',
  'disablePadding': False,
  'label': 'Modifiers',
  'sort': True},
 {'id': 'Tax',
  'align': 'left',
  'disablePadding': False,
  'label': 'Tax',
  'sort': True},
 {'id': 'Discounts',
  'align': 'left',
  'disablePadding': False,
  'label': 'Discounts',
  'sort': True},
 {'id': 'Refunds',
  'align': 'left',
  'disablePadding': False,
  'label': 'Refunds',
  'sort': True},
 {'id': 'Inventory',
  'align': 'left',
  'disablePadding': False,
  'label': 'Inventory',
  'sort': True},
 {'id': 'Cost',
  'align': 'left',
  'disablePadding': False,
  'label': 'Cost',
  'sort': True},
 {'id': 'Net',
  'align': 'left',
  'disablePadding': False,
  'label': 'Net',
  'sort': True},
 {'id': 'Profit',
  'align': 'left',
  'disablePadding': False,
  'label': 'Profit',
  'sort': True},
 {'id': 'Gross',
  'align': 'left',
  'disablePadding': False,
  'label': 'Gross',
  'sort': True},
 ]}})
        