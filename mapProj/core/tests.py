from django.test import TestCase
from django.contrib.admin.sites import AdminSite
from mapProj.core.models import Fenomeno
from mapProj.core.admin import FenomenoAdmin
import geojson
# TODO add lat/log no model, remove geom do admin, overwrite save method to pass geom the lat/lon values

# from . import admin
# from . import models

class ModelGeomTest(TestCase):
    def setUp(self):
        self.fenomeno = Fenomeno.objects.create(
            name='Arvore',
            data='2020-11-06',
            hora='09:30:00',
            geom=geojson.Point((0, 0))
        )

    def test_create(self):
        self.assertTrue(Fenomeno.objects.exists())

    def test_geom(self):
        geometry = geojson.Feature(geometry=self.fenomeno.geom)
        valid = geometry.is_valid
        self.assertTrue(valid)

class TestPostAdmin(TestCase):
    def test_create(self):
        fenomeno = Fenomeno(
            name='Arvore',
            data='2020-11-06',
            hora='09:30:00',
            geom={'type': 'Point', 'coordinates': [0, 0]}
        )
        adm = FenomenoAdmin(model=Fenomeno, admin_site=AdminSite())
        adm.save_model(obj=fenomeno, request=None, form=None, change=None)
        # some test assertions here
        # site = AdminSite()
        # fenomeno_admin = admin.FenomenoAdmin(models.Fenomeno, site)
        # result = fenomeno_admin.response_post_save_add(self, fenomeno)
        # self.assertTrue(Fenomeno.objects.exists())
