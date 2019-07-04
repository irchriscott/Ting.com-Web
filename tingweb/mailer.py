from __future__ import unicode_literals
from django.core.mail import send_mail
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

class SendAdminRegistrationMail(object):

	def __init__(self, email, context):
		self.email = email
		self.subject = '[Ting.com] Administrator Credintials'
		self.context = context
		self.template = 'emails/admin_sign_up.html'


	def send(self):
		html_content = render_to_string(self.template, self.context)
		text_content = strip_tags(html_content)

		message = EmailMultiAlternatives(self.subject, text_content, settings.EMAIL_HOST_USER, [self.email])
		message.attach_alternative(html_content, 'text/html')
		message.send()


class SendAdminResetPasswordMail(object):

	def __init__(self, email, context):
		self.email = email
		self.subject = '[Ting.com] Administrator Reset Password Link'
		self.context = context
		self.template = 'emails/admin_reset_password.html'


	def send(self):
		html_content = render_to_string(self.template, self.context)
		text_content = strip_tags(html_content)

		message = EmailMultiAlternatives(self.subject, text_content, settings.EMAIL_HOST_USER, [self.email])
		message.attach_alternative(html_content, 'text/html')
		message.send()


class SendAdminSuccessResetPasswordMail(object):

	def __init__(self, email, context):
		self.email = email
		self.subject = '[Ting.com] Administrator Password Reset'
		self.context = context
		self.template = 'emails/admin_success_reset_password.html'


	def send(self):
		html_content = render_to_string(self.template, self.context)
		text_content = strip_tags(html_content)

		message = EmailMultiAlternatives(self.subject, text_content, settings.EMAIL_HOST_USER, [self.email])
		message.attach_alternative(html_content, 'text/html')
		message.send()


class SendUserResetPasswordMail(object):

	def __init__(self, email, context):
		self.email = email
		self.subject = '[Ting.com] User Reset Password Link'
		self.context = context
		self.template = 'emails/user_reset_password.html'


	def send(self):
		html_content = render_to_string(self.template, self.context)
		text_content = strip_tags(html_content)

		message = EmailMultiAlternatives(self.subject, text_content, settings.EMAIL_HOST_USER, [self.email])
		message.attach_alternative(html_content, 'text/html')
		message.send()


class SendUserSuccessResetPasswordMail(object):

	def __init__(self, email, context):
		self.email = email
		self.subject = '[Ting.com] User Password Reset'
		self.context = context
		self.template = 'emails/user_success_reset_password.html'


	def send(self):
		html_content = render_to_string(self.template, self.context)
		text_content = strip_tags(html_content)

		message = EmailMultiAlternatives(self.subject, text_content, settings.EMAIL_HOST_USER, [self.email])
		message.attach_alternative(html_content, 'text/html')


class SendUserUpdateEmailMail(object):

	def __init__(self, email, context):
		self.email = email
		self.subject = '[Ting.com] New Email'
		self.context = context
		self.template = 'emails/user_update_email.html'


	def send(self):
		html_content = render_to_string(self.template, self.context)
		text_content = strip_tags(html_content)

		message = EmailMultiAlternatives(self.subject, text_content, settings.EMAIL_HOST_USER, [self.email])
		message.attach_alternative(html_content, 'text/html')
		message.send()