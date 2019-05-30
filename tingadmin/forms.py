from __future__ import unicode_literals
from django import forms
from tingweb.models import Restaurant
from tingadmin.models import RestaurantCategory, TingPackage


class RestaurantCategoryForm(forms.ModelForm):

	class Meta:
		model = RestaurantCategory
		fields = ('name', 'country',)


class TingPackageForm(forms.ModelForm):

	class Meta:
		model = TingPackage
		fields = ('name', 'image', 'tables', 'menus', 'amount', 'currency',)


class RestaurantFormAdmin(forms.ModelForm):

	class Meta:
		model = Restaurant
		fields = ('name', 'branch', 'motto', 'country', 'town', 'address', 'latitude', 'longitude', 'place_id', 'opening', 'closing',)