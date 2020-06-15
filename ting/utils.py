from __future__ import unicode_literals
from django.core.files.uploadedfile import InMemoryUploadedFile
from datetime import datetime, timedelta, date
from django.core.files import File
from django.utils import timezone
from django.http import HttpResponse
from django.template.loader import get_template
from collections import OrderedDict
from xhtml2pdf import pisa
from io import BytesIO
from PIL import Image
import os
import base64
import time

TING_PACKAGES = (
		(1, 'Trial'),
		(2, 'Silver'),
		(3, 'Gold'),
		(4, 'Platinum')
	)

ACCOUNT_PURPOSE = (
		(1, 'Advertisment'),
		(2, 'Managment')
	)

ADMIN_TYPE = (
		(1, 'Administrator'),
		(2, 'Supervisor'),
		(3, 'Chef'),
		(4, 'Waiter'),
		(5, 'Accountant')
	)

TABLE_LOCATION = (
		(1, 'Inside'),
		(2, 'Outside'),
		(3, 'Balcony'),
		(4, 'Rooftop')
	)

CHAIR_TYPE = (
		(1, 'Iron'),
		(2, 'Wooden'),
		(3, 'Plastic'),
		(4, 'Couch'),
		(5, 'Mixture')
	)

GENDER = (
		('male', 'Male'),
		('female', 'Female')
	)

MENU_TYPE = (
		(1, 'Food'),
		(2, 'Drink'),
		(3, 'Dish')
	)

FOOD_TYPE = (
		(1, 'Appetizer'),
		(2, 'Meal'),
		(3, 'Dessert'),
		(4, 'Sauce')
	)

DRINK_TYPE = (
		(1, 'Water'),
		(2, 'Hot Beverage'),
		(3, 'Beer'),
		(4, 'Alcohol'),
		(5, 'Soda'),
		(6, 'Juice'),
		(7, 'Smoothie'),
		(8, 'Milkshake'),
		(9, 'Ice Cream'),
		(10, 'Cocktail'),
		(11, 'Wine'),
		(12, 'Other')
	)

DISH_TIME = (
		(1, 'Breakfast'),
		(2, 'Lunch'),
		(3, 'Dinner'),
		(4, 'Supper'),
		(5, 'Brunch'),
		(6, 'Snack'),
		(7, 'Other')
	)

PAID_BY = (
		(1, 'Cash'),
		(2, 'Mobile Money'),
		(3, 'Credit Card')
	)


CURRENCIES = (
		('USD', 'United State Dollar'),
		('UGX', 'Ugandan Shillings'),
		('GBP', 'Grand Britain Pounds')
	)

PROMOTION_MENU = (
		('00', 'All Menus'),
		('01', 'Food Menus'),
		('02', 'Drink Menus'),
		('03', 'Dish Menus'),
		('04', 'Specific Menu'),
		('05', 'Specific Category')
	)

PROMOTION_PERIOD = (
		(1, 'Every Day'),
		(2, 'Every Monday'),
		(3, 'Every Tuesday'),
		(4, 'Every Wednesday'),
		(5, 'Every Thursday'),
		(6, 'Every Friday'),
		(7, 'Every Saturday'),
		(8, 'Every Weekend')
	)


USER_ADDRESS_TYPE = (
		(1, 'Home'),
		(2, 'Work'),
		(3, 'School'),
		(4, 'Other')
	)

USER_ADDRESS_TYPE_LIST = ['Home', 'Work', 'School', 'Other']


RESTAURANT_AVAILABILITY = [
	{'id': 1, 'title': 'Not Available'},
	{'id': 2, 'title': 'Opened'},
	{'id': 3, 'title': 'Closed'}
]


RESTAURANT_RATINGS = [
	{'id': 1, 'title': '1 Star'},
	{'id': 2, 'title': '2 Stars'},
	{'id': 3, 'title': '3 Stars'},
	{'id': 4, 'title': '4 Stars'},
	{'id': 5, 'title': '5 Stars'}
]


RESTAURANT_SPECIALS = [
	{'id': 1, 'name': 'Wi-Fi',			'icon': 'wifi'},
	{'id': 2, 'name': 'Phone Booth', 	'icon': 'phone'},
	{'id': 3, 'name': 'TV', 			'icon': 'tv'},
	{'id': 4, 'name': 'Parking', 		'icon': 'car'},
	{'id': 5, 'name': 'Karaoke', 		'icon': 'microphone'},
	{'id': 6, 'name': 'Jazz', 			'icon': 'music'},
	{'id': 7, 'name': 'Bar', 			'icon': 'glass martini'},
	{'id': 8, 'name': 'Guards', 		'icon': 'shield alternate'}
]


RESTAURANT_SERVICES = [
	{'id': 1, 'name': 'Hotel', 			'icon': 'building'},
	{'id': 2, 'name': 'Spa', 			'icon': 'smile'},
	{'id': 3, 'name': 'Bar', 			'icon': 'glass martini'},
	{'id': 4, 'name': 'Meeting Space', 	'icon': 'bullhorn'},
	{'id': 5, 'name': 'Parties', 		'icon': 'birthday cake'}
]


BOOKING_PAYEMENT_MODE = (
		(1, 'Online (Credit Card)'),
		(2, 'Cash (On Site)'),
		(3, 'Both (Online / Cash)')
	)


BOOKING_STATUSES = (
		(1, 'Pending'),
		(2, 'Declined'),
		(3, 'Accepted'),
		(4, 'Paid'),
		(5, 'Completed'),
		(6, 'Refunded'),
		(7, 'Canceled')
	)

RESTAURANT_TYPES = [
		{'id': 1, 'name': 'Restaurant'},
		{'id': 2, 'name': 'Outlet'},
		{'id': 3, 'name': 'Resto & Bar'},
		{'id': 4, 'name': 'Bar'},
		{'id': 5, 'name': 'Coffee Shop'},
		{'id': 6, 'name': 'Supermarket'},
		{'id': 7, 'name': 'Food Truck'},
		{'id': 8, 'name': 'Bakery'}
]


SOCKET_REQUEST_TYPES = [
	'request_resto_table',
	'request_assign_waiter',
	'request_table_order',
	'request_notify_order',
	'request_bill_request',
	'request_placement_terminated'
]

SOCKET_RESPONSE_A_TYPES = [
	'response_w_resto_table',
	'request_w_table_order',
	'response_w_orders_updated',
	'request_w_notify_order',
	'request_w_bill_request',
	'response_w_request_message',
	'request_w_placement_terminated'
]

SOCKET_RESPONSE_U_TYPES = [
	'response_resto_table',
	'response_error',
	'response_resto_placement_done',
	'response_resto_table_waiter',
	'response_resto_bill_paid'
]

def get_from_tuple(data, key):
	if isinstance(data, tuple) is True:
		for t in data:
			if isinstance(t, tuple) is True:
				try:
					if int(t[0]) == int(key):
						return t[1]
				except Exception:
					for i in t:
						if key in i:
							return t[1] if str(t[0]) == str(key) else key
	return key

def get_from_dict(data, k, v):
	if isinstance(data, list) is True:
		for d in data:
			if isinstance(d, dict):
				if d[k] == v:
					return d
	return v


DEFAULT_USER_IMAGE 			= 'users/default.jpg'

DEFAULT_ADMIN_IMAGE 		= 'administrators/default.jpg'

DEFAULT_RESTAURANT_IMAGE 	= 'restaurants/default.jpg'

DEFAULT_ADMIN_NAME 			= 'Restaurant Admin'

DEFAULT_ADMIN_USERNAME 		= 'admin'

PUBNUB_SUBSCRIBE_KEY 		= 'sub-c-6597d23e-1b1d-11ea-b79a-866798696d74'

PUBNUB_PUBLISH_KEY 			= 'pub-c-62f722d6-c307-4dd9-89dc-e598a9164424'

PUSHER_APP_ID 				= '949894'

PUSHER_KEY 					= '299875b04b5fe1dc527a'

PUSHER_SECRET		 		= '6528a9e8016a7355e41c'

PUSHER_CLUSTER 				= 'mt1'

PUSHER_BEAMS_INSTANCE		= 'f47c28dd-63ae-49c0-9f30-88560b21e061'

PUSHER_BEAMS_SECRET_KEY		= '4F360544EE0422D1C115854EDA7B749B8DBD6711EA805849966BC339AB256CB3'

HOST_END_POINT				= 'http://172.20.10.9:8000'


def image_as_base64(image_file, format='png'):

	if not os.path.isfile(image_file):
		return None
    
	encoded_string = ''
	with open(image_file, 'rb') as img_f:
		encoded_string = base64.b64encode(img_f.read())
	return 'data:image/%s;base64,%s' % (format, encoded_string)


def int_to_string(number):
	zeros = ['', '00', '0']
	number = str(number)
	return '%s%s' % (zeros[len(number)], number) if len(number) < 3 else str(number)


def promoted_price(price, promo):			
	if promo != None:
		if promo.has_reduction:
			if promo.reduction_type == '%':
				return price - ((price * promo.amount) / 100)
			else:
				return price - promo.amount
	return price


def query_priority(value, queries):
	p = 0
	q = set(map(lambda v: v.lower(), queries))
	v = set(map(lambda v: v.lower(), value.replace(',','').split()))
		
	p += len(list(q & v))
		
	qr = q.difference(v)
	vr = v.difference(q)

	for k in qr:
		p += len(list(filter(lambda i: k in i, vr)))

	return p if len(qr) > 0 else 1000
		
		
def compress_image(image, memory):
	img = Image.open(image)
	img = img.convert('RGB')
	thumb_io = BytesIO()
	img.save(thumb_io, format='JPEG', quality=60)

	return InMemoryUploadedFile(
    	thumb_io, None, image.name, 
        'image/jpeg', thumb_io.tell(), None) if memory == True else File(img_io, name=image.name)


def get_month_name(month):
	months = ['January','Febuary', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
	return months[int(month) - 1]


def get_dates_days(days):
	today = timezone.datetime.today()
	return [today - timedelta(days=x) for x in range(days)]


def get_dates_months(months):
	today = time.localtime()
	return [time.localtime(time.mktime((today.tm_year, today.tm_mon - n, 1, 0, 0, 0, 0, 0, 0)))[:2] for n in range(months)]


def get_dates_years(years):
	today = time.localtime()
	return [today.tm_year - n for n in range(years)]


def get_days():
	return [n + 1 for n in range(31)]


def get_months():
	return [{'name': get_month_name(n + 1), 'month': n + 1 } for n in range(12)]


def get_years():
	return [n + 1 for n in range(2018, time.localtime().tm_year)]


def get_dates_range(start_date, end_date):
	delta = end_date - start_date
	return [start_date + timedelta(days=d) for d in range(delta.days + 1)]				


def get_months_range(start_date, end_date):
	months = OrderedDict((((start + timedelta(_)).strftime('%Y'), None), ((start + timedelta(_)).strftime('%m'), None)) for _ in xrange((start_date - end_date).days)).keys()
	return sorted(list(dict.fromkeys(list(map(lambda date: tuple(date.strftime('%Y-%m').split('-')), get_dates_range(start_date, end_date))))), reverse=True)


def render_to_pdf(template_src, context_dict={}):
	
	template = get_template(template_src)
	html  = template.render(context_dict)
	
	result = BytesIO()
	pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
	
	if not pdf.err:
		return HttpResponse(result.getvalue(), content_type='application/pdf')
	
	return None


def generate_incomes_dict(date, bills, date_type, format_date=True):
	
	if date_type == 1:
		date_string = date.strftime('%d %B, %Y') if format_date == True else date.strftime('%Y-%m-%d')
	elif date_type == 2:
		date_string = '%s, %s' % (get_month_name(date[1]), date[0]) if format_date == True else '-'.join(date)
	else:
		date_string = date

	try:
		return {
				'date': date_string,
				'count': bills.count(), 
				'amount': sum(list(map(lambda bill: bill.amount, bills))),
				'discount': sum(list(map(lambda bill: bill.discount, bills))),
				'count_discount': bills.filter(discount__gt=0).count(),
				'extras': sum(list(map(lambda bill: bill.extras_total, bills))),
				'count_extras': bills.filter(extras_total__gt=0).count(),
				'tips': sum(list(map(lambda bill: bill.tips, bills))),
				'count_tips': bills.filter(tips__gt=0).count(),
				'total': sum(list(map(lambda bill: bill.total, bills)))
			}
	except Exception as e:
		return {
				'date': date_string,
				'count': len(bills), 
				'amount': sum(list(map(lambda bill: bill.amount, bills))),
				'discount': sum(list(map(lambda bill: bill.discount, bills))),
				'count_discount': 0,
				'extras': sum(list(map(lambda bill: bill.extras_total, bills))),
				'count_extras': 0,
				'tips': sum(list(map(lambda bill: bill.tips, bills))),
				'count_tips': 0,
				'total': sum(list(map(lambda bill: bill.total, bills)))
			}


def generate_orders_dict(date, orders, date_type, format_date=True):
	
	if date_type == 1:
		date_string = date.strftime('%d %B, %Y') if format_date == True else date.strftime('%Y-%m-%d')
	elif date_type == 2:
		date_string = '%s, %s' % (get_month_name(date[1]), date[0]) if format_date == True else '-'.join(date)
	else:
		date_string = date

	return {
			'date': date_string,
			'count': orders.count(),
			'quantity':  sum(list(map(lambda order: order.quantity, orders))),
			'total': sum(list(map(lambda order: order.total, orders))),
			'price': sum(list(map(lambda order: order.price, orders))) / orders.count() if orders.count() > 0 else 0
		}