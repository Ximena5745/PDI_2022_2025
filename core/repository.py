"""
DataRepository: acceso al Dataset_Unificado.xlsx.
Sin dependencias de Streamlit — el caché (@st.cache_data) se aplica
en la capa de servicios o en app.py, no aquí.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional, Tuple
import pandas as pd

from core.config import (
    DATA_DIR,
    DATASET_FILENAME,
    SHEET_BASE,
    SHEET_UNIFICADO,
)
from core.processor import limpiar_dataframe, procesar_datos_unificado


class DataLoadError(Exception):
    """Error al cargar el dataset del PDI."""


class DataRepository:
    """
    Responsabilidad única: localizar y cargar el archivo Excel del PDI.
    Retorna DataFrames limpios y procesados, listos para la capa de servicios.
    """

    def __init__(self, base_path: Optional[Path] = None) -> None:
        self._base_path = base_path or self._detectar_raiz()

    # ------------------------------------------------------------------
    # Carga principal
    # ------------------------------------------------------------------
    def cargar(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Carga y procesa ambas hojas del Excel.

        Returns:
            (df_base, df_unificado)

        Raises:
            DataLoadError: si el archivo no existe o está bloqueado.
        """
        path = self._resolver_ruta()

        try:
            df_base = pd.read_excel(path, sheet_name=SHEET_BASE, engine="openpyxl")
            df_unificado = pd.read_excel(path, sheet_name=SHEET_UNIFICADO, engine="openpyxl")
        except PermissionError:
            raise DataLoadError(
                "El archivo Excel está abierto en otro programa. "
                "Por favor ciérrelo e intente de nuevo."
            )
        except Exception as exc:
            raise DataLoadError(f"Error al leer el archivo: {exc}") from exc

        df_base = limpiar_dataframe(df_base)
        df_unificado = limpiar_dataframe(df_unificado)
        df_unificado = procesar_datos_unificado(df_unificado)

        return df_base, df_unificado

    # ------------------------------------------------------------------
    # Internos
    # ------------------------------------------------------------------
    def _resolver_ruta(self) -> Path:
        candidatos = [
            self._base_path / DATA_DIR / DATASET_FILENAME,
            self._base_path / "Data" / DATASET_FILENAME,   # compatibilidad legacy
            Path(DATA_DIR) / DATASET_FILENAME,
            Path("Data") / DATASET_FILENAME,
        ]
        for p in candidatos:
            if p.exists():
                return p
        raise DataLoadError(
            f"No se encontró '{DATASET_FILENAME}' en ninguna de estas rutas: "
            + ", ".join(str(c) for c in candidatos)
        )

    @staticmethod
    def _detectar_raiz() -> Path:
        """Sube desde este archivo hasta encontrar app.py (raíz del proyecto)."""
        current = Path(__file__).resolve().parent
        for _ in range(5):
            if (current / "app.py").exists():
                return current
            current = current.parent
        return Path(__file__).resolve().parent.parent

    # ------------------------------------------------------------------
    # Utilidades de consulta
    # ------------------------------------------------------------------
    def dataset_path(self) -> Path:
        """Retorna la ruta resuelta del dataset (útil para logging)."""
        return self._resolver_ruta()
