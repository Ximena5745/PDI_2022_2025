"""
AIService: orquesta cache → proveedor IA → fallback estático.
Desacopla la lógica de generación de los views.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from ai.gemini_provider import GeminiProvider
from ai.static_provider import StaticProvider
from ai.prompts import (
    prompt_analisis_general,
    prompt_analisis_linea,
    prompt_analisis_indicador,
)
from core.config import CACHE_ANALISIS_PATH


class AIService:
    """
    Pipeline de análisis inteligente:
    1. Busca en cache JSON pre-generado
    2. Intenta con GeminiProvider (si API key disponible)
    3. Cae a StaticProvider (siempre disponible)
    """

    def __init__(self, base_path: Optional[Path] = None) -> None:
        self._base = base_path or self._detectar_raiz()
        self._gemini = GeminiProvider()
        self._static = StaticProvider()
        self._cache: dict = self._cargar_cache()

    # ------------------------------------------------------------------
    # Análisis general del PDI
    # ------------------------------------------------------------------
    def analisis_general(
        self,
        metricas: dict,
        cumplimiento_por_linea: list[dict],
    ) -> str:
        if self._gemini.is_available():
            # Texto resumido para el encabezado del prompt
            lineas_texto = "\n".join(
                f"- {i['linea']}: {i['cumplimiento']:.1f}% ({i['indicadores']} indicadores)"
                for i in cumplimiento_por_linea
            ) or "No hay datos disponibles"

            # Detalle enriquecido: agrega cumplidos y atención si están disponibles
            lineas_detalle = []
            for i in cumplimiento_por_linea:
                lineas_detalle.append({
                    "linea":        i.get("linea", ""),
                    "cumplimiento": float(i.get("cumplimiento", 0)),
                    "indicadores":  int(i.get("indicadores", 0)),
                    "cumplidos":    int(i.get("cumplidos", 0)),
                    "atencion":     int(i.get("atencion", i.get("no_cumplidos", 0))),
                })

            resultado = self._gemini.generate(
                prompt_analisis_general(metricas, lineas_texto, lineas_detalle)
            )
            if resultado:
                return resultado

        return self._static.analisis_general(metricas, cumplimiento_por_linea)

    # ------------------------------------------------------------------
    # Análisis por línea estratégica
    # ------------------------------------------------------------------
    def analisis_linea(
        self,
        nombre_linea: str,
        total_indicadores: int,
        cumplimiento_promedio: float,
        objetivos_data: list[dict],
        indicadores_data: Optional[list[dict]] = None,
    ) -> str:
        if self._gemini.is_available():
            objetivos_texto = "\n".join(
                f"- {o['objetivo']}: {o['cumplimiento']:.1f}% ({o.get('indicadores', 0)} indicadores)"
                for o in objetivos_data
            ) or "No hay datos de objetivos disponibles"

            indicadores_section = ""
            if indicadores_data:
                cumplidos   = [i for i in indicadores_data if float(i.get("cumplimiento", 0)) >= 100]
                en_prog     = [i for i in indicadores_data if 80 <= float(i.get("cumplimiento", 0)) < 100]
                en_atencion = [i for i in indicadores_data if float(i.get("cumplimiento", 0)) < 80]

                def _gap(ind) -> float:
                    """Brecha absoluta meta − ejecución (0 si no disponible)."""
                    try:
                        return float(ind.get("meta", 0) or 0) - float(ind.get("ejecucion", 0) or 0)
                    except Exception:
                        return 0.0

                def _fmt(ind, show_gap: bool = False) -> str:
                    nombre = ind.get("nombre", "Indicador")[:65]
                    cumpl  = float(ind.get("cumplimiento", 0))
                    meta   = ind.get("meta")
                    ejec   = ind.get("ejecucion")
                    partes = [f"{nombre}: {cumpl:.1f}%"]
                    if meta is not None and ejec is not None:
                        try:
                            m, e = float(meta), float(ejec)
                            partes.append(f"(Meta {m:.1f} → Ejec {e:.1f}")
                            if show_gap:
                                partes.append(f"| brecha {m - e:+.1f})")
                            else:
                                partes.append(")")
                        except Exception:
                            pass
                    return " ".join(partes)

                # Ordenar atención por mayor brecha (más críticos primero)
                en_atencion_sorted = sorted(en_atencion, key=_gap, reverse=True)

                lineas_inds = []
                if cumplidos:
                    lineas_inds += [f"CUMPLIDOS ({len(cumplidos)}):"] + \
                                   [f"  ✓ {_fmt(i)}" for i in cumplidos[:6]]
                if en_prog:
                    lineas_inds += [f"EN PROGRESO — 80 a 99% ({len(en_prog)}):"] + \
                                   [f"  ⚠ {_fmt(i, show_gap=True)}" for i in en_prog[:6]]
                if en_atencion_sorted:
                    lineas_inds += [f"REQUIEREN ATENCIÓN — <80% ({len(en_atencion_sorted)}, ordenados por brecha):"] + \
                                   [f"  ✗ {_fmt(i, show_gap=True)}" for i in en_atencion_sorted[:8]]
                indicadores_section = "\n\n**Detalle de Indicadores:**\n" + "\n".join(lineas_inds)

            resultado = self._gemini.generate(
                prompt_analisis_linea(
                    nombre_linea, total_indicadores, cumplimiento_promedio,
                    objetivos_texto, indicadores_section,
                )
            )
            if resultado:
                return resultado

        return self._static.analisis_linea(
            nombre_linea, total_indicadores, cumplimiento_promedio, objetivos_data
        )

    # ------------------------------------------------------------------
    # Análisis por indicador
    # ------------------------------------------------------------------
    def analisis_indicador(
        self,
        nombre_indicador: str,
        linea: str,
        descripcion: str,
        historico_data: list[dict],
        sentido: str = "Creciente",
    ) -> str:
        # 1. Cache pre-generado
        cached = self._cache.get(nombre_indicador, {}).get("analisis")
        if cached:
            return f"**Análisis del Indicador**\n\n{cached}"

        # 2. IA en vivo
        if self._gemini.is_available() and historico_data:
            historico_texto = "\n".join(
                f"- {h['año']}{' (Línea Base)' if h['año'] == 2021 else ''}: "
                f"Meta: {h['meta']:.2f}, Ejecución: {h['ejecucion']:.2f}, Cumplimiento: {h['cumplimiento']:.1f}%"
                for h in historico_data
            )
            if len(historico_data) >= 2:
                primer_cumpl = historico_data[0]["cumplimiento"]
                ultimo_cumpl = historico_data[-1]["cumplimiento"]
                variacion = ultimo_cumpl - primer_cumpl
                tendencia = "ascendente" if variacion > 5 else "descendente" if variacion < -5 else "estable"
            else:
                variacion, tendencia = 0.0, "no determinada"

            resultado = self._gemini.generate(
                prompt_analisis_indicador(
                    nombre_indicador, linea, descripcion,
                    historico_texto, tendencia, variacion, sentido,
                )
            )
            if resultado:
                return resultado

        # 3. Fallback estático
        return self._static.analisis_indicador(
            nombre_indicador, linea, historico_data, sentido
        )

    # ------------------------------------------------------------------
    # Internos
    # ------------------------------------------------------------------
    def _cargar_cache(self) -> dict:
        path = self._base / CACHE_ANALISIS_PATH
        if not path.exists():
            # compatibilidad con ruta legacy
            legacy = self._base / "Data" / "analisis_cache.json"
            path = legacy if legacy.exists() else path
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    @staticmethod
    def _detectar_raiz() -> Path:
        current = Path(__file__).resolve().parent
        for _ in range(5):
            if (current / "app.py").exists():
                return current
            current = current.parent
        return Path(__file__).resolve().parent.parent
