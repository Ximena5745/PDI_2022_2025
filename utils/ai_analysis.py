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
    return """**Analisis automatico no disponible**

Para habilitar el analisis inteligente con IA (GRATUITO):

1. Ve a aistudio.google.com/app/apikey
2. Crea una API Key gratuita
3. En Streamlit Cloud: Settings > Secrets, agrega GOOGLE_API_KEY
4. O localmente, crea un archivo .env con GOOGLE_API_KEY=tu_api_key

**Google Gemini es GRATUITO** (60 consultas por minuto)."""


def generar_analisis_estatico_general(metricas_dict, cumplimiento_por_linea):
    """
    Genera un analisis estatico basado en reglas cuando la API de IA no esta disponible.
    No requiere conexion a internet.

    Args:
        metricas_dict: Diccionario con metricas generales
        cumplimiento_por_linea: Lista de diccionarios con cumplimiento por linea

    Returns:
        str: Texto del analisis generado
    """
    cumplimiento = metricas_dict.get('cumplimiento_promedio', 0)
    total = metricas_dict.get('total_indicadores', 0)
    cumplidos = metricas_dict.get('indicadores_cumplidos', 0)
    en_progreso = metricas_dict.get('en_progreso', 0)
    no_cumplidos = metricas_dict.get('no_cumplidos', 0)

    # Determinar estado general
    if cumplimiento >= 100:
        estado = "EXCELENTE"
        mensaje_estado = f"El PDI presenta un cumplimiento sobresaliente del {cumplimiento:.1f}%."
    elif cumplimiento >= 90:
        estado = "MUY BUENO"
        mensaje_estado = f"El PDI muestra un cumplimiento muy satisfactorio del {cumplimiento:.1f}%."
    elif cumplimiento >= 80:
        estado = "BUENO"
        mensaje_estado = f"El PDI tiene un cumplimiento aceptable del {cumplimiento:.1f}%, aunque hay oportunidades de mejora."
    elif cumplimiento >= 70:
        estado = "REGULAR"
        mensaje_estado = f"El PDI presenta un cumplimiento del {cumplimiento:.1f}% que requiere atencion."
    else:
        estado = "CRITICO"
        mensaje_estado = f"El PDI tiene un cumplimiento del {cumplimiento:.1f}% que requiere accion inmediata."

    # Analizar lineas
    lineas_destacadas = []
    lineas_criticas = []

    if cumplimiento_por_linea:
        for linea in cumplimiento_por_linea:
            if linea['cumplimiento'] >= 100:
                lineas_destacadas.append(f"{linea['linea']} ({linea['cumplimiento']:.1f}%)")
            elif linea['cumplimiento'] < 80:
                lineas_criticas.append(f"{linea['linea']} ({linea['cumplimiento']:.1f}%)")

    # Construir analisis
    analisis = f"""**RESUMEN EJECUTIVO PDI - Analisis Automatico**

**Estado General:** {estado}

{mensaje_estado}

**Distribucion de Indicadores:**
- Total evaluados: {total}
- Cumplidos (>=100%): {cumplidos} ({(cumplidos/total*100):.1f}% del total)
- En progreso (80-99%): {en_progreso}
- Requieren atencion (<80%): {no_cumplidos}

"""

    if lineas_destacadas:
        analisis += f"**Lineas con mejor desempeno:** {', '.join(lineas_destacadas[:3])}\n\n"

    if lineas_criticas:
        analisis += f"**Lineas que requieren atencion:** {', '.join(lineas_criticas[:3])}\n\n"

    # Recomendaciones basadas en el estado
    if no_cumplidos > cumplidos:
        analisis += "**Recomendacion:** Se sugiere priorizar las lineas con menor cumplimiento y establecer planes de accion inmediatos."
    elif cumplimiento >= 100:
        analisis += "**Recomendacion:** Mantener las estrategias actuales y documentar las mejores practicas para replicar en otras areas."
    else:
        analisis += "**Recomendacion:** Revisar los indicadores en progreso para asegurar que alcancen la meta antes del cierre del periodo."

    return analisis


def generar_analisis_estatico_linea(nombre_linea, total_indicadores, cumplimiento_promedio, objetivos_data):
    """
    Genera un analisis estatico para una linea estrategica especifica.

    Args:
        nombre_linea: Nombre de la linea estrategica
        total_indicadores: Total de indicadores
        cumplimiento_promedio: Cumplimiento promedio de la linea
        objetivos_data: Lista de diccionarios con datos de objetivos

    Returns:
        str: Texto del analisis generado
    """
    # Determinar estado
    if cumplimiento_promedio >= 100:
        estado = "sobresaliente"
        icono = "[OK]"
    elif cumplimiento_promedio >= 80:
        estado = "satisfactorio"
        icono = "[!]"
    else:
        estado = "requiere atencion"
        icono = "[X]"

    analisis = f"""**ANALISIS: {nombre_linea}**

{icono} **Estado:** La linea presenta un cumplimiento {estado} del **{cumplimiento_promedio:.1f}%** con {total_indicadores} indicadores activos.

"""

    # Analizar objetivos
    if objetivos_data:
        objetivos_cumplidos = [o for o in objetivos_data if o['cumplimiento'] >= 100]
        objetivos_criticos = [o for o in objetivos_data if o['cumplimiento'] < 80]

        if objetivos_cumplidos:
            analisis += f"**Objetivos destacados:** {len(objetivos_cumplidos)} de {len(objetivos_data)} objetivos han alcanzado o superado la meta.\n\n"

        if objetivos_criticos:
            nombres_criticos = [o['objetivo'][:50] + '...' if len(o['objetivo']) > 50 else o['objetivo'] for o in objetivos_criticos[:2]]
            analisis += f"**Objetivos a mejorar:** {', '.join(nombres_criticos)}\n\n"

    # Recomendacion
    if cumplimiento_promedio >= 100:
        analisis += "**Recomendacion:** Documentar las estrategias exitosas y compartir con otras lineas."
    elif cumplimiento_promedio >= 80:
        analisis += "**Recomendacion:** Intensificar esfuerzos en los indicadores cercanos a la meta para alcanzar el 100%."
    else:
        analisis += "**Recomendacion:** Revisar y ajustar las estrategias actuales. Considerar reasignar recursos a los objetivos criticos."

    return analisis


def generar_analisis_estatico_indicador(nombre_indicador, linea, historico_data, sentido="Creciente"):
    """
    Genera un analisis estatico para un indicador especifico.

    Args:
        nombre_indicador: Nombre del indicador
        linea: Linea estrategica
        historico_data: Lista de diccionarios con datos historicos
        sentido: Sentido del indicador (Creciente o Decreciente)

    Returns:
        str: Texto del analisis generado
    """
    if not historico_data:
        return f"**{nombre_indicador}**\n\nNo hay datos historicos disponibles para analizar."

    # Obtener ultimo y primer valor
    ultimo = historico_data[-1] if historico_data else None
    primero = historico_data[0] if historico_data else None

    if not ultimo or not primero:
        return f"**{nombre_indicador}**\n\nDatos insuficientes para el analisis."

    cumpl_actual = ultimo.get('cumplimiento', 0)
    cumpl_inicial = primero.get('cumplimiento', 0)
    variacion = cumpl_actual - cumpl_inicial

    # Determinar tendencia
    if variacion > 10:
        tendencia = "positiva"
        icono_tendencia = "^"
    elif variacion < -10:
        tendencia = "negativa"
        icono_tendencia = "v"
    else:
        tendencia = "estable"
        icono_tendencia = "-"

    # Determinar estado
    if cumpl_actual >= 100:
        estado = "[OK] Meta cumplida"
    elif cumpl_actual >= 80:
        estado = "[!] En progreso"
    else:
        estado = "[X] Requiere atencion"

    analisis = f"""**ANALISIS: {nombre_indicador[:60]}{'...' if len(nombre_indicador) > 60 else ''}**

**Linea Estrategica:** {linea}
**Sentido:** {sentido} ({'mayor es mejor' if sentido == 'Creciente' else 'menor es mejor'})

**Estado actual:** {estado} - Cumplimiento: **{cumpl_actual:.1f}%**

**Evolucion ({icono_tendencia} Tendencia {tendencia}):**
- Linea base ({primero.get('año', 'N/D')}): {cumpl_inicial:.1f}%
- Actual ({ultimo.get('año', 'N/D')}): {cumpl_actual:.1f}%
- Variacion: {variacion:+.1f} puntos porcentuales

"""

    # Analisis de brechas
    if 'meta' in ultimo and 'ejecucion' in ultimo:
        brecha = ultimo['meta'] - ultimo['ejecucion']
        if brecha > 0:
            analisis += f"**Brecha actual:** {abs(brecha):.2f} unidades por debajo de la meta.\n\n"
        else:
            analisis += f"**Desempeno:** Supera la meta en {abs(brecha):.2f} unidades.\n\n"

    # Recomendacion
    if cumpl_actual >= 100:
        analisis += "**Recomendacion:** Mantener las acciones actuales y documentar las buenas practicas."
    elif cumpl_actual >= 80 and variacion > 0:
        analisis += "**Recomendacion:** Continuar con la estrategia actual, la tendencia es favorable."
    elif variacion < 0:
        analisis += "**Recomendacion:** Revisar las acciones implementadas, hay una tendencia descendente que requiere correccion."
    else:
        analisis += "**Recomendacion:** Intensificar las acciones y revisar los recursos asignados al indicador."

    return analisis


@st.cache_data(ttl=3600, show_spinner=False)
def generar_analisis_general(metricas_dict, cumplimiento_por_linea):
    """
    Genera el analisis general del dashboard.
    Usa IA si esta disponible, sino genera analisis estatico.
    """
    # Primero intentar con IA
    client = get_gemini_client()

    if client is None:
        # Usar analisis estatico si no hay API
        return generar_analisis_estatico_general(metricas_dict, cumplimiento_por_linea)

    lineas_texto = "\n".join([
        f"- {item['linea']}: {item['cumplimiento']:.1f}% ({item['indicadores']} indicadores)"
        for item in cumplimiento_por_linea
    ]) if cumplimiento_por_linea else "No hay datos disponibles"

    prompt = f"""Eres un analista estrategico del Politecnico Grancolombiano. Analiza los siguientes datos del Plan Estrategico Institucional (PDI) 2021-2025:

**Metricas Generales (Ano {metricas_dict.get('año_actual', 2025)}):**
- Cumplimiento promedio general: {metricas_dict.get('cumplimiento_promedio', 0):.1f}%
- Total de indicadores activos: {metricas_dict.get('total_indicadores', 0)}
- Indicadores cumplidos (>=100%): {metricas_dict.get('indicadores_cumplidos', 0)}
- Indicadores en progreso (80-99%): {metricas_dict.get('en_progreso', 0)}
- Indicadores no cumplidos (<80%): {metricas_dict.get('no_cumplidos', 0)}

**Cumplimiento por Linea Estrategica:**
{lineas_texto}

Genera un RESUMEN EJECUTIVO de maximo 150 palabras que incluya:
1. Estado general del cumplimiento del PDI
2. Las 2 lineas estrategicas con mejor desempeno
3. Las lineas que requieren mayor atencion
4. Una conclusion sobre la tendencia general

Usa un tono profesional, conciso y orientado a la accion. Escribe en espanol."""

    resultado = generar_analisis_con_ia(prompt)

    # Si la API falla, usar analisis estatico
    if "No se pudo generar" in resultado or "RESOURCE_EXHAUSTED" in resultado:
        return generar_analisis_estatico_general(metricas_dict, cumplimiento_por_linea)

    return resultado


@st.cache_data(ttl=3600, show_spinner=False)
def generar_analisis_linea(nombre_linea, total_indicadores, cumplimiento_promedio,
                           objetivos_data, indicadores_data=None):
    """
    Genera analisis contextual (4 parrafos) para una linea estrategica.
    Usa IA si esta disponible, sino genera analisis estatico.

    indicadores_data: lista de dicts {nombre, meta, ejecucion, cumplimiento}
                      con datos reales de cada indicador de la linea.
    """
    client = get_gemini_client()

    if client is None:
        return generar_analisis_estatico_linea(
            nombre_linea, total_indicadores, cumplimiento_promedio, objetivos_data)

    # Construir texto de objetivos
    objetivos_texto = "\n".join([
        f"- {obj['objetivo']}: {obj['cumplimiento']:.1f}% ({obj.get('indicadores', 0)} indicadores)"
        for obj in objetivos_data
    ]) if objetivos_data else "No hay datos de objetivos disponibles"

    # Construir texto de indicadores individuales (si disponibles)
    inds_texto = ""
    if indicadores_data:
        cumplidos    = [i for i in indicadores_data if float(i.get('cumplimiento', 0)) >= 100]
        en_progreso  = [i for i in indicadores_data if 80 <= float(i.get('cumplimiento', 0)) < 100]
        en_atencion  = [i for i in indicadores_data if float(i.get('cumplimiento', 0)) < 80]

        def _fmt_ind(ind):
            nombre = ind.get('nombre', 'Indicador')[:60]
            meta   = ind.get('meta')
            ejec   = ind.get('ejecucion')
            cumpl  = float(ind.get('cumplimiento', 0))
            partes = [f"{nombre}: {cumpl:.1f}%"]
            if meta is not None and ejec is not None:
                try:
                    partes.append(f"(Meta: {float(meta):.1f}, Ejec: {float(ejec):.1f})")
                except Exception:
                    pass
            return " ".join(partes)

        lineas_inds = []
        if cumplidos:
            lineas_inds.append(f"CUMPLIDOS ({len(cumplidos)}):")
            lineas_inds += [f"  ✓ {_fmt_ind(i)}" for i in cumplidos[:5]]
        if en_progreso:
            lineas_inds.append(f"EN PROGRESO ({len(en_progreso)}):")
            lineas_inds += [f"  ⚠ {_fmt_ind(i)}" for i in en_progreso[:5]]
        if en_atencion:
            lineas_inds.append(f"REQUIEREN ATENCIÓN ({len(en_atencion)}):")
            lineas_inds += [f"  ✗ {_fmt_ind(i)}" for i in en_atencion[:5]]
        inds_texto = "\n".join(lineas_inds)

    indicadores_section = f"\n\n**Detalle de Indicadores:**\n{inds_texto}" if inds_texto else ""

    prompt = f"""Eres un analista estrategico del Politecnico Grancolombiano.
Analiza el desempeno REAL de la siguiente linea estrategica del PDI 2021-2025 usando los datos exactos proporcionados.

**Linea Estrategica: {nombre_linea}**
- Total indicadores: {total_indicadores}
- Cumplimiento promedio: {cumplimiento_promedio:.1f}%

**Objetivos:**
{objetivos_texto}{indicadores_section}

Genera un ANALISIS CONTEXTUAL de exactamente 4 parrafos cortos (max 200 palabras total):

PARRAFO 1 — ESTADO REAL: Menciona el cumplimiento global y nombra EXPLICITAMENTE cuales indicadores cumplieron (con su %) y cuales no.

PARRAFO 2 — BRECHA (solo si hay indicadores < 100%): Calcula y menciona el gap real de los indicadores mas criticos (diferencia entre meta y ejecucion, como numero absoluto y %).

PARRAFO 3 — ALERTA O DESTACADO: Si hay indicador > 120% destacar el logro con numero exacto. Si hay indicador < 80% generar alerta con nombre y valor exacto. Si hay proyectos en 0% mencionarlos.

PARRAFO 4 — RECOMENDACION ESPECIFICA: Nombrar el indicador con mayor brecha y proponer una accion medible y concreta. Evitar frases genericas.

Tono: profesional, conciso, orientado a numeros reales. Escribe en espanol sin asteriscos ni markdown."""

    resultado = generar_analisis_con_ia(prompt)

    if "No se pudo generar" in resultado or "RESOURCE_EXHAUSTED" in resultado:
        return generar_analisis_estatico_linea(
            nombre_linea, total_indicadores, cumplimiento_promedio, objetivos_data)

    return resultado


@st.cache_data(ttl=3600, show_spinner=False)
def generar_analisis_indicador(nombre_indicador, linea, descripcion, historico_data, sentido="Creciente"):
    """
    Genera analisis detallado para un indicador especifico.
    Primero busca en cache, luego intenta IA, finalmente usa analisis estatico.
    """
    # Primero intentar obtener del cache pre-generado
    analisis_cache = obtener_analisis_cache(nombre_indicador)
    if analisis_cache:
        return f"**Analisis del Indicador**\n\n{analisis_cache}"

    # Intentar con IA
    client = get_gemini_client()

    if client is None:
        return generar_analisis_estatico_indicador(nombre_indicador, linea, historico_data, sentido)

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

    resultado = generar_analisis_con_ia(prompt)

    # Si la API falla, usar analisis estatico
    if "No se pudo generar" in resultado or "RESOURCE_EXHAUSTED" in resultado:
        return generar_analisis_estatico_indicador(nombre_indicador, linea, historico_data, sentido)

    return resultado


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
