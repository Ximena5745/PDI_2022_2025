"""
ExportService: generación de Excel y PDF.
Centraliza toda la lógica de exportación.
"""

from __future__ import annotations

import io
import pandas as pd


class ExportService:

    @staticmethod
    def exportar_excel(df: pd.DataFrame, nombre_hoja: str = "Datos") -> bytes:
        """Serializa un DataFrame a bytes de Excel (.xlsx)."""
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name=nombre_hoja, index=False)
        return buffer.getvalue()

    @staticmethod
    def exportar_pdf_reportlab(
        df_base: pd.DataFrame,
        df_unificado: pd.DataFrame,
        año: int,
    ) -> bytes:
        """
        Genera el informe PDF usando el generador ReportLab existente.
        Importa el módulo bajo demanda para no cargar ReportLab si no se necesita.
        """
        from utils.pdf_generator_reportlab import exportar_informe_pdf_reportlab  # type: ignore
        return exportar_informe_pdf_reportlab(df_base, df_unificado, año)
