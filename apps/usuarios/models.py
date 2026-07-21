from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.

class Usuario(AbstractUser):
    ROL = [
        ('agricultor', 'Agricultor'),
        ('tecnico', 'Técnico de campo'),
        ('admin', 'Administrador'),
    ]
    rol = models.CharField(max_length=20, choices=ROL, default='agricultor')
    telefono = models.CharField(max_length=15, blank=True)
    municipio = models.CharField(max_length=100, blank=True)
    
    class Meta:
        app_label = 'usuarios'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.get_rol_display()})"


    