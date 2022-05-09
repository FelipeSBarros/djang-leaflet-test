from djgeojson.views import GeoJSONLayerView

from map_proj.core.models import Fenomeno


class FenomenoGeoJson(GeoJSONLayerView):
    model = Fenomeno
    properties = ("popup_content",)


fenomeno_geojson = FenomenoGeoJson.as_view()
