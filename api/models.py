from django.db import models
import json
import requests
import datetime
import time
from pymongo import MongoClient

from django.db import models
import json
import requests
import datetime
import time
from pytz import timezone

class AnalyticsDashboard():
    
    def __init__(self):
        self.refunds = 0
        self.discounts = 0
        self.total_revenue = 0
        self.total_tax = 0
        self.num_orders = 0
        self.merchant = 'DGE0FMKHHSBCE'
        self.token = '6061373e-a84e-4f12-4988-acb1fb9a92e9'
        self.tender = {}
        ### Timezone #
        self.get_properties()
        
        ### start/end time for one day
        self.get_today()
        
        
        self.init_taxes()
        self.init_category_items()
        self.init_mod_sales()
        self.get_category_breakdown()
        
        ### 
        self.get_dashboard()
        
        ### Top 5 categories/ items
        self.get_top_categories()
        self.get_top_items()
        


        
    def get_properties(self):

        merchant_properties = requests.get('https://api.clover.com:443/v3/merchants/{}/properties?access_token={}'.format(self.merchant,self.token)).text
        merchant_properties = json.loads(merchant_properties)
        self.timezone = merchant_properties['timezone']
        
    def get_today(self):
        
        tz = timezone(self.timezone)
        
        today = tz.localize(datetime.datetime.today())
     
        year = int(today.strftime('%Y'))
        month = int(today.strftime('%m'))
        day = int(today.strftime('%d'))

        self.end = datetime.datetime(year, month, day, 0,0)
        self.start = self.end + datetime.timedelta(days=-1)
        
        
  
        
        
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


                
    def get_category_breakdown(self,):
        columns = ['Quantity Sold', 'Sales', 'Modifiers', 'Tax','Discounts','Refunds','Inventory','Cost','Net','Profit']
        self.category_sales = {}

        for category in self.categories:
            self.category_sales[category] = {}
            self.category_sales[category]['Category'] = category
            for column in columns:
                self.category_sales[category][column] = 0

       
        self.line_item_sales = {}
        columns = ['Stock','Quantity Sold','Sales','Cost','Modifiers','Discounts','Refunds','Tax','Gross','Net','Profit']

        for category in self.categories:
            self.line_item_sales[category] = {}
            for item in self.categories[category]['items']['elements']:
            
                self.line_item_sales[category][item['name']] = {}
                for column in columns:
                    self.line_item_sales[category][item['name']][column] = 0
                
                try:
                    self.line_item_sales[category][item['name']]['Cost'] = item['cost']
                except:
                    pass
        
        
    def get_dashboard(self):
        
        self.start_t = self.start
        self.end_t = self.end
        self.sales_widget = {}
        self.sales_widget['date'] = []
        self.sales_widget['sales'] = []
        self.first = True
        self.hourly_sales = {}
        self.hourly_sales['hours'] = []
        self.hourly_sales['sales'] = {}
        
        for i in range(2):
            
            
            start_time = int(time.mktime(self.start_t.timetuple()))*1000
            end_time = int(time.mktime(self.end_t.timetuple()))*1000
            self.day_sales = 0
            
            while True:
                
                time.sleep(.88)
                orders = requests.get('https://api.clover.com:443/v3/merchants/{}/orders?access_token={}&filter=createdTime>={}&filter=createdTime<{}&expand=lineItems.modifications,discounts,refunds,payments.tender&limit=1000'.format(self.merchant,self.token,start_time,end_time)).text
                orders = json.loads(orders)
                
                
                if orders['elements'] == []:
                    self.avg_order = self.total_revenue / self.num_orders
                    break
                
                for order in orders['elements']:
                    
                    ### Line Items ###
                    lineItems = order['lineItems']['elements']
                    for item in lineItems:
                        
                        item_id = item['item']['id']
                        item_name = item['name']
                        item_price = item['price']
                        try:
                            category = self.item_categories[item_id]
                        
                            self.line_item_sales[category][item_name]['Quantity Sold'] += 1
                            self.line_item_sales[category][item_name]['Sales'] += item_price/100
                            
                            for modifier in item['modifications']['elements']:
                            
                                self.line_item_sales[category][item_name]['Modifiers'] += modifier['amount']/100
                                self.category_sales[category]['Modifiers'] += modifier['amount']/100
                                
                            self.category_sales[category]['Quantity Sold'] += 1
                            self.category_sales[category]['Sales'] += item_price/100
                            
                            
                            ### Refunds ### 

                            if item['refunded']:
                                self.category_sales[category]['Refunds'] += item['refunded']['refund']['amount']/100
                                self.refunds += item['refunded']['refund']['amount']/100
                        
                        except:
                            pass
                    
                    ### Discounts ###
                    
                    disc = 0
                    
                    if 'discounts' in order:
                    
                        for discount in order['discounts']['elements']:
                            if 'amount' in discount:
                                disc = discount['amount']
                                self.discounts += disc/100
                
                        
                    ### Sales ###
                    if 'payments' in order:
                        for payment in order['payments']['elements']:

                            if payment['result'] == 'SUCCESS':

                                self.total_revenue += payment['amount']/100 - payment['taxAmount']/100
                                self.total_tax += payment['taxAmount']/100
                                self.day_sales += payment['amount']/100

                                if payment['tender']['label'] in self.tender:
                                    self.tender[payment['tender']['label']] += payment['amount']/100
                                else:
                                    self.tender[payment['tender']['label']] = payment['amount']/100
                    
                    
                                if self.first:
                                    current_hour = payment['createdTime']
                                    tz = timezone(self.timezone)
        
                                    hour = datetime.datetime.fromtimestamp(current_hour/1000, tz).strftime('%I %p')
                                    
                                    if hour not in self.hourly_sales['hours']:
                                       
                                        self.hourly_sales['hours'].insert(0,hour)
                                        self.hourly_sales['sales'][hour] = 0
                                       
                                    self.hourly_sales['sales'][hour] += payment['amount']/100
                                                    
            
            
            
                    ### Num Orders ###
                    
                    self.num_orders += 1
                        

                
                
                end_time = orders['elements'][-1]['createdTime']
                
            self.sales_widget['date'].insert(0,self.start_t.strftime('%m/%d\n%a'))
            self.sales_widget['sales'].insert(0,round(self.day_sales,2))

            self.start_t = self.start_t - datetime.timedelta(days=1)
            self.end_t = self.end_t - datetime.timedelta(days=1)
            time.sleep(1)

            if self.first:
                self.todays_total_revenue = self.total_revenue
                self.todays_discounts = self.discounts
                self.todays_refunds = self.refunds
                
                self.todays_num_orders = self.num_orders
                self.todays_avg_order = self.total_revenue/self.num_orders

            self.first=False
            
        

    def get_top_categories(self):

        
        ### Category Sales ###
        # doesnt include modifier sales
        
        self.top_cats = []
        for category in self.category_sales:
            if len(self.top_cats) < 5:
                self.top_cats.append({'category':category, 'sales':self.category_sales[category]['Sales']})
            else:
                if self.top_cats[-1]['sales'] < self.category_sales[category]['Sales']:
                    self.top_cats[4] = {'category':category, 'sales':self.category_sales[category]['Sales']}
            self.top_cats = sorted(self.top_cats, key=lambda i:i['sales'], reverse=True)
            
    def get_top_items(self):
        
        ### Top 5 item sales ###
        
        self.top_items = []
        for category in self.line_item_sales:
            for item in self.line_item_sales[category]:
                if len(self.top_items) < 5:
                    self.top_items.append({'item':item, 'category':category, 'sales': self.line_item_sales[category][item]['Sales'], 'qty_sold':self.line_item_sales[category][item]['Quantity Sold'], })

                else:
                    if self.line_item_sales[category][item]['Sales'] > self.top_items[-1]['sales']:

                        self.top_items[4] = {'item':item, 'category':category, 'sales': round(self.line_item_sales[category][item]['Sales'],2),'qty_sold':self.line_item_sales[category][item]['Quantity Sold'] }
                self.top_items = sorted(self.top_items, key=lambda i:i['sales'], reverse=True)
        
        for item in self.top_items:
            
            item.update({'percent total': round(item['sales']/self.total_revenue*100,2)} )
     
                
    def get_sales_widget(self):
        
        sales = []
        for sale in self.hourly_sales['sales']:
            sales.insert(0,round(self.hourly_sales['sales'][sale],2))

        
       

        data = {
            'datasets': {
              'Weekly': [
                {
                  'label': "Weekly Sales",
                  'data': self.sales_widget['sales'],
                    'fill': 'start',
                  'labels': self.sales_widget['date'],
                  'total_revenue':round(self.total_revenue,2),
                    'orders':self.num_orders,
                    'avg_order': round(self.avg_order,2),
                    'discounts': round(-self.discounts,2),
                    'refunds': round(self.refunds,2),
                }
              ],
              'Today': [
                {
                  'label': "Daily Sales",
                  'data': sales,
                    'fill':'start',
                  'labels': self.hourly_sales['hours'],
                  'total_revenue':round(self.todays_total_revenue,2),
                'orders':self.todays_num_orders,
                'avg_order': round(self.todays_avg_order,2),
                'discounts': round(-self.todays_discounts,2),
                'refunds': round(self.todays_refunds,2),
                }
              ]
            },
            
            
           
        }
        
        
        return(data)
    
    def top_categories_widget(self):
        labels = []
        sales = []
        
        for item in self.top_cats:
            labels.append(item['category'])
            sales.append(round(item['sales']/self.total_revenue*100,1))
            
        data = {
            'mainChart': {
            'labels': labels,

            'datasets': [
              {
                'data': sales,
                'backgroundColor': [
                  "#4fc3f7",
                  "#7460ee",
                  "orange",
                  "#36bea6",
                  "blue"
                ],
                'hoverBackgroundColor': [
                  "#52629c",
                  "#ff7b2e",
                  "#bfeef2",
                  "#e9487f",
                  "#ffd341"
                ]
              }
            ],
            }}
        return data
    
    def payment_tender_widget(self):
        
        total = self.total_revenue + self.total_tax
        
        labels = ['Cash', 'Credit','Debit']
        tender = [round(self.tender['Cash']/total*100),round(self.tender['Credit Card']/total*100),round(self.tender['Debit Card']/total*100)]
        
        data = {
            'labels': labels,
            'data': tender
        }
        
        return data
    
    def top_items_widget(self):
       
        data = {
           'data':self.top_items
            }
        return data
    