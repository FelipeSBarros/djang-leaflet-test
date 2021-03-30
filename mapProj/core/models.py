from django.db import models
from djgeojson.fields import PointField


class Fenomeno(models.Model):
    name = models.CharField(max_length=100,
                            verbose_name='Fenomeno mapado')
    data = models.DateField(verbose_name='Data da observação')
    hora = models.TimeField()
    geom = PointField()
