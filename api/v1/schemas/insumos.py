from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime
from decimal import Decimal


class InsumoCrear(BaseModel):
    tipo:             str = Field(
                          ...,
                          pattern='^(fertilizante|herbicida|insecticida|fungicida|riego|otro)$'
                      )
    nombre_producto:  str     = Field(..., min_length=2, max_length=150)
    fecha_aplicacion: date
    dosis_por_ha:     Decimal = Field(..., gt=0)
    unidad_dosis:     str     = Field(..., min_length=1, max_length=20)
    costo_total:      Decimal = Field(..., gt=0)
    observaciones:    Optional[str] = ''


class InsumoActualizar(BaseModel):
    tipo:             Optional[str]     = None
    nombre_producto:  Optional[str]     = None
    fecha_aplicacion: Optional[date]    = None
    dosis_por_ha:     Optional[Decimal] = None
    unidad_dosis:     Optional[str]     = None
    costo_total:      Optional[Decimal] = None
    observaciones:    Optional[str]     = None


class InsumoRespuesta(BaseModel):
    id:               int
    cultivo_id:       int
    registrado_por_id: Optional[int]
    tipo:             str
    nombre_producto:  str
    fecha_aplicacion: date
    dosis_por_ha:     Decimal
    unidad_dosis:     str
    costo_total:      Decimal
    observaciones:    str
    fecha_registro:   datetime

    class Config:
        from_attributes = True


class ResumenCostosRespuesta(BaseModel):
    cultivo_id:          int
    especie:             str
    parcela:             str
    superficie_has:      Decimal
    costo_total_insumos: float
    costo_por_hectarea:  float
    total_aplicaciones:  int
    desglose_por_tipo:   dict