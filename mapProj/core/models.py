from django.db import models
from djgeojson.fields import PointField
from geojson import Point


class Fenomenos(models.Model):
    name = models.CharField(max_length=100,
                            verbose_name='Fenomeno mapeado')
    data = models.DateField(verbose_name='Data da observação')
    hora = models.TimeField()
    longitude = models.FloatField()
    latitude = models.FloatField()
    # geom = PointField(blank=True)

    @property
    def geom(self):
        return Point((self.longitude, self.latitude))
