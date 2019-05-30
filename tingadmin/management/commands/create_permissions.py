# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.core.management.base import BaseCommand
from tingadmin.models import Permission
import tingadmin.permissions as permissions


class Command(BaseCommand):

	args = ''
	help = 'This Command Saves All Permissions'

	def _create_permissions(self):
		_permissions = permissions.permissions

		for permission in _permissions:
			_permission = Permission(
					title=permission['title'],
					category=permission['category'],
					permission=permission['permission']
				)
			_permission.save()

	def handle(self, *args, **options):
		self._create_permissions()