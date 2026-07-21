from django.db import models
from django.core.validators import MinValueValidator
from apps.parcelas.models import Parcela

# Create your models here.

class Cultivo(models.Model):
    ESTADO = [
        ('planificado', 'Planificado'),
        ('siembra',     'En siembra'),
        ('desarrollo',  'En desarrollo'),
        ('floracion',   'En floración'),
        ('cosecha',     'Listo para cosecha'),
        ('finalizado',  'Finalizado'),
    ]
    
    ESPECIE = [
        ('maiz',     'Maíz'),     ('frijol',   'Frijol'),
        ('sorgo',    'Sorgo'),    ('tomate',   'Tomate'),
        ('chile',    'Chile'),    ('mango',    'Mango'),
        ('aguacate', 'Aguacate'), ('cana',     'Caña de azúcar'),
        ('limon',    'Limón'),    ('naranja',  'Naranja'),
        ('pepino',   'Pepino'),   ('calabaza', 'Calabaza'),
        ('otro',     'Otro'),
    ]
    
    parcela = models.ForeignKey(Parcela, on_delete=models.CASCADE, related_name='cultivos')
    especie = models.CharField(max_length=30, choices=ESPECIE)
    variedad = models.CharField(max_length=100, blank=True)
    fecha_siembra = models.DateField()
    fecha_cosecha_esperada = models.DateField(null=True, blank=True)
    fecha_cosecha_real = models.DateField(null=True, blank=True)
    rendimiento_ton_ha = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0)])
    precio_venta_ton = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADO, default="planificado")
    observaciones = models.TextField(blank=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        app_label = "cultivos"
        ordering = ["-fecha_siembra"]
    
    def __str__(self):
        return f"{self.get_especie_display()} - {self.parcela.nombre}"
    
    @property
    def costo_total_insumos(self):
        from django.db.models import Sum
        return float(self.aplicaciones.aggregate(total=Sum('costo_total'))['total'] or 0)
    
    @property 
    def costo_por_hectarea(self):
        sup = float(self.parcela.superficie_has)
        return round(self.costo_total_insumos / sup, 2) if sup > 0 else 0
       
