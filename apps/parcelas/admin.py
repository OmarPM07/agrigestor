from django.contrib import admin
from .models import Parcela

# Register your models here.

@admin.register(Parcela)
class ParcelaAdmin(admin.ModelAdmin):
    list_display = ["nombre", "propietario", "superficie_has", "estado", "municipio", "tipo_suelo", "activa"]
    list_filter = ["estado", "municipio", "tipo_suelo", "activa"]
    search_fields = ["nombre", "propietario__username", "localida"]
    