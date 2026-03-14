"""
utils — Re-exports de compatibilidad.
Los nuevos módulos importan desde core/, services/ y ai/.
Este archivo mantiene los imports legacy funcionando durante la transición.
"""

# ── core ──
from core.config import COLORS, COLORES_LINEAS, LINEAS_ESTRATEGICAS, OBJETIVO_STANDBY
from core.calculations import (
    calcular_cumplimiento,
    obtener_color_semaforo,
    obtener_estado_semaforo,
    es_objetivo_standby,
)
from core.filters import (
    filtrar_por_linea,
    filtrar_por_objetivo,
    obtener_lista_indicadores,
    obtener_lista_objetivos,
)

# ── visualizations (se mantiene en utils/ por tamaño y dependencias Plotly) ──
from utils.visualizations import (
    crear_grafico_historico,
    crear_grafico_lineas,
    crear_grafico_semaforo,
    crear_grafico_proyectos,
)

# ── ai ──
from utils.ai_analysis import (
    generar_analisis_general,
    generar_analisis_linea,
    generar_analisis_indicador,
)

__all__ = [
    # config
    "COLORS", "COLORES_LINEAS", "LINEAS_ESTRATEGICAS", "OBJETIVO_STANDBY",
    # calculations
    "calcular_cumplimiento", "obtener_color_semaforo",
    "obtener_estado_semaforo", "es_objetivo_standby",
    # filters
    "filtrar_por_linea", "filtrar_por_objetivo",
    "obtener_lista_indicadores", "obtener_lista_objetivos",
    # visualizations
    "crear_grafico_historico", "crear_grafico_lineas",
    "crear_grafico_semaforo", "crear_grafico_proyectos",
    # ai
    "generar_analisis_general", "generar_analisis_linea", "generar_analisis_indicador",
]
