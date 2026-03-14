"""
Modelos de dominio del Dashboard Estratégico POLI.
Dataclasses tipados que reemplazan los dicts volantes en todo el proyecto.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


# ---------------------------------------------------------------------------
# Métricas generales del PDI
# ---------------------------------------------------------------------------
@dataclass
class MetricasGenerales:
    cumplimiento_promedio: float
    total_indicadores: int
    indicadores_cumplidos: int
    en_progreso: int
    no_cumplidos: int
    stand_by: int
    total_lineas: int
    año_actual: int

    @classmethod
    def vacio(cls, año: int = 2025) -> "MetricasGenerales":
        return cls(
            cumplimiento_promedio=0.0,
            total_indicadores=0,
            indicadores_cumplidos=0,
            en_progreso=0,
            no_cumplidos=0,
            stand_by=0,
            total_lineas=0,
            año_actual=año,
        )

    def as_dict(self) -> dict:
        return {
            "cumplimiento_promedio": self.cumplimiento_promedio,
            "total_indicadores": self.total_indicadores,
            "indicadores_cumplidos": self.indicadores_cumplidos,
            "en_progreso": self.en_progreso,
            "no_cumplidos": self.no_cumplidos,
            "stand_by": self.stand_by,
            "total_lineas": self.total_lineas,
            "año_actual": self.año_actual,
        }


# ---------------------------------------------------------------------------
# Cumplimiento por línea estratégica
# ---------------------------------------------------------------------------
@dataclass
class CumplimientoLinea:
    linea: str
    cumplimiento: float
    total_indicadores: int
    color: str = ""

    def as_dict(self) -> dict:
        return {
            "linea": self.linea,
            "cumplimiento": self.cumplimiento,
            "indicadores": self.total_indicadores,
        }


# ---------------------------------------------------------------------------
# Cumplimiento por objetivo
# ---------------------------------------------------------------------------
@dataclass
class CumplimientoObjetivo:
    objetivo: str
    linea: str
    cumplimiento: float
    total_indicadores: int

    def as_dict(self) -> dict:
        return {
            "objetivo": self.objetivo,
            "cumplimiento": self.cumplimiento,
            "indicadores": self.total_indicadores,
        }


# ---------------------------------------------------------------------------
# Estado de proyectos institucionales
# ---------------------------------------------------------------------------
@dataclass
class EstadoProyectos:
    finalizados: int
    en_ejecucion: int
    stand_by: int
    sin_clasificar: int
    total_proyectos: int

    @classmethod
    def vacio(cls) -> "EstadoProyectos":
        return cls(
            finalizados=0,
            en_ejecucion=0,
            stand_by=0,
            sin_clasificar=0,
            total_proyectos=0,
        )

    def as_dict(self) -> dict:
        return {
            "finalizados": self.finalizados,
            "en_ejecucion": self.en_ejecucion,
            "stand_by": self.stand_by,
            "sin_clasificar": self.sin_clasificar,
            "total_proyectos": self.total_proyectos,
        }


# ---------------------------------------------------------------------------
# Punto histórico de un indicador (un período)
# ---------------------------------------------------------------------------
@dataclass
class PuntoHistorico:
    año: int
    meta: float
    ejecucion: float
    cumplimiento: float
    periodo: str = ""
    semestre: Optional[int] = None

    def as_dict(self) -> dict:
        return {
            "año": self.año,
            "meta": self.meta,
            "ejecucion": self.ejecucion,
            "cumplimiento": self.cumplimiento,
            "periodo": self.periodo,
        }


# ---------------------------------------------------------------------------
# Metadatos de un indicador (desde Base_Indicadores)
# ---------------------------------------------------------------------------
@dataclass
class MetadatosIndicador:
    nombre: str
    linea: str
    objetivo: str
    periodicidad: str = "Anual"
    sentido: str = "Creciente"
    unidad_meta: str = ""
    unidad_ejecucion: str = ""
    meta_pdi: str = ""
    descripcion: str = ""


# ---------------------------------------------------------------------------
# Fila de la estructura cascada
# ---------------------------------------------------------------------------
@dataclass
class FilaCascada:
    nivel: int
    linea: str
    objetivo: str
    meta_pdi: str
    indicador: str
    cumplimiento: float
    total_indicadores: int

    def as_dict(self) -> dict:
        return {
            "Nivel": self.nivel,
            "Linea": self.linea,
            "Objetivo": self.objetivo,
            "Meta_PDI": self.meta_pdi,
            "Indicador": self.indicador,
            "Cumplimiento": self.cumplimiento,
            "Total_Indicadores": self.total_indicadores,
        }
