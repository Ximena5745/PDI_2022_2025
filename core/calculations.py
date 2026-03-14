"""
Funciones puras de cálculo del PDI.
Sin dependencias externas (solo stdlib + pandas).
Todas las funciones son deterministas y testeables de forma aislada.
"""

from __future__ import annotations

import pandas as pd
from typing import Optional, Tuple

from core.config import (
    COLORS,
    UMBRAL_CUMPLIDO,
    UMBRAL_ALERTA,
    OBJETIVO_STANDBY,
)


# ---------------------------------------------------------------------------
# Cálculo de cumplimiento
# ---------------------------------------------------------------------------
def calcular_cumplimiento(
    meta: float,
    ejecucion: float,
    sentido: str = "Creciente",
) -> Optional[float]:
    """
    Retorna el porcentaje de cumplimiento según el sentido del indicador.

    Sentido 'Creciente' (mayor es mejor): ejecucion / meta * 100
    Sentido 'Decreciente' (menor es mejor): penaliza si ejecucion > meta

    Returns None si meta es 0 o algún valor es NaN.
    """
    if pd.isna(meta) or pd.isna(ejecucion) or meta == 0:
        return None

    if sentido == "Decreciente":
        if ejecucion <= meta:
            return 100.0 + ((meta - ejecucion) / meta) * 100.0
        return (meta / ejecucion) * 100.0

    return (ejecucion / meta) * 100.0


# ---------------------------------------------------------------------------
# Semáforo
# ---------------------------------------------------------------------------
def obtener_color_semaforo(
    cumplimiento: Optional[float],
    es_standby: bool = False,
) -> str:
    """Retorna el color hex del semáforo según el cumplimiento."""
    if es_standby:
        return COLORS["standby"]
    if cumplimiento is None or pd.isna(cumplimiento):
        return COLORS["gray"]
    if cumplimiento >= UMBRAL_CUMPLIDO:
        return COLORS["success"]
    if cumplimiento >= UMBRAL_ALERTA:
        return COLORS["warning"]
    return COLORS["danger"]


def obtener_estado_semaforo(
    cumplimiento: Optional[float],
    es_standby: bool = False,
) -> Tuple[str, str]:
    """
    Retorna (etiqueta_texto, clave_color) del semáforo.
    Ejemplo: ('Meta cumplida', 'success')
    """
    if es_standby:
        return "Stand by", "standby"
    if cumplimiento is None or pd.isna(cumplimiento):
        return "Sin datos", "gray"
    if cumplimiento >= UMBRAL_CUMPLIDO:
        return "Meta cumplida", "success"
    if cumplimiento >= UMBRAL_ALERTA:
        return "Alerta", "warning"
    return "Peligro", "danger"


# ---------------------------------------------------------------------------
# Verificación de Stand by
# ---------------------------------------------------------------------------
def es_objetivo_standby(objetivo: Optional[str]) -> bool:
    """True si el objetivo corresponde al que está en pausa institucional."""
    if objetivo is None or (isinstance(objetivo, float) and pd.isna(objetivo)):
        return False
    return str(objetivo).strip().lower() == OBJETIVO_STANDBY.lower()


# ---------------------------------------------------------------------------
# Cálculo jerárquico: indicadores → objetivos → líneas
# ---------------------------------------------------------------------------
def cumplimiento_jerarquico(
    df: pd.DataFrame,
    col_cumplimiento: str = "Cumplimiento",
    col_objetivo: str = "Objetivo",
    col_linea: str = "Linea",
) -> float:
    """
    Calcula el cumplimiento global usando la jerarquía:
      1. Promedio de indicadores por objetivo
      2. Promedio de objetivos por línea
      3. Promedio de líneas = cumplimiento general

    Retorna 0.0 si el DataFrame está vacío o faltan columnas.
    """
    if df.empty or col_cumplimiento not in df.columns:
        return 0.0

    df = df.copy()
    df[col_cumplimiento] = df[col_cumplimiento].fillna(0)

    if col_objetivo in df.columns and col_linea in df.columns:
        por_objetivo = df.groupby([col_linea, col_objetivo])[col_cumplimiento].mean()
        por_linea = por_objetivo.groupby(level=0).mean()
        result = por_linea.mean()
    else:
        result = df[col_cumplimiento].mean()

    return round(float(result), 1) if pd.notna(result) else 0.0
