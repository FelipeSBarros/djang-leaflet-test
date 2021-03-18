from django.db import models
from djgeojson.fields import PointField


class FloraOccurrence(models.Model):

    species_name = models.CharField(max_length=100, verbose_name='Nomre de la especie', null=False)
    Observations = models.TextField(verbose_name='Observaciones')
    picture = models.ImageField()
    lon = models.FloatField(null=True, blank=True)
    lat = models.FloatField(null=True, blank=True)
    geom = PointField(null=True, blank=True)

    def __str__(self):
        return self.species_name

    @property
    def picture_url(self):
        return self.picture.url

    def save(self, *args, **kwargs):
        if self.lon is None or self.lat is None:
            self.geom = {'type': 'Point', 'coordinates': [0, 0]}
        else:
            self.geom = {'type': 'Point', 'coordinates': [self.lon, self.lat]}
        super(FloraOccurrence, self).save(*args, **kwargs)