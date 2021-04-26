from django.contrib import admin
from mapProj.core.models import Fenomenos

class FenomenoAdmin(admin.ModelAdmin):
    model = Fenomenos

admin.site.register(Fenomenos, FenomenoAdmin)
