"""
Helpers generales del proyecto (sin lógica de negocio ni Streamlit).
"""

from __future__ import annotations

import io
import pandas as pd

# Re-exportar normalizar_columnas desde processor para no romper imports legacy
from core.processor import normalizar_columnas  # noqa: F401


def exportar_a_excel(df: pd.DataFrame, nombre_archivo: str = "informe_poli.xlsx") -> bytes:
    """Serializa un DataFrame a bytes de Excel. Alias de ExportService.exportar_excel."""
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Datos", index=False)
    return buffer.getvalue()
