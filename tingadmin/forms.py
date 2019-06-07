from __future__ import unicode_literals
from django import forms
from tingweb.models import Restaurant, Branch
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
		fields = ('name', 'motto', 'purpose', 'country', 'town', 'opening', 'closing',)


class BranchForm(forms.ModelForm):

	class Meta:
		model = Branch
		fields = ('address', 'country', 'town', 'longitude', 'latitude', 'place_id')