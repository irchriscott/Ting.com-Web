from __future__ import unicode_literals
from django.core.mail import send_mail
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags


class SendAdminRegistrationMail(object):

	def __init__(self, email, context):
		self.email = email
		self.subject = 'Administrator Credintials'
		self.context = context
		self.template = 'emails/admin_sign_up.html'


	def send(self):
		html_content = render_to_string(self.template, self.context)
		text_content = strip_tags(html_content)

		message = EmailMultiAlternatives(self.subject, text_content, 'Ting.com <%s>' % settings.EMAIL_HOST_USER, [self.email])
		message.attach_alternative(html_content, 'text/html')
		message.send(fail_silently=True)


class SendAdminResetPasswordMail(object):

	def __init__(self, email, context):
		self.email = email
		self.subject = 'Administrator Reset Password Link'
		self.context = context
		self.template = 'emails/admin_reset_password.html'


	def send(self):
		html_content = render_to_string(self.template, self.context)
		text_content = strip_tags(html_content)

		message = EmailMultiAlternatives(self.subject, text_content, 'Ting.com <%s>' % settings.EMAIL_HOST_USER, [self.email])
		message.attach_alternative(html_content, 'text/html')
		message.send(fail_silently=True)


class SendAdminSuccessResetPasswordMail(object):

	def __init__(self, email, context):
		self.email = email
		self.subject = 'Administrator Password Reset'
		self.context = context
		self.template = 'emails/admin_success_reset_password.html'


	def send(self):
		html_content = render_to_string(self.template, self.context)
		text_content = strip_tags(html_content)

		message = EmailMultiAlternatives(self.subject, text_content, 'Ting.com <%s>' % settings.EMAIL_HOST_USER, [self.email])
		message.attach_alternative(html_content, 'text/html')
		message.send(fail_silently=True)


class SendUserResetPasswordMail(object):

	def __init__(self, email, context):
		self.email = email
		self.subject = 'User Reset Password Link'
		self.context = context
		self.template = 'emails/user_reset_password.html'


	def send(self):
		html_content = render_to_string(self.template, self.context)
		text_content = strip_tags(html_content)

		message = EmailMultiAlternatives(self.subject, text_content, 'Ting.com <%s>' % settings.EMAIL_HOST_USER, [self.email])
		message.attach_alternative(html_content, 'text/html')
		message.send(fail_silently=True)


class SendUserSuccessResetPasswordMail(object):

	def __init__(self, email, context):
		self.email = email
		self.subject = 'User Password Reset'
		self.context = context
		self.template = 'emails/user_success_reset_password.html'


	def send(self):
		html_content = render_to_string(self.template, self.context)
		text_content = strip_tags(html_content)

		message = EmailMultiAlternatives(self.subject, text_content, 'Ting.com <%s>' % settings.EMAIL_HOST_USER, [self.email])
		message.attach_alternative(html_content, 'text/html')
		message.send(fail_silently=True)


class SendUserUpdateEmailMail(object):

	def __init__(self, email, context):
		self.email = email
		self.subject = 'New Email'
		self.context = context
		self.template = 'emails/user_update_email.html'


	def send(self):
		html_content = render_to_string(self.template, self.context)
		text_content = strip_tags(html_content)

		message = EmailMultiAlternatives(self.subject, text_content, 'Ting.com <%s>' % settings.EMAIL_HOST_USER, [self.email])
		message.attach_alternative(html_content, 'text/html')
		message.send(fail_silently=True)


class SendAcceptedReservationMail(object):

	def __init__(self, email, context):
		self.email = email
		self.subject = 'Reservation Status'
		self.context = context
		self.template = 'emails/reservation_accepted.html'


	def send(self):
		html_content = render_to_string(self.template, self.context)
		text_content = strip_tags(html_content)

		message = EmailMultiAlternatives(self.subject, text_content, 'Ting.com <%s>' % settings.EMAIL_HOST_USER, [self.email])
		message.attach_alternative(html_content, 'text/html')
		message.send(fail_silently=True)


class SendDeclinedReservationMail(object):

	def __init__(self, email, context):
		self.email = email
		self.subject = 'Reservation Status'
		self.context = context
		self.template = 'emails/reservation_declined.html'


	def send(self):
		html_content = render_to_string(self.template, self.context)
		text_content = strip_tags(html_content)

		message = EmailMultiAlternatives(self.subject, text_content, 'Ting.com <%s>' % settings.EMAIL_HOST_USER, [self.email])
		message.attach_alternative(html_content, 'text/html')
		message.send(fail_silently=True)