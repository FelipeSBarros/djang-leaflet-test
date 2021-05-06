from django.contrib import admin
from mapProj.core.models import Fenomeno
from mapProj.core.forms import FenomenoForm

class FenomenoAdmin(admin.ModelAdmin):
    model = Fenomeno
    form = FenomenoForm

admin.site.register(Fenomeno, FenomenoAdmin)
