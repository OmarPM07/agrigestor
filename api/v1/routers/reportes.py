from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional
from api.v1.schemas.reportes import (
    ReporteRendimientoRespuesta,
    ReporteCicloRespuesta,
    ReporteComparativaRespuesta,
    ResumenGeneralRespuesta,
)
from api.dependencies import get_usuario_actual

router = APIRouter(prefix='/reportes', tags=['Reportes'])


@router.get('/resumen/', response_model=ResumenGeneralRespuesta)
def resumen_general(usuario=Depends(get_usuario_actual)):
    """
    Panel general del agricultor:
    - Total de parcelas y superficie
    - Cultivos activos y finalizados
    - Ingreso total estimado y utilidad
    """
    from apps.parcelas.models import Parcela
    from apps.cultivos.models import Cultivo

    parcelas = Parcela.objects.filter(propietario=usuario, activa=True)
    cultivos = Cultivo.objects.filter(parcela__in=parcelas)
    finalizados = cultivos.filter(estado='finalizado')
    activos = cultivos.exclude(estado='finalizado').exclude(estado='planificado')

    ingreso_total  = 0.0
    costo_total    = 0.0
    utilidad_total = 0.0

    for cultivo in finalizados:
        if cultivo.rendimiento_ton_ha and cultivo.precio_venta_ton:
            sup     = float(cultivo.parcela.superficie_has)
            ingreso = float(cultivo.rendimiento_ton_ha) * sup * float(cultivo.precio_venta_ton)
            costo   = cultivo.costo_total_insumos
            ingreso_total  += ingreso
            costo_total    += costo
            utilidad_total += ingreso - costo

    return {
        'usuario':                usuario.get_full_name() or usuario.username,
        'total_parcelas':         parcelas.count(),
        'superficie_total_has':   float(sum(p.superficie_has for p in parcelas)),
        'total_cultivos':         cultivos.count(),
        'cultivos_activos':       activos.count(),
        'cultivos_finalizados':   finalizados.count(),
        'ingreso_total_estimado': round(ingreso_total, 2),
        'costo_total_insumos':    round(costo_total, 2),
        'utilidad_total_estimada': round(utilidad_total, 2),
    }


@router.get('/rendimiento/', response_model=list[ReporteRendimientoRespuesta])
def reporte_rendimiento(usuario=Depends(get_usuario_actual)):
    """
    Rendimiento por parcela:
    - Promedio de ton/ha en todos sus ciclos finalizados
    - Mejor cultivo registrado
    """
    from apps.parcelas.models import Parcela
    from django.db.models import Avg, Max

    parcelas = Parcela.objects.filter(propietario=usuario, activa=True)
    resultado = []

    for parcela in parcelas:
        finalizados = parcela.cultivos.filter(
            estado='finalizado',
            rendimiento_ton_ha__isnull=False
        )
        stats = finalizados.aggregate(
            promedio=Avg('rendimiento_ton_ha'),
            maximo=Max('rendimiento_ton_ha')
        )
        mejor = finalizados.filter(
            rendimiento_ton_ha=stats['maximo']
        ).first() if stats['maximo'] else None

        resultado.append({
            'parcela_id':           parcela.id,
            'parcela_nombre':       parcela.nombre,
            'municipio':            parcela.municipio,
            'superficie_has':       parcela.superficie_has,
            'total_ciclos':         parcela.cultivos.count(),
            'ciclos_finalizados':   finalizados.count(),
            'rendimiento_promedio': round(float(stats['promedio']), 2) if stats['promedio'] else None,
            'mejor_ciclo_especie':  mejor.get_especie_display() if mejor else None,
            'mejor_rendimiento':    round(float(stats['maximo']), 2) if stats['maximo'] else None,
        })

    return resultado


@router.get('/ciclo/{cultivo_id}/', response_model=ReporteCicloRespuesta)
def reporte_ciclo(
    cultivo_id: int,
    usuario=Depends(get_usuario_actual)
):
    """
    Reporte financiero completo de un ciclo:
    - Producción total en toneladas
    - Ingreso bruto
    - Costo total de insumos
    - Utilidad bruta y margen de utilidad
    """
    from apps.cultivos.models import Cultivo

    try:
        cultivo = Cultivo.objects.get(
            id=cultivo_id,
            parcela__propietario=usuario
        )
    except Cultivo.DoesNotExist:
        raise HTTPException(status_code=404, detail='Cultivo no encontrado')

    sup = float(cultivo.parcela.superficie_has)

    # Cálculos financieros
    produccion_total = None
    ingreso_bruto    = None
    utilidad_bruta   = None
    margen_pct       = None

    if cultivo.rendimiento_ton_ha and cultivo.precio_venta_ton:
        produccion_total = round(float(cultivo.rendimiento_ton_ha) * sup, 2)
        ingreso_bruto    = round(produccion_total * float(cultivo.precio_venta_ton), 2)
        costo            = cultivo.costo_total_insumos
        utilidad_bruta   = round(ingreso_bruto - costo, 2)
        margen_pct       = round((utilidad_bruta / ingreso_bruto) * 100, 2) if ingreso_bruto > 0 else 0

    return {
        'cultivo_id':           cultivo.id,
        'especie':              cultivo.get_especie_display(),
        'variedad':             cultivo.variedad,
        'parcela':              cultivo.parcela.nombre,
        'fecha_siembra':        cultivo.fecha_siembra,
        'fecha_cosecha_real':   cultivo.fecha_cosecha_real,
        'superficie_has':       cultivo.parcela.superficie_has,
        'rendimiento_ton_ha':   cultivo.rendimiento_ton_ha,
        'precio_venta_ton':     cultivo.precio_venta_ton,
        'produccion_total_ton': produccion_total,
        'ingreso_bruto':        ingreso_bruto,
        'costo_total_insumos':  cultivo.costo_total_insumos,
        'costo_por_hectarea':   cultivo.costo_por_hectarea,
        'utilidad_bruta':       utilidad_bruta,
        'margen_utilidad_pct':  margen_pct,
    }


@router.get('/comparativa/', response_model=ReporteComparativaRespuesta)
def reporte_comparativa(
    especie: str = Query(..., description='Especie a comparar: maiz, frijol, sorgo, etc.'),
    usuario=Depends(get_usuario_actual)
):
    """
    Comparativa de todos los ciclos de una misma especie:
    - Rendimiento máximo, mínimo y promedio
    - Costo promedio por hectárea
    - Utilidad promedio
    Útil para identificar qué parcela produce mejor esa especie.
    """
    from apps.cultivos.models import Cultivo
    from django.db.models import Avg, Max, Min

    cultivos = Cultivo.objects.filter(
        parcela__propietario=usuario,
        especie=especie,
        estado='finalizado',
        rendimiento_ton_ha__isnull=False
    )

    if not cultivos.exists():
        raise HTTPException(
            status_code=404,
            detail=f'No hay ciclos finalizados de {especie}'
        )

    stats = cultivos.aggregate(
        promedio=Avg('rendimiento_ton_ha'),
        maximo=Max('rendimiento_ton_ha'),
        minimo=Min('rendimiento_ton_ha'),
    )

    # Construye los ciclos con sus datos financieros
    ciclos = []
    ingreso_total  = 0.0
    utilidad_total = 0.0
    costo_total    = 0.0

    for cultivo in cultivos:
        sup = float(cultivo.parcela.superficie_has)
        produccion_total = None
        ingreso_bruto    = None
        utilidad_bruta   = None
        margen_pct       = None

        if cultivo.rendimiento_ton_ha and cultivo.precio_venta_ton:
            produccion_total = round(float(cultivo.rendimiento_ton_ha) * sup, 2)
            ingreso_bruto    = round(produccion_total * float(cultivo.precio_venta_ton), 2)
            costo            = cultivo.costo_total_insumos
            utilidad_bruta   = round(ingreso_bruto - costo, 2)
            margen_pct       = round((utilidad_bruta / ingreso_bruto) * 100, 2) if ingreso_bruto > 0 else 0
            ingreso_total    += ingreso_bruto
            utilidad_total   += utilidad_bruta
            costo_total      += costo

        ciclos.append({
            'cultivo_id':           cultivo.id,
            'especie':              cultivo.get_especie_display(),
            'variedad':             cultivo.variedad,
            'parcela':              cultivo.parcela.nombre,
            'fecha_siembra':        cultivo.fecha_siembra,
            'fecha_cosecha_real':   cultivo.fecha_cosecha_real,
            'superficie_has':       cultivo.parcela.superficie_has,
            'rendimiento_ton_ha':   cultivo.rendimiento_ton_ha,
            'precio_venta_ton':     cultivo.precio_venta_ton,
            'produccion_total_ton': produccion_total,
            'ingreso_bruto':        ingreso_bruto,
            'costo_total_insumos':  cultivo.costo_total_insumos,
            'costo_por_hectarea':   cultivo.costo_por_hectarea,
            'utilidad_bruta':       utilidad_bruta,
            'margen_utilidad_pct':  margen_pct,
        })

    n = len(ciclos)
    return {
        'especie':              especie,
        'total_ciclos':         n,
        'rendimiento_promedio': round(float(stats['promedio']), 2) if stats['promedio'] else None,
        'rendimiento_maximo':   round(float(stats['maximo']), 2) if stats['maximo'] else None,
        'rendimiento_minimo':   round(float(stats['minimo']), 2) if stats['minimo'] else None,
        'costo_promedio_ha':    round(costo_total / n, 2) if n > 0 else None,
        'ingreso_promedio':     round(ingreso_total / n, 2) if n > 0 else None,
        'utilidad_promedio':    round(utilidad_total / n, 2) if n > 0 else None,
        'ciclos':               ciclos,
    }