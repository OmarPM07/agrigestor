from fastapi import APIRouter, HTTPException, Depends, status
from api.v1.schemas.insumos import (
    InsumoCrear, InsumoActualizar,
    InsumoRespuesta, ResumenCostosRespuesta
)
from api.dependencies import get_usuario_actual

router = APIRouter(prefix='/parcelas', tags=['Insumos'])


def get_parcela_o_404(parcela_id: int, usuario):
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
    from apps.cultivos.models import Cultivo
    try:
        return Cultivo.objects.get(id=cultivo_id, parcela=parcela)
    except Cultivo.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Cultivo no encontrado'
        )


@router.get(
    '/{parcela_id}/cultivos/{cultivo_id}/insumos/',
    response_model=list[InsumoRespuesta]
)
def listar_insumos(
    parcela_id: int,
    cultivo_id: int,
    usuario=Depends(get_usuario_actual)
):
    """Lista todas las aplicaciones de insumos de un cultivo."""
    parcela = get_parcela_o_404(parcela_id, usuario)
    cultivo = get_cultivo_o_404(cultivo_id, parcela)
    return list(cultivo.aplicaciones.all())


@router.post(
    '/{parcela_id}/cultivos/{cultivo_id}/insumos/',
    response_model=InsumoRespuesta,
    status_code=status.HTTP_201_CREATED
)
def crear_insumo(
    parcela_id: int,
    cultivo_id: int,
    datos: InsumoCrear,
    usuario=Depends(get_usuario_actual)
):
    """Registra una nueva aplicación de insumo en un cultivo."""
    from apps.insumos.models import AplicacionInsumo
    parcela = get_parcela_o_404(parcela_id, usuario)
    cultivo = get_cultivo_o_404(cultivo_id, parcela)

    if cultivo.estado == 'finalizado':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='No se pueden agregar insumos a un cultivo finalizado'
        )

    insumo = AplicacionInsumo(
        cultivo          = cultivo,
        registrado_por   = usuario,
        tipo             = datos.tipo,
        nombre_producto  = datos.nombre_producto,
        fecha_aplicacion = datos.fecha_aplicacion,
        dosis_por_ha     = datos.dosis_por_ha,
        unidad_dosis     = datos.unidad_dosis,
        costo_total      = datos.costo_total,
        observaciones    = datos.observaciones or '',
    )
    insumo.save()
    return insumo


@router.get(
    '/{parcela_id}/cultivos/{cultivo_id}/insumos/{insumo_id}/',
    response_model=InsumoRespuesta
)
def obtener_insumo(
    parcela_id: int,
    cultivo_id: int,
    insumo_id:  int,
    usuario=Depends(get_usuario_actual)
):
    """Obtiene el detalle de una aplicación de insumo."""
    from apps.insumos.models import AplicacionInsumo
    parcela = get_parcela_o_404(parcela_id, usuario)
    cultivo = get_cultivo_o_404(cultivo_id, parcela)
    try:
        return AplicacionInsumo.objects.get(
            id=insumo_id, cultivo=cultivo
        )
    except AplicacionInsumo.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Insumo no encontrado'
        )


@router.patch(
    '/{parcela_id}/cultivos/{cultivo_id}/insumos/{insumo_id}/',
    response_model=InsumoRespuesta
)
def actualizar_insumo(
    parcela_id: int,
    cultivo_id: int,
    insumo_id:  int,
    datos: InsumoActualizar,
    usuario=Depends(get_usuario_actual)
):
    """Actualiza uno o varios campos de una aplicación de insumo."""
    from apps.insumos.models import AplicacionInsumo
    parcela = get_parcela_o_404(parcela_id, usuario)
    cultivo = get_cultivo_o_404(cultivo_id, parcela)
    try:
        insumo = AplicacionInsumo.objects.get(
            id=insumo_id, cultivo=cultivo
        )
    except AplicacionInsumo.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Insumo no encontrado'
        )

    campos = datos.model_dump(exclude_none=True)
    for campo, valor in campos.items():
        setattr(insumo, campo, valor)
    insumo.save()
    return insumo


@router.delete(
    '/{parcela_id}/cultivos/{cultivo_id}/insumos/{insumo_id}/',
    status_code=status.HTTP_204_NO_CONTENT
)
def eliminar_insumo(
    parcela_id: int,
    cultivo_id: int,
    insumo_id:  int,
    usuario=Depends(get_usuario_actual)
):
    """Elimina una aplicación de insumo."""
    from apps.insumos.models import AplicacionInsumo
    parcela = get_parcela_o_404(parcela_id, usuario)
    cultivo = get_cultivo_o_404(cultivo_id, parcela)
    try:
        insumo = AplicacionInsumo.objects.get(
            id=insumo_id, cultivo=cultivo
        )
    except AplicacionInsumo.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Insumo no encontrado'
        )
    insumo.delete()


@router.get(
    '/{parcela_id}/cultivos/{cultivo_id}/insumos/resumen/costos/',
    response_model=ResumenCostosRespuesta
)
def resumen_costos(
    parcela_id: int,
    cultivo_id: int,
    usuario=Depends(get_usuario_actual)
):
    """
    Devuelve el resumen económico del cultivo:
    - Costo total de insumos
    - Costo por hectárea
    - Desglose por tipo de insumo
    """
    from apps.insumos.models import AplicacionInsumo
    from django.db.models import Sum

    parcela = get_parcela_o_404(parcela_id, usuario)
    cultivo = get_cultivo_o_404(cultivo_id, parcela)

    # Desglose de costos agrupado por tipo de insumo
    desglose = {}
    tipos = AplicacionInsumo.objects.filter(
        cultivo=cultivo
    ).values('tipo').annotate(total=Sum('costo_total'))

    for item in tipos:
        desglose[item['tipo']] = float(item['total'])

    return {
        'cultivo_id':          cultivo.id,
        'especie':             cultivo.get_especie_display(),
        'parcela':             parcela.nombre,
        'superficie_has':      parcela.superficie_has,
        'costo_total_insumos': cultivo.costo_total_insumos,
        'costo_por_hectarea':  cultivo.costo_por_hectarea,
        'total_aplicaciones':  cultivo.aplicaciones.count(),
        'desglose_por_tipo':   desglose,
    }