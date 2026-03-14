"""
Repositorio centralizado de prompts del PDI.
Separar los prompts del código de orquestación facilita ajustarlos
sin tocar la lógica de negocio.
"""

from __future__ import annotations


def prompt_analisis_general(
    metricas: dict,
    lineas_texto: str,
) -> str:
    return f"""Eres un analista estratégico del Politécnico Grancolombiano. \
Analiza los siguientes datos del Plan Estratégico Institucional (PDI) 2021-2025:

**Métricas Generales (Año {metricas.get('año_actual', 2025)}):**
- Cumplimiento promedio general: {metricas.get('cumplimiento_promedio', 0):.1f}%
- Total de indicadores activos: {metricas.get('total_indicadores', 0)}
- Indicadores cumplidos (>=100%): {metricas.get('indicadores_cumplidos', 0)}
- Indicadores en progreso (80-99%): {metricas.get('en_progreso', 0)}
- Indicadores no cumplidos (<80%): {metricas.get('no_cumplidos', 0)}

**Cumplimiento por Línea Estratégica:**
{lineas_texto}

Genera un RESUMEN EJECUTIVO de máximo 150 palabras que incluya:
1. Estado general del cumplimiento del PDI
2. Las 2 líneas estratégicas con mejor desempeño
3. Las líneas que requieren mayor atención
4. Una conclusión sobre la tendencia general

Usa un tono profesional, conciso y orientado a la acción. Escribe en español."""


def prompt_analisis_linea(
    nombre_linea: str,
    total_indicadores: int,
    cumplimiento_promedio: float,
    objetivos_texto: str,
    indicadores_section: str = "",
) -> str:
    return f"""Eres un analista estratégico del Politécnico Grancolombiano.
Analiza el desempeño REAL de la siguiente línea estratégica del PDI 2021-2025 \
usando los datos exactos proporcionados.

**Línea Estratégica: {nombre_linea}**
- Total indicadores: {total_indicadores}
- Cumplimiento promedio: {cumplimiento_promedio:.1f}%

**Objetivos:**
{objetivos_texto}{indicadores_section}

Genera un ANÁLISIS CONTEXTUAL de exactamente 4 párrafos cortos (máx 200 palabras total):

PÁRRAFO 1 — ESTADO REAL: Menciona el cumplimiento global y nombra EXPLÍCITAMENTE \
cuáles indicadores cumplieron (con su %) y cuáles no.

PÁRRAFO 2 — BRECHA (solo si hay indicadores < 100%): Calcula y menciona el gap real \
de los indicadores más críticos (diferencia entre meta y ejecución, como número \
absoluto y %).

PÁRRAFO 3 — ALERTA O DESTACADO: Si hay indicador > 120% destacar el logro con número \
exacto. Si hay indicador < 80% generar alerta con nombre y valor exacto. \
Si hay proyectos en 0% mencionarlos.

PÁRRAFO 4 — RECOMENDACIÓN ESPECÍFICA: Nombrar el indicador con mayor brecha y proponer \
una acción medible y concreta. Evitar frases genéricas.

Tono: profesional, conciso, orientado a números reales. \
Escribe en español sin asteriscos ni markdown."""


def prompt_analisis_indicador(
    nombre_indicador: str,
    linea: str,
    descripcion: str,
    historico_texto: str,
    tendencia: str,
    variacion: float,
    sentido: str,
) -> str:
    return f"""Eres un analista estratégico del Politécnico Grancolombiano. \
Analiza el siguiente indicador del PDI 2021-2025:

**Indicador:** {nombre_indicador}
**Línea Estratégica:** {linea}
**Descripción:** {descripcion or 'No disponible'}
**Sentido:** {sentido} (el indicador se considera positivo si \
{'aumenta' if sentido == 'Creciente' else 'disminuye'})

**Histórico de Desempeño:**
{historico_texto}

**Tendencia calculada:** {tendencia} \
(variación de {variacion:+.1f} puntos porcentuales desde la línea base)

Genera un ANÁLISIS de máximo 100 palabras que incluya:
1. Evaluación de la tendencia desde la línea base (2021)
2. Evolución del cumplimiento año a año
3. Identificación de brechas significativas entre meta y ejecución
4. Una recomendación específica y accionable para mejorar el indicador

Sé conciso, profesional y enfocado en la acción. Escribe en español."""
