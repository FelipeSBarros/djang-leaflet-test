from djgeojson.views import GeoJSONLayerView

from map_proj.core.models import Fenomeno


class FenomenoGeoJson(GeoJSONLayerView):
    model = Fenomeno
    properties = ('popup_content',)

    def get_queryset(self):
        context = Fenomeno.objects.all()
        return context


fenomeno_geojson = FenomenoGeoJson.as_view()
