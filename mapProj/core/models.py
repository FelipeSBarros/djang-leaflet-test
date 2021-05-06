from django.db import models
from djgeojson.fields import PointField


class Fenomeno(models.Model):
    nome = models.CharField(max_length=100,
                            verbose_name='Fenomeno mapeado')
    data = models.DateField(verbose_name='Data da observação')
    hora = models.TimeField()
    # longitude = models.FloatField()
    # latitude = models.FloatField()
    geom = PointField(blank=True)

    def __str__(self):
        return self.nome
