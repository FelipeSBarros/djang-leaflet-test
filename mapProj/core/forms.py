from django.core.exceptions import ValidationError
from django.forms import ModelForm, HiddenInput
from mapProj.core.models import Fenomenos
from geojson import Point


class FenomenosForm(ModelForm):
    class Meta:
        model = Fenomenos
        fields = '__all__'
        widgets = {
            'geom': HiddenInput(),
        }

    def clean(self):
        cleaned_data = super().clean()
        lon = cleaned_data.get('longitude')
        lat = cleaned_data.get('latitude')
        cleaned_data['geom'] = Point((lon, lat))
        if not cleaned_data['geom'].is_valid:
            raise ValidationError('Deu ruim')
        return cleaned_data
