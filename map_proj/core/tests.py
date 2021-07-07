from django.shortcuts import resolve_url as r
from django.test import TestCase
from geojson import Point
from django.conf import settings
from map_proj.core.forms import FenomenoForm
from map_proj.core.models import Fenomeno


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
    @staticmethod
    def create_form(**kwargs):
        valid_form = {
            'nome': 'Teste',
            'data': '2020-01-01',
            'hora': '09:12:12',
            'longitude': -42,
            'latitude': -21}

        valid_form.update(**kwargs)
        form = FenomenoForm(valid_form)
        return form

    def test_max_longitude_raises_error(self):
        form = self.create_form(longitude='-45')
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["longitude"][0], 'Coordenada longitude fora do contexto do estado do Rio de Janeiro')

    def test_min_longitude_raises_error(self):
        form = self.create_form(longitude='-40')
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["longitude"][0], 'Coordenada longitude fora do contexto do estado do Rio de Janeiro')

    def test_max_latitude_raises_error(self):
        form = self.create_form(latitude='-24')
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["latitude"][0], 'Coordenada latitude fora do contexto do estado do Rio de Janeiro')

    def test_min_latitude_raises_error(self):
        form = self.create_form(latitude='-19')
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["latitude"][0], 'Coordenada latitude fora do contexto do estado do Rio de Janeiro')


class FenomenoGeoJsonTest(TestCase):
    def setUp(self):
        self.form = Fenomeno.objects.create( # todo usar ORM passar direto ao banco para evitar efeito colateral
            nome='Teste',
            data='2020-01-01',
            hora='09:12:12',
            geom= {"type": "Point", "coordinates": [-42, -22]})

    def teste_geojson_status_code(self):
        self.resp = self.client.get(r('geojson'))
        self.assertEqual(200, self.resp.status_code)

    def teste_geojson_feature_collection(self):
        self.resp = self.client.get(r('geojson'))
        self.assertEqual(self.resp.json(), {"type": "FeatureCollection", "features": [{"type": "Feature", "properties": {"popup_content": "<p><strong><span>Nome: </span>Teste</strong></p>", "model": "core.fenomeno"}, "id": 1, "geometry": {"type": "Point", "coordinates": [-42.0, -22.0]}}], "crs": {"type": "name", "properties": {"name": "EPSG:4326"}}})
