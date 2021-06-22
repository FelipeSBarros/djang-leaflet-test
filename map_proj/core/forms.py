from django.core.exceptions import ValidationError
from django.forms import ModelForm, FloatField, HiddenInput
from geojson import Point

from map_proj.core.models import Fenomeno
from map_proj.core.validators import validate_longitude, validate_latitude


class FenomenoForm(ModelForm):
    longitude = FloatField(validators=[validate_longitude])
    latitude = FloatField(validators=[validate_latitude])
    class Meta:
        model = Fenomeno
        fields = ('nome', 'data', 'hora', 'latitude', 'longitude')
        widgets = {'geom': HiddenInput()}

    def clean(self):
        cleaned_data = super().clean()
        lon = cleaned_data.get('longitude')
        lat = cleaned_data.get('latitude')
        if all((lon, lat)):
            cleaned_data['geom'] = Point((lon, lat))
            if not cleaned_data['geom'].is_valid:
                raise ValidationError('Geometria inválida')
        return cleaned_data
