from django.core.exceptions import ValidationError
from django.conf import settings


def validate_longitude(lon):
    if lon < settings.BOUNDING_BOX_LON_MIN or lon > settings.BOUNDING_BOX_LON_MAX:
        raise ValidationError("Coordenada longitude fora do contexto do estado do Rio de Janeiro", "erro longitude")

def validate_latitude(lat):
    if lat < settings.BOUNDING_BOX_LAT_MIN or lat > settings.BOUNDING_BOX_LAT_MAX:
        raise ValidationError("Coordenada latitude fora do contexto do estado do Rio de Janeiro", "erro latitude")
