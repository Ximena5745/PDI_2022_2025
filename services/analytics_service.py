"""
AnalyticsService: orquesta core/ para producir métricas, cascadas e históricos.
Esta capa NO importa Streamlit; el @st.cache_data va en los views.
"""

from __future__ import annotations

import pandas as pd
from typing import Optional

from core.config import AÑOS_PDI, FUENTE_AVANCE, FUENTE_CIERRE
from core.models import (
    MetricasGenerales,
    CumplimientoLinea,
    EstadoProyectos,
    PuntoHistorico,
    MetadatosIndicador,
    FilaCascada,
)
from core.calculations import (
    obtener_color_semaforo,
    cumplimiento_jerarquico,
)
from core.filters import (
    filtrar_por_año,
    filtrar_años_validos,
    filtrar_por_fuente,
    filtrar_indicadores,
    filtrar_proyectos,
    excluir_standby,
    contar_standby,
    obtener_año_mas_reciente,
)


class AnalyticsService:
    """
    Capa de orquestación para todos los cálculos analíticos del PDI.
    Recibe DataFrames limpios (salida de DataRepository) y retorna modelos tipados.
    """

    # ------------------------------------------------------------------
    # Métricas generales
    # ------------------------------------------------------------------
    def calcular_metricas_generales(
        self,
        df_unificado: pd.DataFrame,
        año: Optional[int] = None,
    ) -> MetricasGenerales:
        if df_unificado is None or df_unificado.empty:
            return MetricasGenerales.vacio()

        año = año or obtener_año_mas_reciente(df_unificado)
        df = filtrar_por_año(df_unificado, año)
        df = filtrar_años_validos(df, AÑOS_PDI)
        df = filtrar_por_fuente(df, FUENTE_AVANCE)
        df = filtrar_indicadores(df)

        stand_by = contar_standby(df)
        df = excluir_standby(df)

        df_full = df.copy()
        if "Cumplimiento" in df_full.columns:
            df_full["Cumplimiento"] = df_full["Cumplimiento"].fillna(0)

        cumpl_promedio = cumplimiento_jerarquico(df_full)

        df_validos = (
            df[df["Cumplimiento"].notna()] if "Cumplimiento" in df.columns else df
        )
        cumplidos = int((df_validos["Cumplimiento"] >= 100).sum()) if "Cumplimiento" in df_validos.columns else 0
        en_progreso = int(((df_validos["Cumplimiento"] >= 80) & (df_validos["Cumplimiento"] < 100)).sum()) if "Cumplimiento" in df_validos.columns else 0
        no_cumplidos = int((df_validos["Cumplimiento"] < 80).sum()) if "Cumplimiento" in df_validos.columns else 0
        total = int(df_validos["Indicador"].nunique()) if "Indicador" in df_validos.columns else len(df_validos)
        total_lineas = int(df["Linea"].nunique()) if "Linea" in df.columns else 0

        return MetricasGenerales(
            cumplimiento_promedio=cumpl_promedio,
            total_indicadores=total,
            indicadores_cumplidos=cumplidos,
            en_progreso=en_progreso,
            no_cumplidos=no_cumplidos,
            stand_by=stand_by,
            total_lineas=total_lineas,
            año_actual=int(año),
        )

    # ------------------------------------------------------------------
    # Cumplimiento por línea
    # ------------------------------------------------------------------
    def cumplimiento_por_linea(
        self,
        df_unificado: pd.DataFrame,
        año: Optional[int] = None,
    ) -> list[CumplimientoLinea]:
        if df_unificado is None or df_unificado.empty:
            return []

        año = año or obtener_año_mas_reciente(df_unificado)
        df = filtrar_por_año(df_unificado, año)
        df = filtrar_indicadores(df)
        df = filtrar_por_fuente(df, FUENTE_AVANCE)
        df = excluir_standby(df)

        if "Linea" not in df.columns or "Cumplimiento" not in df.columns:
            return []

        df_full = df.copy()
        df_full["Cumplimiento"] = df_full["Cumplimiento"].fillna(0)

        resultado: list[CumplimientoLinea] = []

        for linea in df_full["Linea"].dropna().unique():
            df_linea = df_full[df_full["Linea"] == linea]

            if "Objetivo" in df_linea.columns:
                por_obj = df_linea.groupby("Objetivo")["Cumplimiento"].mean()
                cumpl = round(float(por_obj.mean()), 1) if len(por_obj) else 0.0
            else:
                cumpl = round(float(df_linea["Cumplimiento"].mean()), 1)

            df_con_datos = df[df["Linea"] == linea]
            df_con_datos = df_con_datos[df_con_datos["Cumplimiento"].notna()] if "Cumplimiento" in df_con_datos.columns else df_con_datos
            total_ind = int(df_con_datos["Indicador"].nunique()) if "Indicador" in df_con_datos.columns else 0

            resultado.append(CumplimientoLinea(
                linea=linea,
                cumplimiento=cumpl,
                total_indicadores=total_ind,
                color=obtener_color_semaforo(cumpl),
            ))

        return sorted(resultado, key=lambda x: x.cumplimiento, reverse=True)

    # ------------------------------------------------------------------
    # Estado de proyectos
    # ------------------------------------------------------------------
    def calcular_estado_proyectos(
        self,
        df_unificado: pd.DataFrame,
        año: Optional[int] = None,
    ) -> EstadoProyectos:
        if df_unificado is None or df_unificado.empty or "Proyectos" not in df_unificado.columns:
            return EstadoProyectos.vacio()

        df = filtrar_proyectos(df_unificado)
        if df.empty:
            return EstadoProyectos.vacio()

        año = año or obtener_año_mas_reciente(df)
        df = filtrar_por_año(df, año)
        df = df.sort_values(["Indicador", "Año"]).drop_duplicates("Indicador", keep="last")

        def _clasificar(row):
            ejec = row.get("Ejecución")
            ejec_s = str(row.get("Ejecución s", "")).strip().lower()
            if pd.notna(ejec) and ejec == 100:
                return "Finalizado"
            if (pd.isna(ejec) or ejec == 0) and ejec_s == "stand by":
                return "Stand by"
            if pd.notna(ejec) and 0 < ejec < 100:
                return "En ejecución"
            if pd.notna(ejec) and ejec > 0:
                return "En ejecución"
            return "Sin clasificar"

        df["Estado"] = df.apply(_clasificar, axis=1)
        conteo = df["Estado"].value_counts()

        return EstadoProyectos(
            finalizados=int(conteo.get("Finalizado", 0)),
            en_ejecucion=int(conteo.get("En ejecución", 0)),
            stand_by=int(conteo.get("Stand by", 0)),
            sin_clasificar=int(conteo.get("Sin clasificar", 0)),
            total_proyectos=int(len(df)),
        )

    # ------------------------------------------------------------------
    # Histórico de un indicador
    # ------------------------------------------------------------------
    def historico_indicador(
        self,
        df_unificado: pd.DataFrame,
        df_base: pd.DataFrame,
        nombre_indicador: str,
    ) -> tuple[pd.DataFrame, MetadatosIndicador]:
        meta = self._metadatos_indicador(df_base, nombre_indicador)

        if df_unificado is None or df_unificado.empty:
            return pd.DataFrame(), meta

        df_ind = df_unificado[df_unificado["Indicador"] == nombre_indicador].copy()

        # Preferir Cierre sobre Avance
        if "Fuente" in df_ind.columns:
            df_cierre = df_ind[df_ind["Fuente"] == FUENTE_CIERRE]
            df_ind = df_cierre if not df_cierre.empty else df_ind[df_ind["Fuente"] == FUENTE_AVANCE]

        if df_ind.empty:
            return pd.DataFrame(), meta

        if meta.periodicidad.lower() == "semestral" and "Semestre" in df_ind.columns:
            df_ind = df_ind[df_ind["Semestre"].isin([1, 2, "1", "2"])]
            df_ind["Semestre"] = pd.to_numeric(df_ind["Semestre"], errors="coerce").fillna(0).astype(int)
            df_ind["Periodo"] = df_ind.apply(
                lambda r: f"{int(r['Año'])}-S{int(r['Semestre'])}" if pd.notna(r["Año"]) else "",
                axis=1,
            )
            df_ind["Periodo_orden"] = df_ind["Año"] * 10 + df_ind["Semestre"]
            df_ind = df_ind.sort_values("Periodo_orden")
        else:
            if "Semestre" in df_ind.columns:
                df_anual = df_ind[df_ind["Semestre"].isna() | (df_ind["Semestre"] == "") | (df_ind["Semestre"] == 0)]
                if df_anual.empty:
                    df_ind = df_ind.groupby("Año").agg({
                        "Meta": "mean", "Ejecución": "mean", "Cumplimiento": "mean",
                        "Indicador": "first", "Linea": "first", "Objetivo": "first",
                    }).reset_index()
                else:
                    df_ind = df_anual
            df_ind["Periodo"] = df_ind["Año"].apply(lambda x: str(int(x)) if pd.notna(x) else "")
            df_ind["Periodo_orden"] = df_ind["Año"]
            df_ind = df_ind.sort_values("Año")

        return df_ind, meta

    # ------------------------------------------------------------------
    # Estructura cascada
    # ------------------------------------------------------------------
    def calcular_cascada(
        self,
        df_unificado: pd.DataFrame,
        df_base: pd.DataFrame,
        año: Optional[int] = None,
        max_niveles: int = 4,
        filtro_tipo: str = "indicadores",
    ) -> pd.DataFrame:
        if df_unificado is None or df_unificado.empty:
            return pd.DataFrame()

        año = año or obtener_año_mas_reciente(df_unificado)
        df = filtrar_por_año(df_unificado, año)
        df = filtrar_años_validos(df, AÑOS_PDI)
        df = filtrar_por_fuente(df, FUENTE_AVANCE)

        if filtro_tipo == "indicadores":
            df = filtrar_indicadores(df)
        elif filtro_tipo == "proyectos":
            df = filtrar_proyectos(df)

        if "Cumplimiento" in df.columns:
            df = df.copy()
            df["Cumplimiento"] = df["Cumplimiento"].fillna(0)

        if df_base is not None and "Meta_PDI" in df_base.columns and "Indicador" in df.columns:
            meta_dict = df_base.set_index("Indicador")["Meta_PDI"].to_dict()
            df = df.copy()
            df["Meta_PDI"] = df["Indicador"].map(meta_dict)

        filas: list[dict] = []
        if "Linea" not in df.columns:
            return pd.DataFrame()

        for linea in sorted(df["Linea"].dropna().unique()):
            df_linea = df[df["Linea"] == linea]
            if "Objetivo" in df_linea.columns and df_linea["Objetivo"].notna().any():
                por_obj = df_linea.groupby("Objetivo")["Cumplimiento"].mean()
                cumpl_linea = float(por_obj.mean()) if len(por_obj) else 0.0
            else:
                cumpl_linea = float(df_linea["Cumplimiento"].mean()) if "Cumplimiento" in df_linea.columns else 0.0

            filas.append(FilaCascada(1, linea, "", "", "", cumpl_linea,
                                     df_linea["Indicador"].nunique() if "Indicador" in df_linea.columns else len(df_linea)).as_dict())

            if max_niveles >= 2 and "Objetivo" in df_linea.columns:
                for objetivo in sorted(df_linea["Objetivo"].dropna().unique()):
                    df_obj = df_linea[df_linea["Objetivo"] == objetivo]
                    cumpl_obj = float(df_obj["Cumplimiento"].mean()) if "Cumplimiento" in df_obj.columns else 0.0
                    filas.append(FilaCascada(2, linea, objetivo, "", "", cumpl_obj,
                                             df_obj["Indicador"].nunique() if "Indicador" in df_obj.columns else len(df_obj)).as_dict())

                    if max_niveles >= 3 and "Meta_PDI" in df_obj.columns:
                        for meta_pdi in df_obj["Meta_PDI"].dropna().unique():
                            df_meta = df_obj[df_obj["Meta_PDI"] == meta_pdi]
                            cumpl_meta = float(df_meta["Cumplimiento"].mean()) if "Cumplimiento" in df_meta.columns else 0.0
                            filas.append(FilaCascada(3, linea, objetivo, str(meta_pdi), "", cumpl_meta,
                                                     df_meta["Indicador"].nunique() if "Indicador" in df_meta.columns else len(df_meta)).as_dict())

                            if max_niveles >= 4 and "Indicador" in df_meta.columns:
                                for ind in df_meta["Indicador"].unique():
                                    df_i = df_meta[df_meta["Indicador"] == ind]
                                    cumpl_i = float(df_i["Cumplimiento"].iloc[0]) if not df_i.empty else 0.0
                                    filas.append(FilaCascada(4, linea, objetivo, str(meta_pdi), ind, cumpl_i, 1).as_dict())

                    if max_niveles >= 4:
                        df_sin = df_obj[df_obj["Meta_PDI"].isna()] if "Meta_PDI" in df_obj.columns else pd.DataFrame()
                        if not df_sin.empty and "Indicador" in df_sin.columns:
                            for ind in df_sin["Indicador"].unique():
                                df_i = df_sin[df_sin["Indicador"] == ind]
                                cumpl_i = float(df_i["Cumplimiento"].iloc[0]) if not df_i.empty else 0.0
                                filas.append(FilaCascada(4, linea, objetivo, "N/D", ind, cumpl_i, 1).as_dict())

        return pd.DataFrame(filas)

    # ------------------------------------------------------------------
    # Preparación de datos para IA
    # ------------------------------------------------------------------
    def preparar_historico_para_ia(self, df_indicador: pd.DataFrame) -> list[dict]:
        if df_indicador is None or df_indicador.empty:
            return []
        resultado = []
        for _, row in df_indicador.sort_values("Año").iterrows():
            año = int(row["Año"]) if "Año" in row and pd.notna(row["Año"]) else None
            meta = float(row["Meta"]) if "Meta" in row and pd.notna(row["Meta"]) else 0.0
            ejec = float(row["Ejecución"]) if "Ejecución" in row and pd.notna(row["Ejecución"]) else 0.0
            cumpl = (ejec / meta * 100) if meta > 0 else 0.0
            resultado.append({"año": año, "meta": meta, "ejecucion": ejec, "cumplimiento": cumpl})
        return resultado

    def preparar_objetivos_para_ia(
        self,
        df_linea: pd.DataFrame,
        año: Optional[int] = None,
    ) -> list[dict]:
        if df_linea is None or df_linea.empty or "Objetivo" not in df_linea.columns:
            return []
        if año and "Año" in df_linea.columns:
            df_linea = df_linea[df_linea["Año"] == año]
        resultado = []
        for obj in df_linea["Objetivo"].dropna().unique():
            df_o = df_linea[df_linea["Objetivo"] == obj]
            cumpl = df_o["Cumplimiento"].mean() if "Cumplimiento" in df_o.columns else 0.0
            inds = df_o["Indicador"].nunique() if "Indicador" in df_o.columns else len(df_o)
            resultado.append({"objetivo": obj, "cumplimiento": float(cumpl) if pd.notna(cumpl) else 0.0, "indicadores": inds})
        return sorted(resultado, key=lambda x: x["cumplimiento"], reverse=True)

    def preparar_lineas_para_ia(
        self,
        df_unificado: pd.DataFrame,
        año: Optional[int] = None,
    ) -> list[dict]:
        if df_unificado is None or df_unificado.empty or "Linea" not in df_unificado.columns:
            return []
        if año and "Año" in df_unificado.columns:
            df_unificado = df_unificado[df_unificado["Año"] == año]
        resultado = []
        for linea in df_unificado["Linea"].dropna().unique():
            df_l = df_unificado[df_unificado["Linea"] == linea]
            cumpl = df_l["Cumplimiento"].mean() if "Cumplimiento" in df_l.columns else 0.0
            inds = df_l["Indicador"].nunique() if "Indicador" in df_l.columns else len(df_l)
            resultado.append({"linea": linea, "cumplimiento": float(cumpl) if pd.notna(cumpl) else 0.0, "indicadores": inds})
        return sorted(resultado, key=lambda x: x["cumplimiento"], reverse=True)

    # ------------------------------------------------------------------
    # Helpers privados
    # ------------------------------------------------------------------
    @staticmethod
    def _metadatos_indicador(
        df_base: Optional[pd.DataFrame],
        nombre: str,
    ) -> MetadatosIndicador:
        defaults = MetadatosIndicador(nombre=nombre, linea="", objetivo="")
        if df_base is None or df_base.empty or "Indicador" not in df_base.columns:
            return defaults
        rows = df_base[df_base["Indicador"] == nombre]
        if rows.empty:
            return defaults
        r = rows.iloc[0]
        return MetadatosIndicador(
            nombre=nombre,
            linea=str(r.get("Linea", "")) if pd.notna(r.get("Linea")) else "",
            objetivo=str(r.get("Objetivo", "")) if pd.notna(r.get("Objetivo")) else "",
            periodicidad=str(r.get("Periodicidad", "Anual")) if pd.notna(r.get("Periodicidad")) else "Anual",
            sentido=str(r.get("Sentido", "Creciente")) if pd.notna(r.get("Sentido")) else "Creciente",
            unidad_meta=str(r.get("Meta s", "")) if pd.notna(r.get("Meta s")) else "",
            unidad_ejecucion=str(r.get("Ejecución s", "")) if pd.notna(r.get("Ejecución s")) else "",
            meta_pdi=str(r.get("Meta_PDI", "")) if pd.notna(r.get("Meta_PDI")) else "",
            descripcion=str(r.get("Descripcion", "")) if pd.notna(r.get("Descripcion")) else "",
        )
