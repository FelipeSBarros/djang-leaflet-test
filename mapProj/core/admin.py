from django.contrib import admin
from leaflet.admin import LeafletGeoAdmin
from mapProj.core.models import FloraOccurrence

admin.site.register(FloraOccurrence, LeafletGeoAdmin)
