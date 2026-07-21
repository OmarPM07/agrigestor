from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario

# Register your models here.

@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ["username", "email", "first_name", "last_name", "rol", "municipio"]
    list_filter = ["rol", "municipio"]
    fieldsets = UserAdmin.fieldsets + (
        ("Datos Agrigestor", {"fields": ("rol", "telefono", "municipio")}),
    )

