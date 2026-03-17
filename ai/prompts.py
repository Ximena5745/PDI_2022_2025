"""
Repositorio centralizado de prompts del PDI.
Separar los prompts del código de orquestación facilita ajustarlos
sin tocar la lógica de negocio.
"""

from __future__ import annotations

# Contexto institucional por línea estratégica — da al modelo el "para qué"
# de cada línea y evita análisis genéricos sin referencia real.
_CONTEXTO_LINEA: dict[str, str] = {
    "calidad": (
        "gestiona acreditaciones, renovaciones de registro calificado, resultados Saber-Pro "
        "y procesos de autoevaluación y mejora continua de programas académicos."
    ),
    "expansion": (
        "impulsa el crecimiento de matrícula, apertura de nuevos programas, presencia regional "
        "y alianzas B2B/B2G que amplían la cobertura de la institución."
    ),
    "educacion para toda la vida": (
        "promueve la formación continua, posgrados, educación corporativa y programas de "
        "actualización para egresados y comunidad, más allá del pregrado tradicional."
    ),
    "experiencia": (
        "mide la satisfacción, bienestar y experiencia integral del estudiante: NPS, "
        "retención, acompañamiento y entornos de aprendizaje."
    ),
    "transformacion organizacional": (
        "lidera la modernización interna: transformación digital, eficiencia de procesos, "
        "cultura organizacional, talento humano y proyectos tecnológicos."
    ),
    "sostenibilidad": (
        "garantiza la sostenibilidad financiera, gestión de riesgos, EBITDA institucional "
        "y equilibrio entre ingresos, costos y proyecciones a mediano plazo."
    ),
}


def _ctx_linea(nombre: str) -> str:
    """Retorna el contexto institucional de la línea (insensible a acentos)."""
    import unicodedata
    n = unicodedata.normalize("NFD", nombre.lower()).encode("ascii", "ignore").decode().strip()
    for key, ctx in _CONTEXTO_LINEA.items():
        if key in n or n in key:
            return ctx
    return "representa una dimensión estratégica del PDI 2022-2025."


def prompt_analisis_general(
    metricas: dict,
    lineas_texto: str,
    lineas_detalle: list[dict] | None = None,
) -> str:
    """
    Prompt para resumen ejecutivo global del PDI.
    lineas_detalle: lista de {linea, cumplimiento, indicadores, cumplidos, atencion}
    """
    año = metricas.get("año_actual", 2025)
    cumpl_prom = metricas.get("cumplimiento_promedio", 0)
    total = metricas.get("total_indicadores", 0)
    cumplidos = metricas.get("indicadores_cumplidos", 0)
    en_prog = metricas.get("en_progreso", 0)
    no_cumpl = metricas.get("no_cumplidos", 0)
    pct_cumpl = round(cumplidos / total * 100, 1) if total else 0

    # Construir ranking con contexto
    ranking_txt = ""
    if lineas_detalle:
        ordenadas = sorted(lineas_detalle, key=lambda x: x.get("cumplimiento", 0), reverse=True)
        mejor = ordenadas[0] if ordenadas else None
        peor  = ordenadas[-1] if len(ordenadas) > 1 else None
        ranking_txt = "\n**Ranking de líneas (mejor → peor):**\n"
        for ld in ordenadas:
            nom = ld.get("linea", "")
            p   = ld.get("cumplimiento", 0)
            ni  = ld.get("indicadores", 0)
            nc  = ld.get("cumplidos", 0)
            na  = ld.get("atencion", 0)
            gap = round(100 - p, 1) if p < 100 else 0
            ranking_txt += (
                f"  • {nom}: {p:.1f}% | {nc}/{ni} cumplidos"
                + (f" | {na} en atención" if na else "")
                + (f" | brecha {gap}pp" if gap > 0 else " | META SUPERADA")
                + "\n"
            )

    return f"""Eres analista estratégico del Politécnico Grancolombiano. \
Redacta un resumen ejecutivo del PDI {año} usando EXCLUSIVAMENTE los datos reales provistos. \
Nunca uses frases genéricas como "se evidencia un avance satisfactorio" o "se recomienda fortalecer". \
Cada oración debe citar un número o nombre concreto.

**Datos del PDI {año}:**
- Cumplimiento promedio: {cumpl_prom:.1f}%
- Total indicadores: {total} | Cumplidos (≥100%): {cumplidos} ({pct_cumpl}%) | \
En progreso (80–99%): {en_prog} | Requieren atención (<80%): {no_cumpl}
{lineas_texto}{ranking_txt}
**Instrucciones de redacción:**
Escribe exactamente 3 párrafos sin títulos, sin viñetas, sin markdown, en español:

PÁRRAFO 1 (estado global): Menciona el cumplimiento promedio, cuántos indicadores cumplieron \
y el porcentaje que representan. Cita la línea con mayor cumplimiento y su valor exacto.

PÁRRAFO 2 (brechas): Nombra explícitamente las líneas con cumplimiento menor a 90% y cuántos \
indicadores están en atención. Calcula cuántos puntos porcentuales separan la línea más baja \
de la más alta.

PÁRRAFO 3 (cierre ejecutivo): Una sola acción prioritaria para el trimestre siguiente, \
vinculada al indicador o línea con mayor brecha. Menciona el nombre exacto y el gap numérico. \
Evita frases vagas — propón qué medir o ajustar, no solo "mejorar"."""


def prompt_analisis_linea(
    nombre_linea: str,
    total_indicadores: int,
    cumplimiento_promedio: float,
    objetivos_texto: str,
    indicadores_section: str = "",
) -> str:
    ctx = _ctx_linea(nombre_linea)
    return f"""Eres analista estratégico del Politécnico Grancolombiano. \
La línea "{nombre_linea}" {ctx}

**Datos reales del corte actual:**
- Indicadores totales: {total_indicadores}
- Cumplimiento promedio de la línea: {cumplimiento_promedio:.1f}%

**Objetivos y su cumplimiento:**
{objetivos_texto}{indicadores_section}

**Reglas de redacción (incumplirlas invalida la respuesta):**
- Máximo 220 palabras en 4 párrafos sin títulos, sin asteriscos, sin markdown.
- Cada afirmación debe ir acompañada de su número exacto (%, meta, ejecución o brecha).
- Prohibido usar: "se evidencia", "se recomienda fortalecer", "es importante", \
"se debe trabajar en", "continuar con los esfuerzos". Usa verbos de acción directa.
- Escribe en español.

PÁRRAFO 1 — SITUACIÓN ACTUAL: Cumplimiento global de la línea y cuántos indicadores \
alcanzaron la meta. Cita el indicador con mayor y menor cumplimiento con sus valores exactos.

PÁRRAFO 2 — BRECHAS CRÍTICAS: Para cada indicador por debajo del 80%, indica su nombre, \
meta, ejecución y brecha absoluta (meta − ejecución). Si no hay indicadores en rojo, \
describe los que están entre 80–99% con su gap específico.

PÁRRAFO 3 — LOGROS DESTACADOS: Si algún indicador superó el 110%, menciona su nombre y \
valor. Si todos están bajo 100%, identifica el que más se acercó y cuánto le faltó.

PÁRRAFO 4 — ACCIÓN CONCRETA: Propón una única acción medible para el próximo período, \
vinculada al indicador con mayor brecha. Especifica qué métrica ajustar, en qué magnitud \
y con qué frecuencia de seguimiento."""


def prompt_analisis_indicador(
    nombre_indicador: str,
    linea: str,
    descripcion: str,
    historico_texto: str,
    tendencia: str,
    variacion: float,
    sentido: str,
) -> str:
    ctx = _ctx_linea(linea)
    return f"""Eres analista estratégico del Politécnico Grancolombiano. \
La línea "{linea}" {ctx}

**Indicador:** {nombre_indicador}
**Sentido:** {sentido} — positivo si {'aumenta' if sentido == 'Creciente' else 'disminuye'}
**Descripción:** {descripcion or 'No disponible'}

**Serie histórica (año: meta → ejecución → cumplimiento%):**
{historico_texto}

**Tendencia calculada:** {tendencia} (variación {variacion:+.1f} pp desde línea base)

Escribe un análisis de máximo 110 palabras en español, sin markdown, sin títulos. \
Prohibido usar frases genéricas. Cada oración debe citar un dato numérico concreto del \
histórico. Incluye obligatoriamente:
1. Evolución del cumplimiento citando al menos dos años con sus valores.
2. Brecha concreta del último período (meta − ejecución como número absoluto).
3. Una recomendación accionable que mencione una cifra objetivo para el próximo período."""
