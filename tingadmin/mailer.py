from __future__ import unicode_literals
from django.core.mail import send_mail
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

class SendRestaurantRegistrationMail(object):

	def __init__(self, email, context):
		self.email = email
		self.subject = '[Ting.com] Restaurant Registration Credintials'
		self.context = context
		self.template = 'emails/restaurant_sign_up.html'


	def send(self):
		html_content = render_to_string(self.template, self.context)
		text_content = strip_tags(html_content)

		message = EmailMultiAlternatives(self.subject, text_content, settings.EMAIL_HOST_USER, [self.email])
		message.attach_alternative(html_content, 'text/html')
		message.send()
