from django.core.exceptions import ValidationError
from django.conf import settings


def validate_longitude(lon):
    if lon < settings.PROJECT_BBOX['LON']['Min'] or lon > settings.PROJECT_BBOX['LON']['Max']:
        raise ValidationError("Coordenada longitude fora do contexto do estado do Rio de Janeiro", "erro longitude")

def validate_latitude(lat):
    if lat < settings.PROJECT_BBOX['LAT']['Min'] or lat > settings.PROJECT_BBOX['LAT']['Max']:
        raise ValidationError("Coordenada latitude fora do contexto do estado do Rio de Janeiro", "erro latitude")
