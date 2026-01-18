"""
Módulo de análisis con IA (Anthropic Claude) para el Dashboard Estratégico POLI.
"""

import os
import streamlit as st
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()


def get_anthropic_client():
    """
    Obtiene el cliente de Anthropic si está disponible.
    """
    try:
        import anthropic
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if api_key:
            return anthropic.Anthropic(api_key=api_key)
        return None
    except ImportError:
        return None


def generar_analisis_con_ia(prompt, max_tokens=1000):
    """
    Genera análisis usando la API de Anthropic.

    Args:
        prompt: El prompt a enviar a Claude
        max_tokens: Máximo de tokens en la respuesta

    Returns:
        str: Texto del análisis o mensaje de error
    """
    client = get_anthropic_client()

    if client is None:
        return generar_analisis_fallback(prompt)

    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=max_tokens,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        return message.content[0].text
    except Exception as e:
        return f"⚠️ No se pudo generar el análisis con IA: {str(e)}\n\nPor favor configure ANTHROPIC_API_KEY en las variables de entorno."


def generar_analisis_fallback(prompt):
    """
    Genera un análisis básico sin IA cuando la API no está disponible.
    """
    return """📊 **Análisis automático no disponible**

Para habilitar el análisis inteligente con IA:

1. Obtenga una API Key de Anthropic en [console.anthropic.com](https://console.anthropic.com)
2. Cree un archivo `.env` en el directorio del proyecto
3. Agregue: `ANTHROPIC_API_KEY=su_api_key_aqui`
4. Reinicie la aplicación

El análisis con IA proporciona insights personalizados sobre tendencias, brechas y recomendaciones estratégicas."""


@st.cache_data(ttl=3600, show_spinner=False)
def generar_analisis_general(metricas_dict, cumplimiento_por_linea):
    """
    Genera el análisis general del dashboard.

    Args:
        metricas_dict: Diccionario con métricas generales
        cumplimiento_por_linea: Lista de diccionarios con cumplimiento por línea

    Returns:
        str: Texto del análisis
    """
    # Construir resumen de líneas estratégicas
    lineas_texto = "\n".join([
        f"- {item['linea']}: {item['cumplimiento']:.1f}% ({item['indicadores']} indicadores)"
        for item in cumplimiento_por_linea
    ]) if cumplimiento_por_linea else "No hay datos disponibles"

    prompt = f"""Eres un analista estratégico del Politécnico Grancolombiano. Analiza los siguientes datos del Plan Estratégico Institucional (PDI) 2021-2025:

**Métricas Generales (Año {metricas_dict.get('año_actual', 2025)}):**
- Cumplimiento promedio general: {metricas_dict.get('cumplimiento_promedio', 0):.1f}%
- Total de indicadores activos: {metricas_dict.get('total_indicadores', 0)}
- Indicadores con meta cumplida (≥90%): {metricas_dict.get('metas_cumplidas', 0)}
- Indicadores en progreso (70-89%): {metricas_dict.get('en_progreso', 0)}
- Indicadores que requieren atención (<70%): {metricas_dict.get('requieren_atencion', 0)}

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

    Args:
        nombre_linea: Nombre de la línea estratégica
        total_indicadores: Total de indicadores en la línea
        cumplimiento_promedio: Cumplimiento promedio de la línea
        objetivos_data: Lista de diccionarios con datos de objetivos

    Returns:
        str: Texto del análisis
    """
    # Construir resumen de objetivos
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

    Args:
        nombre_indicador: Nombre del indicador
        linea: Línea estratégica a la que pertenece
        descripcion: Descripción del indicador
        historico_data: Lista de diccionarios con datos históricos por año
        sentido: Sentido del indicador (Creciente/Decreciente)

    Returns:
        str: Texto del análisis
    """
    # Construir histórico
    historico_texto = "\n".join([
        f"- {item['año']}{' (Línea Base)' if item['año'] == 2021 else ''}: Meta: {item['meta']:.2f}, Ejecución: {item['ejecucion']:.2f}, Cumplimiento: {item['cumplimiento']:.1f}%"
        for item in historico_data
    ]) if historico_data else "No hay datos históricos disponibles"

    # Calcular tendencia
    if historico_data and len(historico_data) >= 2:
        primer_cumpl = historico_data[0]['cumplimiento']
        ultimo_cumpl = historico_data[-1]['cumplimiento']
        variacion = ultimo_cumpl - primer_cumpl
        tendencia = "ascendente" if variacion > 5 else "descendente" if variacion < -5 else "estable"
    else:
        tendencia = "no determinada"
        variacion = 0

    prompt = f"""Eres un analista estratégico del Politécnico Grancolombiano. Analiza el siguiente indicador del PDI 2021-2025:

**Indicador:** {nombre_indicador}
**Línea Estratégica:** {linea}
**Descripción:** {descripcion if descripcion else 'No disponible'}
**Sentido:** {sentido} (el indicador se considera positivo si {'aumenta' if sentido == 'Creciente' else 'disminuye'})

**Histórico de Desempeño:**
{historico_texto}

**Tendencia calculada:** {tendencia} (variación de {variacion:+.1f} puntos porcentuales desde la línea base)

Genera un ANÁLISIS de máximo 100 palabras que incluya:
1. Evaluación de la tendencia desde la línea base (2021)
2. Evolución del cumplimiento año a año
3. Identificación de brechas significativas entre meta y ejecución
4. Una recomendación específica y accionable para mejorar el indicador

Sé conciso, profesional y enfocado en la acción. Escribe en español."""

    return generar_analisis_con_ia(prompt)


def preparar_historico_para_analisis(df_indicador):
    """
    Prepara los datos históricos de un indicador para el análisis con IA.

    Args:
        df_indicador: DataFrame con datos del indicador

    Returns:
        list: Lista de diccionarios con datos por año
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

    Args:
        df_linea: DataFrame filtrado por línea
        año: Año a considerar

    Returns:
        list: Lista de diccionarios con datos por objetivo
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

    Args:
        df_unificado: DataFrame con todos los datos
        año: Año a considerar

    Returns:
        list: Lista de diccionarios con datos por línea
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
