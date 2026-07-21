from django.contrib import admin
from .models import AplicacionInsumo

# Register your models here.

@admin.register(AplicacionInsumo)
class AplicaInsumoAdmin(admin.ModelAdmin):
    list_display = ["nombre_producto", "tipo", "cultivo", "fecha_aplicacion", "costo_total"]
    list_filter = ["tipo"]
    search_fields = ["nombre_producto", "cultivo__parcela__nombre"]

