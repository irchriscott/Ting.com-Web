# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.core.management.base import BaseCommand
from tingweb.models import Administrator, AdminPermission
import tingadmin.permissions as permissions


class Command(BaseCommand):

	args = ''
	help = 'This Command Assigns All Permissions To Super Admins'

	def _assign_permissions(self):
		admins = Administrator.objects.filter(admin_type=1)

		for admin in admins:
			if admin.permissions == None or len(admin.permissions) == 0:
				_permissions = AdminPermission(
						admin=Administrator.objects.get(pk=admin.pk),
						permissions=', '.join(permissions.admin_permissions)
					)
				_permissions.save()


	def handle(self, *args, **options):
		self._assign_permissions()