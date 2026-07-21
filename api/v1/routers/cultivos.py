from fastapi import APIRouter, HTTPException, Depends, status
from api.v1.schemas.cultivos import (
    CultivoCrear, CultivoActualizarEstado,
    CultivoFinalizar, CultivoRespuesta
)
from api.dependencies import get_usuario_actual

router = APIRouter(prefix='/parcelas', tags=['Cultivos'])


def get_parcela_o_404(parcela_id: int, usuario):
    """
    Reutilizable — obtiene una parcela verificando que
    pertenece al usuario autenticado.
    """
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


def get_cultivo_o_404(cultivo_id: int, parcela):
    """
    Reutilizable — obtiene un cultivo verificando que
    pertenece a la parcela indicada.
    """
    from apps.cultivos.models import Cultivo
    try:
        return Cultivo.objects.get(id=cultivo_id, parcela=parcela)
    except Cultivo.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Cultivo no encontrado'
        )


@router.get('/{parcela_id}/cultivos/', response_model=list[CultivoRespuesta])
def listar_cultivos(parcela_id: int, usuario=Depends(get_usuario_actual)):
    """Lista todos los cultivos de una parcela."""
    parcela = get_parcela_o_404(parcela_id, usuario)
    return list(parcela.cultivos.all())


@router.post(
    '/{parcela_id}/cultivos/',
    response_model=CultivoRespuesta,
    status_code=status.HTTP_201_CREATED
)
def crear_cultivo(
    parcela_id: int,
    datos: CultivoCrear,
    usuario=Depends(get_usuario_actual)
):
    """Registra un nuevo ciclo de cultivo en una parcela."""
    from apps.cultivos.models import Cultivo
    parcela = get_parcela_o_404(parcela_id, usuario)

    cultivo = Cultivo(
        parcela                = parcela,
        especie                = datos.especie,
        variedad               = datos.variedad or '',
        fecha_siembra          = datos.fecha_siembra,
        fecha_cosecha_esperada = datos.fecha_cosecha_esperada,
        observaciones          = datos.observaciones or '',
    )
    cultivo.save()
    return cultivo


@router.get('/{parcela_id}/cultivos/{cultivo_id}/', response_model=CultivoRespuesta)
def obtener_cultivo(
    parcela_id: int,
    cultivo_id: int,
    usuario=Depends(get_usuario_actual)
):
    """Obtiene el detalle de un cultivo con sus costos calculados."""
    parcela = get_parcela_o_404(parcela_id, usuario)
    return get_cultivo_o_404(cultivo_id, parcela)


@router.patch(
    '/{parcela_id}/cultivos/{cultivo_id}/estado/',
    response_model=CultivoRespuesta
)
def cambiar_estado(
    parcela_id: int,
    cultivo_id: int,
    datos: CultivoActualizarEstado,
    usuario=Depends(get_usuario_actual)
):
    """
    Avanza el estado fenológico del cultivo.
    planificado → siembra → desarrollo → floracion → cosecha → finalizado
    """
    parcela = get_parcela_o_404(parcela_id, usuario)
    cultivo = get_cultivo_o_404(cultivo_id, parcela)

    cultivo.estado = datos.estado
    cultivo.save()
    return cultivo


@router.patch(
    '/{parcela_id}/cultivos/{cultivo_id}/finalizar/',
    response_model=CultivoRespuesta
)
def finalizar_cultivo(
    parcela_id: int,
    cultivo_id: int,
    datos: CultivoFinalizar,
    usuario=Depends(get_usuario_actual)
):
    """
    Registra la cosecha real con rendimiento y precio de venta.
    Cambia el estado a 'finalizado' automáticamente.
    Con estos datos el sistema puede calcular ingreso bruto y utilidad.
    """
    parcela = get_parcela_o_404(parcela_id, usuario)
    cultivo = get_cultivo_o_404(cultivo_id, parcela)

    if cultivo.estado == 'finalizado':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Este cultivo ya está finalizado'
        )

    cultivo.fecha_cosecha_real = datos.fecha_cosecha_real
    cultivo.rendimiento_ton_ha = datos.rendimiento_ton_ha
    cultivo.precio_venta_ton   = datos.precio_venta_ton
    cultivo.estado             = 'finalizado'
    cultivo.save()
    return cultivo


@router.delete(
    '/{parcela_id}/cultivos/{cultivo_id}/',
    status_code=status.HTTP_204_NO_CONTENT
)
def eliminar_cultivo(
    parcela_id: int,
    cultivo_id: int,
    usuario=Depends(get_usuario_actual)
):
    """Elimina un cultivo. Solo se permite si está en estado planificado."""
    parcela = get_parcela_o_404(parcela_id, usuario)
    cultivo = get_cultivo_o_404(cultivo_id, parcela)

    if cultivo.estado != 'planificado':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Solo se pueden eliminar cultivos en estado planificado'
        )
    cultivo.delete()