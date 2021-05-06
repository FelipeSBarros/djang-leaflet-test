from django.test import TestCase
from geojson import Point

from map_proj.core.models import Fenomeno
from map_proj.core.forms import FenomenoForm


class ModelGeomTest(TestCase):
    def setUp(self):
        self.fenomeno = Fenomeno.objects.create(
            nome='Arvore',
            data='2020-11-06',
            hora='09:30:00'
        )

    def test_create(self):
        self.assertTrue(Fenomeno.objects.exists())


class FenomenoFormTest(TestCase):
    def setUp(self):
        self.form = FenomenoForm({
            'nome': 'Teste',
            'data': '2020-01-01',
            'hora': '09:12:12',
            'longitude': -45,
            'latitude': -22})
        self.validation = self.form.is_valid()

    def test_form_is_valid(self):
        """"form must be valid"""
        self.assertTrue(self.validation)

    def test_geom_coordinates(self):
        """after validating, geom have same values of longitude and latitude"""
        self.assertEqual(self.form.cleaned_data['geom'], Point(
            (self.form.cleaned_data['longitude'],
        self.form.cleaned_data['latitude'])))

    def test_geom_is_valid(self):
        """geom must be valid"""
        self.assertTrue(self.form.cleaned_data['geom'].is_valid)
