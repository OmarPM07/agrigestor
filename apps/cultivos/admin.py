from django.contrib import admin
from .models import Cultivo

# Register your models here.

@admin.register(Cultivo)
class CultivoAdmin(admin.ModelAdmin):
    list_display = ["especie", "variedad", "parcela", "fecha_siembra", "estado"]
    list_filter = ["especie", "estado"]
    search_fields = ["parcela__nombre", "variedad"]