"""
Procesamiento y normalización de datos crudos del PDI.
Sin dependencias de Streamlit — operable en cualquier contexto Python.
"""

from __future__ import annotations

import unicodedata
import pandas as pd

from core.calculations import calcular_cumplimiento


# ---------------------------------------------------------------------------
# Normalización de nombres de columnas (maneja tildes y variantes)
# ---------------------------------------------------------------------------
_COLUMN_MAP: dict[str, str] = {
    "ano":           "Año",
    "ejecucion":     "Ejecución",
    "clasificacion": "Clasificación",
    "proyeccion":    "Proyección",
    "caracteristica": "CARACTERÍSTICA",
    "ejecucion s":   "Ejecución s",
}


def _ascii(text: str) -> str:
    return (
        unicodedata.normalize("NFKD", text)
        .encode("ASCII", "ignore")
        .decode("ASCII")
        .strip()
        .lower()
    )


def normalizar_columnas(df: pd.DataFrame) -> pd.DataFrame:
    """
    Renombra columnas del DataFrame para unificar variantes con/sin tilde.
    Preserva columnas que ya tienen el nombre canónico.
    """
    mapeo: dict[str, str] = {}
    for col in df.columns:
        col_ascii = _ascii(str(col))
        canonical = _COLUMN_MAP.get(col_ascii)
        if canonical and col != canonical:
            mapeo[col] = canonical
    return df.rename(columns=mapeo) if mapeo else df


# ---------------------------------------------------------------------------
# Procesamiento del DataFrame Unificado
# ---------------------------------------------------------------------------
def procesar_datos_unificado(df: pd.DataFrame) -> pd.DataFrame:
    """
    Limpia tipos y calcula la columna Cumplimiento si no existe.
    Recibe el DataFrame crudo de la hoja 'Unificado'.
    """
    df = df.copy()

    # Convertir columnas numéricas
    for col in ("Año", "Meta", "Ejecución", "Cumplimiento"):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Normalizar Cumplimiento de decimal a porcentaje
    if "Cumplimiento" in df.columns:
        max_val = df["Cumplimiento"].max()
        if pd.notna(max_val) and max_val <= 2:
            df["Cumplimiento"] = df["Cumplimiento"] * 100

    # Calcular Cumplimiento si no existe
    if "Cumplimiento" not in df.columns and "Meta" in df.columns and "Ejecución" in df.columns:
        sentido_col = "Sentido" if "Sentido" in df.columns else None
        df["Cumplimiento"] = df.apply(
            lambda row: calcular_cumplimiento(
                row["Meta"],
                row["Ejecución"],
                str(row[sentido_col]) if sentido_col else "Creciente",
            ),
            axis=1,
        )

    return df


# ---------------------------------------------------------------------------
# Limpieza post-carga (nombres de columnas + tipos)
# ---------------------------------------------------------------------------
def limpiar_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aplica strip a encabezados y normaliza columnas con tilde.
    Paso inicial antes de cualquier procesamiento de negocio.
    """
    df = df.copy()
    df.columns = df.columns.str.strip()
    df = normalizar_columnas(df)
    return df
