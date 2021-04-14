from django.contrib import admin
from mapProj.core.models import Fenomeno

class FenomenoAdmin(admin.ModelAdmin):
    model = Fenomeno

admin.site.register(Fenomeno, FenomenoAdmin)
