from django.db import models
from django.core.validators import MinValueValidator
from apps.usuarios.models import Usuario

# Create your models here.
class Parcela(models.Model):
    TIPO_SUELO = [
        ("arcilloso", "Arcilloso"),
        ("limoso", "Limoso"),
        ("arenoso", "Arenoso"),
        ("franco", "Franco"),
        ("franco_arcilloso", "Franco arcilloso"),
    ]
    
    propietario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="parcelas")
    nombre = models.CharField(max_length=100)
    superficie_has = models.DecimalField(max_digits=8, decimal_places=2, validators=[MinValueValidator(0.01)])
    tipo_suelo = models.CharField(max_length=20, choices=TIPO_SUELO)
    estado = models.CharField(max_length=50, default="Nayarit")
    municipio = models.CharField(max_length=100)
    localidad = models.CharField(max_length=100)
    latitud = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitud = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    activa = models.BooleanField(default=True)
    
    class Meta:
        app_label = "parcelas"
        ordering = ["-fecha_registro"]
    
    def __str__(self):
        return f"{self.nombre} ({self.superficie_has} ha)"