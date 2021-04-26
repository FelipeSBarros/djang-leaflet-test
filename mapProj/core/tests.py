from django.test import TestCase
from django.contrib.admin.sites import AdminSite
from mapProj.core.models import Fenomenos
from mapProj.core.admin import FenomenoAdmin
import geojson
from mapProj.core.forms import FenomenosForm

# TODO add lat/log no model, remove geom do admin, overwrite save method to pass geom the lat/lon values

# from . import admin
# from . import models

class ModelGeomTest(TestCase):
    def setUp(self):
        self.fenomeno = Fenomenos.objects.create(
            name='Arvore',
            data='2020-11-06',
            hora='09:30:00',
            longitude = 22.0,
            latitude = 22.0,
            # geom=geojson.Point((22, 22))
        )

    def test_create(self):
        self.assertTrue(Fenomenos.objects.exists())

    def test_geom(self):
        # geometry = geojson.Feature(geometry=self.fenomeno.geom)
        geometry = self.fenomeno.geom
        valid = geometry.is_valid
        self.assertTrue(valid)


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

# class TestPostAdmin(TestCase):
#     def test_create(self):
#         fenomeno = Fenomeno(
#             name='Arvore',
#             data='2020-11-06',
#             hora='09:30:00',
#             longitude=22.0,
#             latitude=22.0,
#             geom={'type': 'Point', 'coordinates': [0, 0]}
#         )
#         adm = FenomenoAdmin(model=Fenomeno, admin_site=AdminSite())
#         adm.save_model(obj=fenomeno, request=None, form=None, change=None)
        # some test assertions here
        # site = AdminSite()
        # fenomeno_admin = admin.FenomenoAdmin(models.Fenomeno, site)
        # result = fenomeno_admin.response_post_save_add(self, fenomeno)
        # self.assertTrue(Fenomeno.objects.exists())
