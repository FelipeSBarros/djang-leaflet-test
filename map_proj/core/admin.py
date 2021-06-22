from django.contrib import admin
from map_proj.core.models import Fenomeno
from map_proj.core.forms import FenomenoForm

class FenomenoAdmin(admin.ModelAdmin):
    # model = Fenomeno
    form = FenomenoForm

admin.site.register(Fenomeno, FenomenoAdmin)
