from django.core.exceptions import ValidationError
from django.forms import ModelForm, HiddenInput, FloatField
from mapProj.core.models import Fenomenos
from geojson import Point


class FenomenosForm(ModelForm):
    longitude = FloatField()
    latitude = FloatField()
    class Meta:
        model = Fenomenos
        fields = ('nome', 'data', 'hora', 'latitude', 'longitude')
        # widgets = {
        #     'geom': HiddenInput(),
        # }

    def clean(self):
        cleaned_data = super().clean()
        lon = cleaned_data.get('longitude')
        lat = cleaned_data.get('latitude')
        cleaned_data['geom'] = Point((lon, lat))

        if not cleaned_data['geom'].is_valid:
            raise ValidationError('Geometria inválida')
        return cleaned_data
