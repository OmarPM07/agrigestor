from fastapi import APIRouter, HTTPException, Depends, status
from api.v1.schemas.parcelas import (
    ParcelaCrear, ParcelaActualizar, ParcelaRespuesta
)
from api.dependencies import get_usuario_actual

router = APIRouter(prefix='/parcelas', tags=['Parcelas'])

@router.get('/', response_model=list[ParcelaRespuesta])
def listar_parcelas(usuario=Depends(get_usuario_actual)):
    """Lista todas las parcelas activas del usuario autenticado."""
    from apps.parcelas.models import Parcela
    parcelas = Parcela.objects.filter(
        propietario=usuario, activa=True
    )
    return list(parcelas)

@router.post('/', response_model=ParcelaRespuesta, status_code=status.HTTP_201_CREATED)
def crear_parcela(datos: ParcelaCrear, usuario=Depends(get_usuario_actual)):
    """Registra una nueva parcela para el usuario autenticado."""
    from apps.parcelas.models import Parcela
    parcela = Parcela(
        propietario    = usuario,
        nombre         = datos.nombre,
        superficie_has = datos.superficie_has,
        tipo_suelo     = datos.tipo_suelo,
        municipio      = datos.municipio,
        localidad      = datos.localidad,
        latitud        = datos.latitud,
        longitud       = datos.longitud,
    )
    parcela.save()
    return parcela

@router.get('/{parcela_id}', response_model=ParcelaRespuesta)
def obtener_parcela(parcela_id: int, usuario=Depends(get_usuario_actual)):
    """Obtiene el detalle de una parcela específica."""
    from apps.parcelas.models import Parcela
    try:
        return Parcela.objects.get(
            id=parcela_id, propietario=usuario, activa=True
        )
    except Parcela.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Parcela no encontrada'
        )

@router.patch('/{parcela_id}', response_model=ParcelaRespuesta)
def actualizar_parcela(
    parcela_id: int,
    datos: ParcelaActualizar,
    usuario=Depends(get_usuario_actual)
):
    """Actualiza uno o varios campos de una parcela."""
    from apps.parcelas.models import Parcela
    try:
        parcela = Parcela.objects.get(
            id=parcela_id, propietario=usuario, activa=True
        )
    except Parcela.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Parcela no encontrada'
        )

    # Solo actualiza los campos que vienen en la petición
    campos = datos.model_dump(exclude_none=True)
    for campo, valor in campos.items():
        setattr(parcela, campo, valor)
    parcela.save()
    return parcela

@router.delete('/{parcela_id}', status_code=status.HTTP_204_NO_CONTENT)
def eliminar_parcela(parcela_id: int, usuario=Depends(get_usuario_actual)):
    """
    Soft delete — marca la parcela como inactiva.
    No se borra de la base de datos para preservar el historial.
    """
    from apps.parcelas.models import Parcela
    try:
        parcela = Parcela.objects.get(
            id=parcela_id, propietario=usuario, activa=True
        )
    except Parcela.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Parcela no encontrada'
        )
    parcela.activa = False
    parcela.save()