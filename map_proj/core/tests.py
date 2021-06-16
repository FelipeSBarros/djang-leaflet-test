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
            'longitude': -42,
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

class FenomenoFormValidatorsTest(TestCase):

    def update_values(self, **kwargs):
        validForm = {  # valid form
            'nome': 'Teste',
            'data': '2020-01-01',
            'hora': '09:12:12',
            'longitude': -42,
            'latitude': -21}

        finalData = dict(validForm, **kwargs)
        form = FenomenoForm(finalData)
        return form

    def test_max_longitude(self):
        form = self.update_values(longitude='-45')
        form.is_valid()
        self.assertEqual(form.errors["longitude"][0], 'Coordenada longitude fora do contexto do estado do Rio de Janeiro')

    def test_min_longitude(self):
        form = self.update_values(longitude='-40')
        form.is_valid()
        self.assertEqual(form.errors["longitude"][0], 'Coordenada longitude fora do contexto do estado do Rio de Janeiro')

    def test_max_latitude(self):
        form = self.update_values(latitude='-24')
        form.is_valid()
        self.assertEqual(form.errors["latitude"][0], 'Coordenada latitude fora do contexto do estado do Rio de Janeiro')

    def test_min_latitude(self):
        form = self.update_values(latitude='-19')
        form.is_valid()
        self.assertEqual(form.errors["latitude"][0], 'Coordenada latitude fora do contexto do estado do Rio de Janeiro')
