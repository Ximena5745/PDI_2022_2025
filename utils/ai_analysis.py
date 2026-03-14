"""
utils/ai_analysis.py — Shim de compatibilidad.

Toda la lógica real ha migrado a:
  - ai/gemini_provider.py   → GeminiProvider
  - ai/static_provider.py   → StaticProvider
  - ai/prompts.py           → prompts centralizados
  - services/ai_service.py  → AIService (orquestación)

Este archivo re-exporta las funciones originales para que los imports
legacy de las views sigan funcionando sin cambios.
"""

import streamlit as st
import pandas as pd
from services.ai_service import AIService
from services.analytics_service import AnalyticsService

_ai = AIService()
_svc = AnalyticsService()


@st.cache_data(ttl=3600, show_spinner=False)
def generar_analisis_general(metricas_dict: dict, cumplimiento_por_linea: list) -> str:
    return _ai.analisis_general(metricas_dict, cumplimiento_por_linea)


@st.cache_data(ttl=3600, show_spinner=False)
def generar_analisis_linea(
    nombre_linea: str,
    total_indicadores: int,
    cumplimiento_promedio: float,
    objetivos_data: list,
    indicadores_data: list | None = None,
) -> str:
    return _ai.analisis_linea(
        nombre_linea, total_indicadores, cumplimiento_promedio,
        objetivos_data, indicadores_data,
    )


@st.cache_data(ttl=3600, show_spinner=False)
def generar_analisis_indicador(
    nombre_indicador: str,
    linea: str,
    descripcion: str,
    historico_data: list,
    sentido: str = "Creciente",
) -> str:
    return _ai.analisis_indicador(
        nombre_indicador, linea, descripcion, historico_data, sentido
    )


def preparar_historico_para_analisis(df_indicador: pd.DataFrame) -> list:
    return _svc.preparar_historico_para_ia(df_indicador)


def preparar_objetivos_para_analisis(df_linea: pd.DataFrame, año=None) -> list:
    return _svc.preparar_objetivos_para_ia(df_linea, año)


def preparar_lineas_para_analisis(df_unificado: pd.DataFrame, año=None) -> list:
    return _svc.preparar_lineas_para_ia(df_unificado, año)
