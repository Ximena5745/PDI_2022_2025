"""
Módulo de carga y procesamiento de datos para el Dashboard Estratégico POLI.
"""

import pandas as pd
import streamlit as st
from pathlib import Path
import unicodedata

# Colores corporativos
COLORS = {
    'primary': '#003d82',
    'secondary': '#0066cc',
    'accent': '#4a90e2',
    'light': '#e8f1f9',
    'gray': '#666666',
    'success': '#28a745',
    'warning': '#ffc107',
    'danger': '#dc3545',
    'white': '#ffffff'
}

# Líneas estratégicas del PDI
LINEAS_ESTRATEGICAS = [
    'Calidad',
    'Expansión',
    'Experiencia',
    'Educación para toda la vida',
    'Transformación organizacional',
    'Sostenibilidad'
]


def normalizar_columnas(df):
    """
    Normaliza los nombres de columnas para manejar tildes y caracteres especiales.
    """
    # Buscar columnas con tildes y crear alias
    columnas_normalizadas = {}
    for col in df.columns:
        # Normalizar removiendo acentos para comparación
        col_normalizado = unicodedata.normalize('NFKD', str(col)).encode('ASCII', 'ignore').decode('ASCII')
        col_normalizado = col_normalizado.strip()

        # Mapear nombres comunes a versiones con tilde para consistencia
        # col_normalizado ya no tiene tildes (fue normalizado con ASCII)
        if col_normalizado == 'Ano':
            columnas_normalizadas[col] = 'Año'
        elif col_normalizado == 'Ejecucion':
            columnas_normalizadas[col] = 'Ejecución'
        elif col_normalizado == 'Clasificacion':
            columnas_normalizadas[col] = 'Clasificación'
        elif col_normalizado == 'Proyeccion':
            columnas_normalizadas[col] = 'Proyección'
        elif col_normalizado == 'CARACTERISTICA':
            columnas_normalizadas[col] = 'CARACTERÍSTICA'

    # Renombrar columnas si es necesario
    if columnas_normalizadas:
        df = df.rename(columns=columnas_normalizadas)

    return df


@st.cache_data(ttl=3600)
def cargar_datos():
    """
    Carga y procesa los datos desde el archivo Excel.

    Returns:
        tuple: (df_indicadores, df_unificado, df_base) DataFrames procesados
    """
    try:
        # Determinar la ruta del archivo
        base_path = Path(__file__).parent.parent
        file_path = base_path / 'Data' / 'Dataset_Unificado.xlsx'

        if not file_path.exists():
            # Intentar ruta alternativa
            file_path = Path('Data/Dataset_Unificado.xlsx')

        if not file_path.exists():
            st.error(f"No se encontró el archivo de datos en: {file_path}")
            return None, None, None

        # Cargar ambas hojas
        df_base = pd.read_excel(file_path, sheet_name='Base_Indicadores', engine='openpyxl')
        df_unificado = pd.read_excel(file_path, sheet_name='Unificado', engine='openpyxl')

        # Limpiar nombres de columnas
        df_base.columns = df_base.columns.str.strip()
        df_unificado.columns = df_unificado.columns.str.strip()

        # Normalizar nombres de columnas (manejar tildes)
        df_base = normalizar_columnas(df_base)
        df_unificado = normalizar_columnas(df_unificado)

        # Procesar datos unificados
        df_unificado = procesar_datos_unificado(df_unificado)

        return df_base, df_unificado, df_base

    except PermissionError:
        st.error("El archivo Excel está abierto en otro programa. Por favor ciérrelo e intente de nuevo.")
        return None, None, None
    except Exception as e:
        st.error(f"Error al cargar datos: {str(e)}")
        return None, None, None


def procesar_datos_unificado(df):
    """
    Procesa y limpia el DataFrame unificado.
    """
    # Asegurar tipos de datos correctos
    if 'Año' in df.columns:
        df['Año'] = pd.to_numeric(df['Año'], errors='coerce')

    if 'Meta' in df.columns:
        df['Meta'] = pd.to_numeric(df['Meta'], errors='coerce')

    if 'Ejecución' in df.columns:
        df['Ejecución'] = pd.to_numeric(df['Ejecución'], errors='coerce')

    if 'Cumplimiento' in df.columns:
        df['Cumplimiento'] = pd.to_numeric(df['Cumplimiento'], errors='coerce')
        # Convertir de decimal a porcentaje si es necesario (valores <= 2 indican formato decimal)
        if df['Cumplimiento'].max() <= 2:
            df['Cumplimiento'] = df['Cumplimiento'] * 100

    # Calcular cumplimiento si no existe
    if 'Cumplimiento' not in df.columns and 'Meta' in df.columns and 'Ejecución' in df.columns:
        df['Cumplimiento'] = df.apply(
            lambda x: calcular_cumplimiento(x['Meta'], x['Ejecución']),
            axis=1
        )

    return df


def calcular_cumplimiento(meta, ejecucion):
    """
    Calcula el porcentaje de cumplimiento.
    """
    if pd.isna(meta) or pd.isna(ejecucion) or meta == 0:
        return None
    return (ejecucion / meta) * 100


def obtener_color_semaforo(cumplimiento):
    """
    Retorna el color del semáforo según el nivel de cumplimiento.

    - Verde: >= 90%
    - Amarillo: 70-89%
    - Rojo: < 70%
    """
    if cumplimiento is None or pd.isna(cumplimiento):
        return COLORS['gray']
    elif cumplimiento >= 90:
        return COLORS['success']
    elif cumplimiento >= 70:
        return COLORS['warning']
    else:
        return COLORS['danger']


def obtener_estado_semaforo(cumplimiento):
    """
    Retorna el estado del semáforo como texto.
    """
    if cumplimiento is None or pd.isna(cumplimiento):
        return 'Sin datos', 'gray'
    elif cumplimiento >= 90:
        return 'Meta cumplida', 'success'
    elif cumplimiento >= 70:
        return 'En progreso', 'warning'
    else:
        return 'Requiere atención', 'danger'


def calcular_metricas_generales(df_unificado, año=None):
    """
    Calcula las métricas generales del dashboard.

    Args:
        df_unificado: DataFrame con datos unificados
        año: Año a filtrar (opcional, usa el más reciente por defecto)

    Returns:
        dict: Diccionario con métricas calculadas
    """
    if df_unificado is None or df_unificado.empty:
        return {
            'cumplimiento_promedio': 0,
            'total_indicadores': 0,
            'metas_cumplidas': 0,
            'en_progreso': 0,
            'requieren_atencion': 0,
            'total_lineas': 0,
            'año_actual': 2025
        }

    # Filtrar por año si se especifica
    if año is None:
        año = df_unificado['Año'].max() if 'Año' in df_unificado.columns else 2025

    df_año = df_unificado[df_unificado['Año'] == año] if 'Año' in df_unificado.columns else df_unificado

    # Calcular métricas
    if 'Cumplimiento' in df_año.columns:
        cumplimiento_promedio = df_año['Cumplimiento'].mean()
        metas_cumplidas = len(df_año[df_año['Cumplimiento'] >= 90])
        en_progreso = len(df_año[(df_año['Cumplimiento'] >= 70) & (df_año['Cumplimiento'] < 90)])
        requieren_atencion = len(df_año[df_año['Cumplimiento'] < 70])
    else:
        cumplimiento_promedio = 0
        metas_cumplidas = 0
        en_progreso = 0
        requieren_atencion = 0

    # Contar indicadores únicos
    total_indicadores = df_año['Indicador'].nunique() if 'Indicador' in df_año.columns else len(df_año)

    # Contar líneas estratégicas
    total_lineas = df_año['Linea'].nunique() if 'Linea' in df_año.columns else 0

    return {
        'cumplimiento_promedio': round(cumplimiento_promedio, 1) if pd.notna(cumplimiento_promedio) else 0,
        'total_indicadores': total_indicadores,
        'metas_cumplidas': metas_cumplidas,
        'en_progreso': en_progreso,
        'requieren_atencion': requieren_atencion,
        'total_lineas': total_lineas,
        'año_actual': año
    }


def obtener_cumplimiento_por_linea(df_unificado, año=None):
    """
    Obtiene el cumplimiento promedio por línea estratégica.
    """
    if df_unificado is None or df_unificado.empty:
        return pd.DataFrame()

    if año is None:
        año = df_unificado['Año'].max() if 'Año' in df_unificado.columns else 2025

    df_año = df_unificado[df_unificado['Año'] == año] if 'Año' in df_unificado.columns else df_unificado

    if 'Linea' in df_año.columns and 'Cumplimiento' in df_año.columns:
        resumen = df_año.groupby('Linea').agg({
            'Cumplimiento': 'mean',
            'Indicador': 'nunique'
        }).reset_index()
        resumen.columns = ['Linea', 'Cumplimiento', 'Total_Indicadores']
        resumen['Cumplimiento'] = resumen['Cumplimiento'].round(1)
        resumen['Color'] = resumen['Cumplimiento'].apply(obtener_color_semaforo)
        return resumen.sort_values('Cumplimiento', ascending=False)

    return pd.DataFrame()


def obtener_historico_indicador(df_unificado, indicador_id):
    """
    Obtiene el histórico de un indicador específico.
    """
    if df_unificado is None or df_unificado.empty:
        return pd.DataFrame()

    if 'Id' in df_unificado.columns:
        df_ind = df_unificado[df_unificado['Id'] == indicador_id].copy()
    elif 'Indicador' in df_unificado.columns:
        df_ind = df_unificado[df_unificado['Indicador'] == indicador_id].copy()
    else:
        return pd.DataFrame()

    if not df_ind.empty and 'Año' in df_ind.columns:
        df_ind = df_ind.sort_values('Año')

    return df_ind


def filtrar_por_linea(df_unificado, linea):
    """
    Filtra los datos por línea estratégica.
    """
    if df_unificado is None or 'Linea' not in df_unificado.columns:
        return df_unificado
    return df_unificado[df_unificado['Linea'] == linea]


def filtrar_por_objetivo(df_unificado, objetivo):
    """
    Filtra los datos por objetivo.
    """
    if df_unificado is None or 'Objetivo' not in df_unificado.columns:
        return df_unificado
    return df_unificado[df_unificado['Objetivo'] == objetivo]


def obtener_lista_indicadores(df_unificado, linea=None, objetivo=None):
    """
    Obtiene la lista de indicadores filtrada.
    """
    if df_unificado is None:
        return []

    df = df_unificado.copy()

    if linea and 'Linea' in df.columns:
        df = df[df['Linea'] == linea]

    if objetivo and 'Objetivo' in df.columns:
        df = df[df['Objetivo'] == objetivo]

    if 'Indicador' in df.columns:
        return sorted(df['Indicador'].unique().tolist())

    return []


def obtener_lista_objetivos(df_unificado, linea=None):
    """
    Obtiene la lista de objetivos filtrada por línea.
    """
    if df_unificado is None:
        return []

    df = df_unificado.copy()

    if linea and 'Linea' in df.columns:
        df = df[df['Linea'] == linea]

    if 'Objetivo' in df.columns:
        return sorted(df['Objetivo'].dropna().unique().tolist())

    return []


def exportar_a_excel(df, nombre_archivo="informe_poli.xlsx"):
    """
    Exporta un DataFrame a Excel.
    """
    import io
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Datos', index=False)
    return buffer.getvalue()
