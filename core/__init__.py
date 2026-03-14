"""
core — Lógica de negocio pura del Dashboard Estratégico POLI.
Sin dependencias de Streamlit.
"""

from core.config import COLORS, COLORES_LINEAS, LINEAS_ESTRATEGICAS, OBJETIVO_STANDBY
from core.models import (
    MetricasGenerales,
    CumplimientoLinea,
    CumplimientoObjetivo,
    EstadoProyectos,
    PuntoHistorico,
    MetadatosIndicador,
    FilaCascada,
)
from core.calculations import (
    calcular_cumplimiento,
    obtener_color_semaforo,
    obtener_estado_semaforo,
    es_objetivo_standby,
    cumplimiento_jerarquico,
)
from core.filters import (
    filtrar_por_linea,
    filtrar_por_objetivo,
    filtrar_indicadores,
    filtrar_proyectos,
    excluir_standby,
    obtener_lista_indicadores,
    obtener_lista_objetivos,
    obtener_año_mas_reciente,
)
from core.repository import DataRepository, DataLoadError

__all__ = [
    # config
    "COLORS", "COLORES_LINEAS", "LINEAS_ESTRATEGICAS", "OBJETIVO_STANDBY",
    # models
    "MetricasGenerales", "CumplimientoLinea", "CumplimientoObjetivo",
    "EstadoProyectos", "PuntoHistorico", "MetadatosIndicador", "FilaCascada",
    # calculations
    "calcular_cumplimiento", "obtener_color_semaforo", "obtener_estado_semaforo",
    "es_objetivo_standby", "cumplimiento_jerarquico",
    # filters
    "filtrar_por_linea", "filtrar_por_objetivo", "filtrar_indicadores",
    "filtrar_proyectos", "excluir_standby", "obtener_lista_indicadores",
    "obtener_lista_objetivos", "obtener_año_mas_reciente",
    # repository
    "DataRepository", "DataLoadError",
]
