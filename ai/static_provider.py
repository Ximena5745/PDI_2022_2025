"""
Proveedor estático de análisis (fallback sin API).
Genera análisis basados en reglas cuando ningún proveedor de IA está disponible.
"""

from __future__ import annotations

from ai.base import AIProvider


class StaticProvider(AIProvider):
    """
    Fallback que genera textos analíticos a partir de reglas deterministas.
    No requiere conexión a internet ni credenciales.
    """

    def is_available(self) -> bool:
        return True  # Siempre disponible

    def generate(self, prompt: str, max_tokens: int = 1000) -> str:
        # El StaticProvider no interpreta el prompt;
        # la generación real la hace AIService al construir el texto estático.
        return ""

    # ------------------------------------------------------------------
    # Métodos de análisis estático (llamados directamente por AIService)
    # ------------------------------------------------------------------
    def analisis_general(
        self,
        metricas: dict,
        cumplimiento_por_linea: list[dict],
    ) -> str:
        cumplimiento = metricas.get("cumplimiento_promedio", 0)
        total = metricas.get("total_indicadores", 0)
        cumplidos = metricas.get("indicadores_cumplidos", 0)
        en_progreso = metricas.get("en_progreso", 0)
        no_cumplidos = metricas.get("no_cumplidos", 0)

        if cumplimiento >= 100:
            estado, mensaje = "EXCELENTE", f"El PDI presenta un cumplimiento sobresaliente del {cumplimiento:.1f}%."
        elif cumplimiento >= 90:
            estado, mensaje = "MUY BUENO", f"El PDI muestra un cumplimiento muy satisfactorio del {cumplimiento:.1f}%."
        elif cumplimiento >= 80:
            estado, mensaje = "BUENO", f"El PDI tiene un cumplimiento aceptable del {cumplimiento:.1f}%, aunque hay oportunidades de mejora."
        elif cumplimiento >= 70:
            estado, mensaje = "REGULAR", f"El PDI presenta un cumplimiento del {cumplimiento:.1f}% que requiere atención."
        else:
            estado, mensaje = "CRÍTICO", f"El PDI tiene un cumplimiento del {cumplimiento:.1f}% que requiere acción inmediata."

        lineas_dest = [f"{l['linea']} ({l['cumplimiento']:.1f}%)" for l in cumplimiento_por_linea if l["cumplimiento"] >= 100]
        lineas_crit = [f"{l['linea']} ({l['cumplimiento']:.1f}%)" for l in cumplimiento_por_linea if l["cumplimiento"] < 80]

        pct_cumpl = f"{(cumplidos/total*100):.1f}%" if total else "N/D"
        texto = (
            f"**RESUMEN EJECUTIVO PDI — Análisis Automático**\n\n"
            f"**Estado General:** {estado}\n\n{mensaje}\n\n"
            f"**Distribución de Indicadores:**\n"
            f"- Total evaluados: {total}\n"
            f"- Cumplidos (≥100%): {cumplidos} ({pct_cumpl} del total)\n"
            f"- En progreso (80-99%): {en_progreso}\n"
            f"- Requieren atención (<80%): {no_cumplidos}\n\n"
        )
        if lineas_dest:
            texto += f"**Líneas con mejor desempeño:** {', '.join(lineas_dest[:3])}\n\n"
        if lineas_crit:
            texto += f"**Líneas que requieren atención:** {', '.join(lineas_crit[:3])}\n\n"
        if no_cumplidos > cumplidos:
            texto += "**Recomendación:** Priorizar las líneas con menor cumplimiento y establecer planes de acción inmediatos."
        elif cumplimiento >= 100:
            texto += "**Recomendación:** Mantener las estrategias actuales y documentar las mejores prácticas."
        else:
            texto += "**Recomendación:** Revisar los indicadores en progreso para asegurar que alcancen la meta antes del cierre del período."
        return texto

    def analisis_linea(
        self,
        nombre_linea: str,
        total_indicadores: int,
        cumplimiento_promedio: float,
        objetivos_data: list[dict],
    ) -> str:
        if cumplimiento_promedio >= 100:
            estado, icono = "sobresaliente", "[OK]"
        elif cumplimiento_promedio >= 80:
            estado, icono = "satisfactorio", "[!]"
        else:
            estado, icono = "requiere atención", "[X]"

        texto = (
            f"**ANÁLISIS: {nombre_linea}**\n\n"
            f"{icono} **Estado:** La línea presenta un cumplimiento {estado} del "
            f"**{cumplimiento_promedio:.1f}%** con {total_indicadores} indicadores activos.\n\n"
        )
        if objetivos_data:
            obj_cumpl = [o for o in objetivos_data if o["cumplimiento"] >= 100]
            obj_crit = [o for o in objetivos_data if o["cumplimiento"] < 80]
            if obj_cumpl:
                texto += f"**Objetivos destacados:** {len(obj_cumpl)} de {len(objetivos_data)} objetivos han alcanzado o superado la meta.\n\n"
            if obj_crit:
                nombres = [o["objetivo"][:50] + ("..." if len(o["objetivo"]) > 50 else "") for o in obj_crit[:2]]
                texto += f"**Objetivos a mejorar:** {', '.join(nombres)}\n\n"

        if cumplimiento_promedio >= 100:
            texto += "**Recomendación:** Documentar las estrategias exitosas y compartir con otras líneas."
        elif cumplimiento_promedio >= 80:
            texto += "**Recomendación:** Intensificar esfuerzos en los indicadores cercanos a la meta para alcanzar el 100%."
        else:
            texto += "**Recomendación:** Revisar y ajustar las estrategias actuales. Considerar reasignar recursos a los objetivos críticos."
        return texto

    def analisis_indicador(
        self,
        nombre_indicador: str,
        linea: str,
        historico_data: list[dict],
        sentido: str = "Creciente",
    ) -> str:
        if not historico_data:
            return f"**{nombre_indicador}**\n\nNo hay datos históricos disponibles para analizar."

        primero = historico_data[0]
        ultimo = historico_data[-1]
        cumpl_actual = ultimo.get("cumplimiento", 0)
        variacion = cumpl_actual - primero.get("cumplimiento", 0)

        if variacion > 10:
            tendencia, icono_t = "positiva", "^"
        elif variacion < -10:
            tendencia, icono_t = "negativa", "v"
        else:
            tendencia, icono_t = "estable", "-"

        if cumpl_actual >= 100:
            estado = "[OK] Meta cumplida"
        elif cumpl_actual >= 80:
            estado = "[!] En progreso"
        else:
            estado = "[X] Requiere atención"

        texto = (
            f"**ANÁLISIS: {nombre_indicador[:60]}{'...' if len(nombre_indicador) > 60 else ''}**\n\n"
            f"**Línea Estratégica:** {linea}\n"
            f"**Sentido:** {sentido} ({'mayor es mejor' if sentido == 'Creciente' else 'menor es mejor'})\n\n"
            f"**Estado actual:** {estado} — Cumplimiento: **{cumpl_actual:.1f}%**\n\n"
            f"**Evolución ({icono_t} Tendencia {tendencia}):**\n"
            f"- Línea base ({primero.get('año', 'N/D')}): {primero.get('cumplimiento', 0):.1f}%\n"
            f"- Actual ({ultimo.get('año', 'N/D')}): {cumpl_actual:.1f}%\n"
            f"- Variación: {variacion:+.1f} pp\n\n"
        )
        if "meta" in ultimo and "ejecucion" in ultimo:
            brecha = ultimo["meta"] - ultimo["ejecucion"]
            if brecha > 0:
                texto += f"**Brecha actual:** {abs(brecha):.2f} unidades por debajo de la meta.\n\n"
            else:
                texto += f"**Desempeño:** Supera la meta en {abs(brecha):.2f} unidades.\n\n"

        if cumpl_actual >= 100:
            texto += "**Recomendación:** Mantener las acciones actuales y documentar las buenas prácticas."
        elif cumpl_actual >= 80 and variacion > 0:
            texto += "**Recomendación:** Continuar con la estrategia actual, la tendencia es favorable."
        elif variacion < 0:
            texto += "**Recomendación:** Revisar las acciones implementadas, hay una tendencia descendente que requiere corrección."
        else:
            texto += "**Recomendación:** Intensificar las acciones y revisar los recursos asignados al indicador."
        return texto
