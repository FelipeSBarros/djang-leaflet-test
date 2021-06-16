from django.core.exceptions import ValidationError


def validate_longitude(lon):
    if lon < -44.887212 or lon > -40.95975:
        raise ValidationError("Coordenada longitude fora do contexto do estado do Rio de Janeiro", "erro longitude")

def validate_latitude(lat):
    if lat < -23.366868 or lat > -20.764962:
        raise ValidationError("Coordenada latitude fora do contexto do estado do Rio de Janeiro", "erro latitude")