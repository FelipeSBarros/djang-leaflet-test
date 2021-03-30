from django.test import TestCase
from mapProj.core.models import Fenomeno
from djgeojson.fields import PointField


class ModelGeomTest(TestCase):
    def setUp(self):
        self.fenomeno = Fenomeno.objects.create(
            name='Arvore',
            data='2020-11-06',
            hora='09:30:00',
            geom={'type': 'Point', 'coordinates': [0, 0]}
        )

    def test_create(self):
        self.assertTrue(Fenomeno.objects.exists())


    def test_geom_is_Point(self):
        self.assertEqual(self.fenomeno.geom.get("type"), "Point")
