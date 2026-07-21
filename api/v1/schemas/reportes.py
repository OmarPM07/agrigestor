from pydantic import BaseModel
from typing import Optional
from datetime import date
from decimal import Decimal


class ReporteRendimientoRespuesta(BaseModel):
    parcela_id:            int
    parcela_nombre:        str
    municipio:             str
    superficie_has:        Decimal
    total_ciclos:          int
    ciclos_finalizados:    int
    rendimiento_promedio:  Optional[float]
    mejor_ciclo_especie:   Optional[str]
    mejor_rendimiento:     Optional[float]


class ReporteCicloRespuesta(BaseModel):
    cultivo_id:            int
    especie:               str
    variedad:              str
    parcela:               str
    fecha_siembra:         date
    fecha_cosecha_real:    Optional[date]
    superficie_has:        Decimal
    rendimiento_ton_ha:    Optional[Decimal]
    precio_venta_ton:      Optional[Decimal]
    produccion_total_ton:  Optional[float]
    ingreso_bruto:         Optional[float]
    costo_total_insumos:   float
    costo_por_hectarea:    float
    utilidad_bruta:        Optional[float]
    margen_utilidad_pct:   Optional[float]


class ReporteComparativaRespuesta(BaseModel):
    especie:               str
    total_ciclos:          int
    rendimiento_promedio:  Optional[float]
    rendimiento_maximo:    Optional[float]
    rendimiento_minimo:    Optional[float]
    costo_promedio_ha:     Optional[float]
    ingreso_promedio:      Optional[float]
    utilidad_promedio:     Optional[float]
    ciclos:                list[ReporteCicloRespuesta]


class ResumenGeneralRespuesta(BaseModel):
    usuario:               str
    total_parcelas:        int
    superficie_total_has:  float
    total_cultivos:        int
    cultivos_activos:      int
    cultivos_finalizados:  int
    ingreso_total_estimado: float
    costo_total_insumos:   float
    utilidad_total_estimada: float