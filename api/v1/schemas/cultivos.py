from pydantic import BaseModel, Field, model_validator
from typing import Optional
from datetime import date, datetime
from decimal import Decimal


class CultivoCrear(BaseModel):
    especie:                str  = Field(..., pattern='^(maiz|frijol|sorgo|tomate|chile|mango|aguacate|cana|limon|naranja|pepino|calabaza|otro)$')
    variedad:               Optional[str]  = ''
    fecha_siembra:          date
    fecha_cosecha_esperada: Optional[date] = None
    observaciones:          Optional[str]  = ''

    @model_validator(mode='after')
    def validar_fechas(self):
        if (self.fecha_cosecha_esperada
                and self.fecha_cosecha_esperada <= self.fecha_siembra):
            raise ValueError(
                'La fecha de cosecha debe ser posterior a la de siembra.'
            )
        return self


class CultivoActualizarEstado(BaseModel):
    estado: str = Field(
        ...,
        pattern='^(planificado|siembra|desarrollo|floracion|cosecha|finalizado)$'
    )


class CultivoFinalizar(BaseModel):
    fecha_cosecha_real: date
    rendimiento_ton_ha: Decimal = Field(..., gt=0)
    precio_venta_ton:   Decimal = Field(..., gt=0)


class CultivoRespuesta(BaseModel):
    id:                     int
    parcela_id:             int
    especie:                str
    variedad:               str
    fecha_siembra:          date
    fecha_cosecha_esperada: Optional[date]
    fecha_cosecha_real:     Optional[date]
    rendimiento_ton_ha:     Optional[Decimal]
    precio_venta_ton:       Optional[Decimal]
    estado:                 str
    observaciones:          str
    fecha_registro:         datetime
    costo_total_insumos:    float
    costo_por_hectarea:     float

    class Config:
        from_attributes = True