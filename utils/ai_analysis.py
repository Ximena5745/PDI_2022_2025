"""
Módulo de análisis con IA (Google Gemini - GRATUITO) para el Dashboard Estratégico POLI.
Soporta análisis pre-generados desde archivo cache para evitar llamadas a la API.
"""

import os
import json
import streamlit as st
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Cache de análisis pre-generados
_analisis_cache = None


def cargar_cache_analisis():
    """
    Carga el cache de análisis pre-generados desde archivo JSON.
    """
    global _analisis_cache
    if _analisis_cache is not None:
        return _analisis_cache

    try:
        # Buscar archivo de cache
        base_path = Path(__file__).parent.parent
        cache_path = base_path / 'Data' / 'analisis_cache.json'

        if cache_path.exists():
            with open(cache_path, 'r', encoding='utf-8') as f:
                _analisis_cache = json.load(f)
            return _analisis_cache
    except Exception:
        pass

    _analisis_cache = {}
    return _analisis_cache


def obtener_analisis_cache(indicador_nombre):
    """
    Obtiene el análisis pre-generado de un indicador desde el cache.

    Returns:
        str o None: El análisis si existe, None si no está en cache.
    """
    cache = cargar_cache_analisis()
    if indicador_nombre in cache:
        return cache[indicador_nombre].get('analisis', None)
    return None


def get_gemini_client():
    """
    Obtiene el cliente de Google Gemini si está disponible.
    Gemini tiene un tier GRATUITO generoso (60 consultas/minuto).
    """
    try:
        from google import genai
        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            try:
                api_key = st.secrets.get("GOOGLE_API_KEY", None)
            except Exception:
                pass
        if api_key:
            return genai.Client(api_key=api_key)
        return None
    except ImportError:
        return None
    except Exception:
        return None


def generar_analisis_con_ia(prompt, max_tokens=1000):
    """
    Genera análisis usando la API de Google Gemini (GRATUITA).

    Args:
        prompt: El prompt a enviar a Gemini
        max_tokens: Máximo de tokens en la respuesta

    Returns:
        str: Texto del análisis o mensaje de error
    """
    client = get_gemini_client()

    if client is None:
        return generar_analisis_fallback(prompt)

    try:
        response = client.models.generate_content(
            model='models/gemini-2.0-flash',
            contents=prompt,
            config={
                'max_output_tokens': max_tokens,
                'temperature': 0.7
            }
        )
        return response.text
    except Exception as e:
        return f"⚠️ No se pudo generar el análisis con IA: {str(e)}\n\nPor favor configure GOOGLE_API_KEY en las variables de entorno."


def generar_analisis_fallback(prompt):
    """
    Genera un mensaje cuando la API no está disponible.
    """
    return """📊 **Análisis automático no disponible**

Para habilitar el análisis inteligente con IA (GRATUITO):

1. Ve a [aistudio.google.com](https://aistudio.google.com/app/apikey)
2. Crea una API Key gratuita
3. En Streamlit Cloud: Settings > Secrets, agrega:
   ```
   GOOGLE_API_KEY = "tu_api_key"
   ```
4. O localmente, crea un archivo `.env` con:
   ```
   GOOGLE_API_KEY=tu_api_key
   ```

**Google Gemini es GRATUITO** (60 consultas por minuto)."""


@st.cache_data(ttl=3600, show_spinner=False)
def generar_analisis_general(metricas_dict, cumplimiento_por_linea):
    """
    Genera el análisis general del dashboard.
    """
    lineas_texto = "\n".join([
        f"- {item['linea']}: {item['cumplimiento']:.1f}% ({item['indicadores']} indicadores)"
        for item in cumplimiento_por_linea
    ]) if cumplimiento_por_linea else "No hay datos disponibles"

    prompt = f"""Eres un analista estratégico del Politécnico Grancolombiano. Analiza los siguientes datos del Plan Estratégico Institucional (PDI) 2021-2025:

**Métricas Generales (Año {metricas_dict.get('año_actual', 2025)}):**
- Cumplimiento promedio general: {metricas_dict.get('cumplimiento_promedio', 0):.1f}%
- Total de indicadores activos: {metricas_dict.get('total_indicadores', 0)}
- Indicadores con meta cumplida (≥100%): {metricas_dict.get('metas_cumplidas', 0)}
- Indicadores en alerta (80-99%): {metricas_dict.get('en_progreso', 0)}
- Indicadores en peligro (<80%): {metricas_dict.get('requieren_atencion', 0)}

**Cumplimiento por Línea Estratégica:**
{lineas_texto}

Genera un RESUMEN EJECUTIVO de máximo 150 palabras que incluya:
1. Estado general del cumplimiento del PDI
2. Las 2 líneas estratégicas con mejor desempeño
3. Las líneas que requieren mayor atención
4. Una conclusión sobre la tendencia general

Usa un tono profesional, conciso y orientado a la acción. Escribe en español."""

    return generar_analisis_con_ia(prompt)


@st.cache_data(ttl=3600, show_spinner=False)
def generar_analisis_linea(nombre_linea, total_indicadores, cumplimiento_promedio, objetivos_data):
    """
    Genera análisis para una línea estratégica específica.
    """
    objetivos_texto = "\n".join([
        f"- {obj['objetivo']}: {obj['cumplimiento']:.1f}% ({obj['indicadores']} indicadores)"
        for obj in objetivos_data
    ]) if objetivos_data else "No hay datos de objetivos disponibles"

    prompt = f"""Eres un analista estratégico del Politécnico Grancolombiano. Analiza el desempeño de la siguiente línea estratégica del PDI 2021-2025:

**Línea Estratégica: {nombre_linea}**

**Datos Generales:**
- Total de indicadores: {total_indicadores}
- Cumplimiento promedio: {cumplimiento_promedio:.1f}%

**Objetivos y su Cumplimiento:**
{objetivos_texto}

Genera un ANÁLISIS de máximo 120 palabras que incluya:
1. Evaluación del estado actual de cumplimiento de la línea
2. Los objetivos con mejor desempeño (destacados)
3. Áreas de mejora identificadas
4. Una recomendación estratégica específica y accionable

Usa un tono profesional y enfocado en acciones concretas. Escribe en español."""

    return generar_analisis_con_ia(prompt)


@st.cache_data(ttl=3600, show_spinner=False)
def generar_analisis_indicador(nombre_indicador, linea, descripcion, historico_data, sentido="Creciente"):
    """
    Genera análisis detallado para un indicador específico.
    Primero busca en el cache de análisis pre-generados, si no existe genera con API.
    """
    # Primero intentar obtener del cache pre-generado
    analisis_cache = obtener_analisis_cache(nombre_indicador)
    if analisis_cache:
        return f"📊 **Análisis del Indicador**\n\n{analisis_cache}"

    # Si no está en cache, generar con API
    historico_texto = "\n".join([
        f"- {item['año']}{' (Linea Base)' if item['año'] == 2021 else ''}: Meta: {item['meta']:.2f}, Ejecucion: {item['ejecucion']:.2f}, Cumplimiento: {item['cumplimiento']:.1f}%"
        for item in historico_data
    ]) if historico_data else "No hay datos historicos disponibles"

    if historico_data and len(historico_data) >= 2:
        primer_cumpl = historico_data[0]['cumplimiento']
        ultimo_cumpl = historico_data[-1]['cumplimiento']
        variacion = ultimo_cumpl - primer_cumpl
        tendencia = "ascendente" if variacion > 5 else "descendente" if variacion < -5 else "estable"
    else:
        tendencia = "no determinada"
        variacion = 0

    prompt = f"""Eres un analista estrategico del Politecnico Grancolombiano. Analiza el siguiente indicador del PDI 2021-2025:

**Indicador:** {nombre_indicador}
**Linea Estrategica:** {linea}
**Descripcion:** {descripcion if descripcion else 'No disponible'}
**Sentido:** {sentido} (el indicador se considera positivo si {'aumenta' if sentido == 'Creciente' else 'disminuye'})

**Historico de Desempeno:**
{historico_texto}

**Tendencia calculada:** {tendencia} (variacion de {variacion:+.1f} puntos porcentuales desde la linea base)

Genera un ANALISIS de maximo 100 palabras que incluya:
1. Evaluacion de la tendencia desde la linea base (2021)
2. Evolucion del cumplimiento ano a ano
3. Identificacion de brechas significativas entre meta y ejecucion
4. Una recomendacion especifica y accionable para mejorar el indicador

Se conciso, profesional y enfocado en la accion. Escribe en espanol."""

    return generar_analisis_con_ia(prompt)


def preparar_historico_para_analisis(df_indicador):
    """
    Prepara los datos históricos de un indicador para el análisis con IA.
    """
    if df_indicador.empty:
        return []

    historico = []
    for _, row in df_indicador.sort_values('Año').iterrows():
        año = int(row['Año']) if 'Año' in row else None
        meta = float(row['Meta']) if 'Meta' in row and pd.notna(row['Meta']) else 0
        ejecucion = float(row['Ejecución']) if 'Ejecución' in row and pd.notna(row['Ejecución']) else 0

        if meta > 0:
            cumplimiento = (ejecucion / meta) * 100
        else:
            cumplimiento = 0

        historico.append({
            'año': año,
            'meta': meta,
            'ejecucion': ejecucion,
            'cumplimiento': cumplimiento
        })

    return historico


def preparar_objetivos_para_analisis(df_linea, año=None):
    """
    Prepara los datos de objetivos de una línea para el análisis con IA.
    """
    if df_linea.empty or 'Objetivo' not in df_linea.columns:
        return []

    if año and 'Año' in df_linea.columns:
        df_linea = df_linea[df_linea['Año'] == año]

    objetivos = []
    for objetivo in df_linea['Objetivo'].unique():
        df_obj = df_linea[df_linea['Objetivo'] == objetivo]

        cumplimiento = df_obj['Cumplimiento'].mean() if 'Cumplimiento' in df_obj.columns else 0
        indicadores = df_obj['Indicador'].nunique() if 'Indicador' in df_obj.columns else len(df_obj)

        objetivos.append({
            'objetivo': objetivo,
            'cumplimiento': cumplimiento if pd.notna(cumplimiento) else 0,
            'indicadores': indicadores
        })

    return sorted(objetivos, key=lambda x: x['cumplimiento'], reverse=True)


def preparar_lineas_para_analisis(df_unificado, año=None):
    """
    Prepara los datos de líneas estratégicas para el análisis general.
    """
    if df_unificado is None or df_unificado.empty or 'Linea' not in df_unificado.columns:
        return []

    if año and 'Año' in df_unificado.columns:
        df_unificado = df_unificado[df_unificado['Año'] == año]

    lineas = []
    for linea in df_unificado['Linea'].unique():
        df_linea = df_unificado[df_unificado['Linea'] == linea]

        cumplimiento = df_linea['Cumplimiento'].mean() if 'Cumplimiento' in df_linea.columns else 0
        indicadores = df_linea['Indicador'].nunique() if 'Indicador' in df_linea.columns else len(df_linea)

        lineas.append({
            'linea': linea,
            'cumplimiento': cumplimiento if pd.notna(cumplimiento) else 0,
            'indicadores': indicadores
        })

    return sorted(lineas, key=lambda x: x['cumplimiento'], reverse=True)


# Importar pandas para uso en funciones
import pandas as pd
