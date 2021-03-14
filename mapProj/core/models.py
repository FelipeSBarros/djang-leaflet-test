from django.db import models
from djgeojson.fields import PointField


class FloraOccurrence(models.Model):

    species_name = models.CharField(max_length=100, verbose_name='Nomre de la especie', null=False)
    Observations = models.TextField(verbose_name='Observaciones')
    picture = models.ImageField()
    geom = PointField()

    def __str__(self):
        return self.species_name

    @property
    def picture_url(self):
        return self.picture.url
