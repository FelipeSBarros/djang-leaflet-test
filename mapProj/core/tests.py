from django.test import TestCase
from mapProj.core.models import Fenomenos
from mapProj.core.forms import FenomenosForm


class ModelGeomTest(TestCase):
    def setUp(self):
        self.fenomeno = Fenomenos.objects.create(
            name='Arvore',
            data='2020-11-06',
            hora='09:30:00',
            longitude = 22.0,
            latitude = 22.0
        )

    def test_create(self):
        self.assertTrue(Fenomenos.objects.exists())


class FenomenosFormTest(TestCase):
    def setUp(self):
        self.form = FenomenosForm({
            'name': 'Teste',
            'data': '2020-01-01',
            'hora': '09:12:12',
            'longitude': -45,
            'latitude': -22})

    def test_geom_is_valid(self):
        """"geom Point must be valid"""
        validation = self.form.is_valid()
        self.assertTrue(validation)
