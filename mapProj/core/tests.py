from django.test import TestCase
from mapProj.core.models import Fenomeno
# TODO add lat/log no model, rmeove geom do admin, sobreescrever o save para o geom receber valores do lat/long


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
