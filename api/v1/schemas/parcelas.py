from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal


class ParcelaCrear(BaseModel):
    nombre:         str = Field(..., min_length=2, max_length=100)
    superficie_has: Decimal = Field(..., gt=0)
    tipo_suelo:     str = Field(..., pattern='^(arcilloso|limoso|arenoso|franco|franco_arcilloso)$')
    municipio:      str = Field(..., min_length=2)
    localidad:      str = Field(..., min_length=2)
    latitud:        Optional[Decimal] = None
    longitud:       Optional[Decimal] = None

class ParcelaActualizar(BaseModel):
    nombre:         Optional[str]     = None
    superficie_has: Optional[Decimal] = None
    tipo_suelo:     Optional[str]     = None
    municipio:      Optional[str]     = None
    localidad:      Optional[str]     = None
    latitud:        Optional[Decimal] = None
    longitud:       Optional[Decimal] = None

class ParcelaRespuesta(BaseModel):
    id:                int
    nombre:            str
    superficie_has:    Decimal
    tipo_suelo:        str
    municipio:         str
    localidad:         str
    latitud:           Optional[Decimal]
    longitud:          Optional[Decimal]
    activa:            bool
    fecha_registro:    datetime
    propietario_id:    int

    class Config:
        from_attributes = True