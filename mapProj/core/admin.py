from django.contrib import admin
from mapProj.core.models import Fenomenos
from mapProj.core.forms import FenomenosForm

class FenomenoAdmin(admin.ModelAdmin):
    model = Fenomenos
    form = FenomenosForm

admin.site.register(Fenomenos, FenomenoAdmin)
