from django.test import TestCase
from geojson import Point

from mapProj.core.models import Fenomenos
from mapProj.core.forms import FenomenosForm


class ModelGeomTest(TestCase):
    def setUp(self):
        self.fenomeno = Fenomenos.objects.create(
            nome='Arvore',
            data='2020-11-06',
            hora='09:30:00'
        )

    def test_create(self):
        self.assertTrue(Fenomenos.objects.exists())


class FenomenosFormTest(TestCase):
    def setUp(self):
        self.form = FenomenosForm({
            'nome': 'Teste',
            'data': '2020-01-01',
            'hora': '09:12:12',
            'longitude': -45,
            'latitude': -22})
        self.validation = self.form.is_valid()

    def test_form_is_valid(self):
        """"form must be valid"""
        self.assertTrue(self.validation)

    def test_geom(self):
        """after validating, geom have same values of longitude and latitude"""
        self.assertEqual(self.form.cleaned_data['geom'], Point(
            (self.form.cleaned_data['longitude'],
        self.form.cleaned_data['latitude'])))
