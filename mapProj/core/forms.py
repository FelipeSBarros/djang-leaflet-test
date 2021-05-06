from django.core.exceptions import ValidationError
from django.forms import ModelForm, FloatField
from mapProj.core.models import Fenomeno
from geojson import Point


class FenomenoForm(ModelForm):
    longitude = FloatField()
    latitude = FloatField()
    class Meta:
        model = Fenomeno
        fields = ('nome', 'data', 'hora', 'latitude', 'longitude')

    def clean(self):
        cleaned_data = super().clean()
        lon = cleaned_data.get('longitude')
        lat = cleaned_data.get('latitude')
        cleaned_data['geom'] = Point((lon, lat))

        if not cleaned_data['geom'].is_valid:
            raise ValidationError('Geometria inválida')
        return cleaned_data
