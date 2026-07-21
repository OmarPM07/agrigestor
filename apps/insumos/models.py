from django.db import models
from apps.cultivos.models import Cultivo
from apps.usuarios.models import Usuario

# Create your models here.

class AplicacionInsumo(models.Model):
    TIPO = [
        ('fertilizante', 'Fertilizante'),
        ('herbicida',    'Herbicida'),
        ('insecticida',  'Insecticida'),
        ('fungicida',    'Fungicida'),
        ('riego',        'Riego'),
        ('otro',         'Otro'),
    ]
    
    cultivo = models.ForeignKey(Cultivo, on_delete=models.CASCADE, related_name="aplicaciones")
    registrado_por = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True)
    tipo = models.CharField(max_length=20, choices=TIPO)
    nombre_producto = models.CharField(max_length=150)
    fecha_aplicacion = models.DateField()
    dosis_por_ha = models.DecimalField(max_digits=8, decimal_places=2)
    unidad_dosis = models.CharField(max_length=20)
    costo_total = models.DecimalField(max_digits=10, decimal_places=2)
    observaciones = models.TextField(blank=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        app_label = "insumos"
        ordering = ["-fecha_aplicacion"]
    
    def __str__(self):
        return f"{self.get_tipo_display()} - {self.nombre_producto}"
    
    
