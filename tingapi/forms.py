from __future__ import unicode_literals
from django import forms
from tingweb.models import MomentMedia

class MomentMediaForm(forms.ModelForm):

	class Meta:
		model = MomentMedia
		fields = ('media_type', 'media', 'text')