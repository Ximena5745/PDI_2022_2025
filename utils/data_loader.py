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
    'white': '#ffffff',
    'standby': '#6c757d'  # Gris para objetivos en Stand by
}

# Objetivo en estado Stand by (0% de avance)
OBJETIVO_STANDBY = "Incursionar en los niveles de educación media y de educación para el trabajo y el desarrollo humano"

# Colores representativos de cada Línea Estratégica
COLORES_LINEAS = {
    "Expansión": "#FBAF17",
    "Transformación organizacional": "#42F2F2",
    "Transformación_Organizacional": "#42F2F2",  # Soporte para nombre con guiones bajos
    "Calidad": "#EC0677",
    "Experiencia": "#1FB2DE",
    "Sostenibilidad": "#A6CE38",
    "Educación para toda la vida": "#0F385A",
    "Educación_para_toda_la_vida": "#0F385A"  # Soporte para nombre con guiones bajos
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
    Usa normalización ASCII para comparación robusta.
    """
    mapeo = {}

    for col in df.columns:
        # Normalizar a ASCII para comparación
        try:
            col_ascii = unicodedata.normalize('NFKD', str(col)).encode('ASCII', 'ignore').decode('ASCII').strip().lower()
        except Exception:
            col_ascii = str(col).lower()

        # Mapear basado en versión ASCII
        if col_ascii == 'ano' and col != 'Año':
            mapeo[col] = 'Año'
        elif col_ascii == 'ejecucion' and col != 'Ejecución':
            mapeo[col] = 'Ejecución'
        elif col_ascii == 'clasificacion' and col != 'Clasificación':
            mapeo[col] = 'Clasificación'
        elif col_ascii == 'proyeccion' and col != 'Proyección':
            mapeo[col] = 'Proyección'
        elif col_ascii == 'caracteristica' and col != 'CARACTERÍSTICA':
            mapeo[col] = 'CARACTERÍSTICA'
        elif col_ascii == 'ejecucion s' and col != 'Ejecución s':
            mapeo[col] = 'Ejecución s'

    # Renombrar columnas
    if mapeo:
        df = df.rename(columns=mapeo)

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


def calcular_cumplimiento(meta, ejecucion, sentido='Creciente'):
    """
    Calcula el porcentaje de cumplimiento considerando el sentido del indicador.

    Args:
        meta: Valor de la meta
        ejecucion: Valor de la ejecución
        sentido: 'Creciente' (mayor es mejor) o 'Decreciente' (menor es mejor)

    Returns:
        Porcentaje de cumplimiento
    """
    if pd.isna(meta) or pd.isna(ejecucion) or meta == 0:
        return None

    if sentido == 'Decreciente':
        # Para indicadores decrecientes, menor ejecución es mejor
        # Si la ejecución es menor o igual a la meta, cumplimiento >= 100%
        if ejecucion <= meta:
            return 100 + ((meta - ejecucion) / meta) * 100
        else:
            return (meta / ejecucion) * 100
    else:
        # Indicador creciente (mayor es mejor)
        return (ejecucion / meta) * 100


def obtener_color_semaforo(cumplimiento, es_standby=False):
    """
    Retorna el color del semáforo según el nivel de cumplimiento.

    - Gris Stand by: Objetivos en pausa
    - Verde: >= 100%
    - Amarillo: 80-99.9%
    - Rojo: 0-79.9%
    """
    if es_standby:
        return COLORS['standby']
    if cumplimiento is None or pd.isna(cumplimiento):
        return COLORS['gray']
    elif cumplimiento >= 100:
        return COLORS['success']
    elif cumplimiento >= 80:
        return COLORS['warning']
    else:
        return COLORS['danger']


def obtener_estado_semaforo(cumplimiento, es_standby=False):
    """
    Retorna el estado del semáforo como texto.
    """
    if es_standby:
        return 'Stand by', 'standby'
    if cumplimiento is None or pd.isna(cumplimiento):
        return 'Sin datos', 'gray'
    elif cumplimiento >= 100:
        return 'Meta cumplida', 'success'
    elif cumplimiento >= 80:
        return 'Alerta', 'warning'
    else:
        return 'Peligro', 'danger'


def es_objetivo_standby(objetivo):
    """
    Verifica si un objetivo está en estado Stand by.
    """
    if objetivo is None or pd.isna(objetivo):
        return False
    return str(objetivo).strip().lower() == OBJETIVO_STANDBY.lower()


def calcular_metricas_generales(df_unificado, año=None):
    """
    Calcula las métricas generales del dashboard.
    Solo considera registros donde Fuente = 'Avance' y Proyectos = 0.
    El cumplimiento se calcula como: promedio de indicadores por objetivo, luego promedio de objetivos por línea.

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
            'indicadores_cumplidos': 0,
            'en_progreso': 0,
            'no_cumplidos': 0,
            'stand_by': 0,
            'total_lineas': 0,
            'año_actual': 2025
        }

    # Filtrar por año si se especifica
    if año is None:
        año = df_unificado['Año'].max() if 'Año' in df_unificado.columns else 2025

    df_año = df_unificado[df_unificado['Año'] == año] if 'Año' in df_unificado.columns else df_unificado

    # Solo considerar años 2022-2026 (omitir 2021 línea base)
    if 'Año' in df_año.columns:
        df_año = df_año[df_año['Año'].isin([2022, 2023, 2024, 2025, 2026])]

    # Filtrar solo registros con Fuente = 'Avance'
    if 'Fuente' in df_año.columns:
        df_año = df_año[df_año['Fuente'] == 'Avance']

    # Filtrar solo indicadores (excluir proyectos: Proyectos = 0)
    if 'Proyectos' in df_año.columns:
        df_año = df_año[df_año['Proyectos'] == 0]

    # Identificar indicadores en Stand by (Ejecución = 0 o NaN y Ejecución s = 'Stand by')
    stand_by = 0
    if 'Ejecución s' in df_año.columns:
        df_standby = df_año[df_año['Ejecución s'].astype(str).str.strip().str.lower() == 'stand by']
        stand_by = df_standby['Indicador'].nunique() if 'Indicador' in df_standby.columns else len(df_standby)
        # Excluir stand by para el cálculo de cumplimiento
        df_año = df_año[df_año['Ejecución s'].astype(str).str.strip().str.lower() != 'stand by']

    # Omitir registros con cumplimiento vacío
    if 'Cumplimiento' in df_año.columns:
        df_año = df_año[df_año['Cumplimiento'].notna()]

    # Calcular cumplimiento jerárquico: indicadores -> objetivos -> líneas
    cumplimiento_promedio = 0
    if 'Cumplimiento' in df_año.columns and not df_año.empty:
        if 'Objetivo' in df_año.columns and 'Linea' in df_año.columns:
            # Paso 1: Promedio de indicadores por objetivo
            df_por_objetivo = df_año.groupby(['Linea', 'Objetivo'])['Cumplimiento'].mean().reset_index()
            # Paso 2: Promedio de objetivos por línea
            df_por_linea = df_por_objetivo.groupby('Linea')['Cumplimiento'].mean().reset_index()
            # Paso 3: Promedio de líneas = cumplimiento general
            cumplimiento_promedio = df_por_linea['Cumplimiento'].mean()
        else:
            cumplimiento_promedio = df_año['Cumplimiento'].mean()

        indicadores_cumplidos = len(df_año[df_año['Cumplimiento'] >= 100])
        en_progreso = len(df_año[(df_año['Cumplimiento'] >= 80) & (df_año['Cumplimiento'] < 100)])
        no_cumplidos = len(df_año[df_año['Cumplimiento'] < 80])
    else:
        cumplimiento_promedio = 0
        indicadores_cumplidos = 0
        en_progreso = 0
        no_cumplidos = 0

    # Contar indicadores únicos (excluyendo stand by)
    total_indicadores = df_año['Indicador'].nunique() if 'Indicador' in df_año.columns else len(df_año)

    # Contar líneas estratégicas
    total_lineas = df_año['Linea'].nunique() if 'Linea' in df_año.columns else 0

    return {
        'cumplimiento_promedio': round(cumplimiento_promedio, 1) if pd.notna(cumplimiento_promedio) else 0,
        'total_indicadores': total_indicadores,
        'indicadores_cumplidos': indicadores_cumplidos,
        'en_progreso': en_progreso,
        'no_cumplidos': no_cumplidos,
        'stand_by': stand_by,
        'total_lineas': total_lineas,
        'año_actual': año
    }


def calcular_estado_proyectos(df_unificado, año=None):
    """
    Calcula el estado de los proyectos (Proyectos=1 en el dataset).

    Clasificación:
    - Finalizado: Ejecución = 100
    - En ejecución: Ejecución > 0 y < 100
    - Stand by: Ejecución vacío o 0, y Ejecución s = 'Stand by'

    Args:
        df_unificado: DataFrame con datos unificados
        año: Año a filtrar (opcional, usa el más reciente por defecto)

    Returns:
        dict: Diccionario con conteo de proyectos por estado
    """
    if df_unificado is None or df_unificado.empty:
        return {
            'finalizados': 0,
            'en_ejecucion': 0,
            'stand_by': 0,
            'total_proyectos': 0
        }

    # Verificar que existe la columna Proyectos
    if 'Proyectos' not in df_unificado.columns:
        return {
            'finalizados': 0,
            'en_ejecucion': 0,
            'stand_by': 0,
            'total_proyectos': 0
        }

    # Filtrar solo proyectos (Proyectos = 1)
    df_proyectos = df_unificado[df_unificado['Proyectos'] == 1].copy()

    if df_proyectos.empty:
        return {
            'finalizados': 0,
            'en_ejecucion': 0,
            'stand_by': 0,
            'total_proyectos': 0
        }

    # Filtrar por año si se especifica
    if año is None:
        año = df_proyectos['Año'].max() if 'Año' in df_proyectos.columns else 2025

    if 'Año' in df_proyectos.columns:
        df_proyectos = df_proyectos[df_proyectos['Año'] == año]

    # Obtener proyectos únicos (última fila por indicador/proyecto)
    df_proyectos = df_proyectos.sort_values(['Indicador', 'Año']).drop_duplicates('Indicador', keep='last')

    # Clasificar proyectos
    def clasificar_proyecto(row):
        ejec = row.get('Ejecución')
        ejec_s = row.get('Ejecución s', '')

        if pd.notna(ejec) and ejec == 100:
            return 'Finalizado'
        elif (pd.isna(ejec) or ejec == 0) and str(ejec_s).strip().lower() == 'stand by':
            return 'Stand by'
        elif pd.notna(ejec) and ejec > 0 and ejec < 100:
            return 'En ejecución'
        else:
            # Si no cumple ninguna condición, clasificar según el valor
            if pd.notna(ejec) and ejec > 0:
                return 'En ejecución'
            return 'Sin clasificar'

    df_proyectos['Estado'] = df_proyectos.apply(clasificar_proyecto, axis=1)

    # Contar por estado
    conteo = df_proyectos['Estado'].value_counts()

    return {
        'finalizados': int(conteo.get('Finalizado', 0)),
        'en_ejecucion': int(conteo.get('En ejecución', 0)),
        'stand_by': int(conteo.get('Stand by', 0)),
        'total_proyectos': len(df_proyectos)
    }


def obtener_cumplimiento_por_linea(df_unificado, año=None):
    """
    Obtiene el cumplimiento promedio por línea estratégica.
    El cumplimiento se calcula como: promedio de indicadores por objetivo, luego promedio de objetivos.
    Solo considera indicadores (Proyectos = 0).
    """
    if df_unificado is None or df_unificado.empty:
        return pd.DataFrame()

    if año is None:
        año = df_unificado['Año'].max() if 'Año' in df_unificado.columns else 2025

    df_año = df_unificado[df_unificado['Año'] == año] if 'Año' in df_unificado.columns else df_unificado

    # Filtrar solo indicadores (excluir proyectos)
    if 'Proyectos' in df_año.columns:
        df_año = df_año[df_año['Proyectos'] == 0]

    # Filtrar solo Fuente = 'Avance'
    if 'Fuente' in df_año.columns:
        df_año = df_año[df_año['Fuente'] == 'Avance']

    # Excluir Stand by
    if 'Ejecución s' in df_año.columns:
        df_año = df_año[df_año['Ejecución s'].astype(str).str.strip().str.lower() != 'stand by']

    # Omitir registros con cumplimiento vacío
    if 'Cumplimiento' in df_año.columns:
        df_año = df_año[df_año['Cumplimiento'].notna()]

    if 'Linea' in df_año.columns and 'Cumplimiento' in df_año.columns:
        if 'Objetivo' in df_año.columns:
            # Cálculo jerárquico: indicadores -> objetivos -> línea
            # Paso 1: Promedio de indicadores por objetivo (por línea)
            df_por_objetivo = df_año.groupby(['Linea', 'Objetivo'])['Cumplimiento'].mean().reset_index()
            # Paso 2: Promedio de objetivos por línea
            resumen = df_por_objetivo.groupby('Linea').agg({
                'Cumplimiento': 'mean'
            }).reset_index()
            # Agregar conteo de indicadores únicos
            indicadores_por_linea = df_año.groupby('Linea')['Indicador'].nunique().reset_index()
            indicadores_por_linea.columns = ['Linea', 'Total_Indicadores']
            resumen = resumen.merge(indicadores_por_linea, on='Linea', how='left')
        else:
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


def obtener_historico_indicador_completo(df_unificado, df_base, indicador_nombre):
    """
    Obtiene el histórico completo de un indicador considerando periodicidad.
    Solo considera registros donde Fuente = 'Cierre'.

    Args:
        df_unificado: DataFrame con datos históricos
        df_base: DataFrame con metadatos de indicadores
        indicador_nombre: Nombre del indicador

    Returns:
        tuple: (df_historico, periodicidad, sentido, unidad_meta, unidad_ejecucion)
    """
    if df_unificado is None or df_unificado.empty:
        return pd.DataFrame(), 'Anual', 'Creciente', '', ''

    # Filtrar por indicador
    df_ind = df_unificado[df_unificado['Indicador'] == indicador_nombre].copy()

    # Filtrar solo registros con Fuente = 'Cierre' para las gráficas de indicadores
    if 'Fuente' in df_ind.columns:
        df_ind = df_ind[df_ind['Fuente'] == 'Cierre']

    if df_ind.empty:
        return pd.DataFrame(), 'Anual', 'Creciente', '', ''

    # Obtener metadatos del indicador
    periodicidad = 'Anual'
    sentido = 'Creciente'
    unidad_meta = ''
    unidad_ejecucion = ''

    if df_base is not None and 'Indicador' in df_base.columns:
        indicador_base = df_base[df_base['Indicador'] == indicador_nombre]
        if not indicador_base.empty:
            fila = indicador_base.iloc[0]
            periodicidad = str(fila.get('Periodicidad', 'Anual')) if pd.notna(fila.get('Periodicidad')) else 'Anual'
            sentido = str(fila.get('Sentido', 'Creciente')) if pd.notna(fila.get('Sentido')) else 'Creciente'
            unidad_meta = str(fila.get('Meta s', '')) if pd.notna(fila.get('Meta s')) else ''
            unidad_ejecucion = str(fila.get('Ejecución s', '')) if pd.notna(fila.get('Ejecución s')) else ''

    # Procesar según periodicidad
    if periodicidad.lower() == 'semestral' and 'Semestre' in df_ind.columns:
        # Filtrar solo registros con semestre 1 o 2
        df_ind = df_ind[df_ind['Semestre'].isin([1, 2, '1', '2'])]
        df_ind['Semestre'] = pd.to_numeric(df_ind['Semestre'], errors='coerce').fillna(0).astype(int)

        # Crear columna de periodo (Año-S#)
        df_ind['Periodo'] = df_ind.apply(
            lambda x: f"{int(x['Año'])}-S{int(x['Semestre'])}" if pd.notna(x['Año']) else '',
            axis=1
        )
        df_ind['Periodo_orden'] = df_ind['Año'] * 10 + df_ind['Semestre']
        df_ind = df_ind.sort_values('Periodo_orden')
    else:
        # Anual: agrupar por año si hay múltiples registros
        if 'Semestre' in df_ind.columns:
            # Intentar filtrar registros sin semestre
            df_anual = df_ind[df_ind['Semestre'].isna() | (df_ind['Semestre'] == '') | (df_ind['Semestre'] == 0)]
            # Si el filtro dejó vacío el dataframe, usar todos los datos agrupados por año
            if df_anual.empty:
                df_ind = df_ind.groupby('Año').agg({
                    'Meta': 'mean',
                    'Ejecución': 'mean',
                    'Cumplimiento': 'mean',
                    'Indicador': 'first',
                    'Linea': 'first',
                    'Objetivo': 'first'
                }).reset_index()
            else:
                df_ind = df_anual

        df_ind['Periodo'] = df_ind['Año'].apply(lambda x: str(int(x)) if pd.notna(x) else '')
        df_ind['Periodo_orden'] = df_ind['Año']
        df_ind = df_ind.sort_values('Año')

    return df_ind, periodicidad, sentido, unidad_meta, unidad_ejecucion


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


def obtener_cumplimiento_cascada(df_unificado, df_base, año=None, max_niveles=4):
    """
    Obtiene el cumplimiento en cascada de hasta 4 niveles:
    1. Por Línea Estratégica
    2. Por Objetivo
    3. Por Meta PDI
    4. Por Indicador

    Solo considera registros donde Fuente = 'Avance'.
    Si no hay información, muestra 0%.

    Args:
        df_unificado: DataFrame con datos de cumplimiento
        df_base: DataFrame con metadatos (Meta_PDI)
        año: Año a filtrar (opcional)
        max_niveles: Número máximo de niveles a incluir (1-4, default 4)

    Returns:
        DataFrame con estructura jerárquica de cumplimiento
    """
    if df_unificado is None or df_unificado.empty:
        return pd.DataFrame()

    # Filtrar por año
    if año is None:
        año = df_unificado['Año'].max() if 'Año' in df_unificado.columns else 2025

    df_año = df_unificado[df_unificado['Año'] == año] if 'Año' in df_unificado.columns else df_unificado

    # Solo considerar años 2022-2026 (omitir 2021 línea base)
    if 'Año' in df_año.columns:
        df_año = df_año[df_año['Año'].isin([2022, 2023, 2024, 2025, 2026])]

    # Filtrar solo registros con Fuente = 'Avance'
    if 'Fuente' in df_año.columns:
        df_año = df_año[df_año['Fuente'] == 'Avance']

    # Omitir registros con cumplimiento vacío
    if 'Cumplimiento' in df_año.columns:
        df_año = df_año[df_año['Cumplimiento'].notna()]

    if df_año.empty:
        return pd.DataFrame()

    # Agregar Meta_PDI al DataFrame
    if df_base is not None and 'Meta_PDI' in df_base.columns:
        meta_pdi_dict = df_base.set_index('Indicador')['Meta_PDI'].to_dict()
        df_año = df_año.copy()
        df_año['Meta_PDI'] = df_año['Indicador'].map(meta_pdi_dict)

    # Crear estructura jerárquica
    cascada = []

    if 'Linea' in df_año.columns:
        for linea in sorted(df_año['Linea'].dropna().unique()):
            df_linea = df_año[df_año['Linea'] == linea]
            cumpl_linea = df_linea['Cumplimiento'].mean() if 'Cumplimiento' in df_linea.columns else 0

            # Nivel 1: Línea
            cascada.append({
                'Nivel': 1,
                'Linea': linea,
                'Objetivo': '',
                'Meta_PDI': '',
                'Indicador': '',
                'Cumplimiento': cumpl_linea,
                'Total_Indicadores': df_linea['Indicador'].nunique() if 'Indicador' in df_linea.columns else len(df_linea)
            })

            # Nivel 2: Objetivos
            if max_niveles >= 2 and 'Objetivo' in df_linea.columns:
                for objetivo in sorted(df_linea['Objetivo'].dropna().unique()):
                    df_obj = df_linea[df_linea['Objetivo'] == objetivo]
                    cumpl_obj = df_obj['Cumplimiento'].mean() if 'Cumplimiento' in df_obj.columns else 0

                    cascada.append({
                        'Nivel': 2,
                        'Linea': linea,
                        'Objetivo': objetivo,
                        'Meta_PDI': '',
                        'Indicador': '',
                        'Cumplimiento': cumpl_obj,
                        'Total_Indicadores': df_obj['Indicador'].nunique() if 'Indicador' in df_obj.columns else len(df_obj)
                    })

                    # Nivel 3: Meta PDI
                    if max_niveles >= 3 and 'Meta_PDI' in df_obj.columns:
                        for meta_pdi in df_obj['Meta_PDI'].dropna().unique():
                            df_meta = df_obj[df_obj['Meta_PDI'] == meta_pdi]
                            cumpl_meta = df_meta['Cumplimiento'].mean() if 'Cumplimiento' in df_meta.columns else 0

                            cascada.append({
                                'Nivel': 3,
                                'Linea': linea,
                                'Objetivo': objetivo,
                                'Meta_PDI': str(meta_pdi),
                                'Indicador': '',
                                'Cumplimiento': cumpl_meta,
                                'Total_Indicadores': df_meta['Indicador'].nunique() if 'Indicador' in df_meta.columns else len(df_meta)
                            })

                            # Nivel 4: Indicadores
                            if max_niveles >= 4 and 'Indicador' in df_meta.columns:
                                for indicador in df_meta['Indicador'].unique():
                                    df_ind = df_meta[df_meta['Indicador'] == indicador]
                                    cumpl_ind = df_ind['Cumplimiento'].iloc[0] if 'Cumplimiento' in df_ind.columns and not df_ind.empty else 0

                                    cascada.append({
                                        'Nivel': 4,
                                        'Linea': linea,
                                        'Objetivo': objetivo,
                                        'Meta_PDI': str(meta_pdi),
                                        'Indicador': indicador,
                                        'Cumplimiento': cumpl_ind,
                                        'Total_Indicadores': 1
                                    })

                    # Indicadores sin Meta PDI (solo si max_niveles >= 4)
                    if max_niveles >= 4:
                        df_sin_meta = df_obj[df_obj['Meta_PDI'].isna()] if 'Meta_PDI' in df_obj.columns else df_obj
                        if not df_sin_meta.empty and 'Indicador' in df_sin_meta.columns:
                            for indicador in df_sin_meta['Indicador'].unique():
                                df_ind = df_sin_meta[df_sin_meta['Indicador'] == indicador]
                                cumpl_ind = df_ind['Cumplimiento'].iloc[0] if 'Cumplimiento' in df_ind.columns and not df_ind.empty else 0

                                cascada.append({
                                    'Nivel': 4,
                                    'Linea': linea,
                                    'Objetivo': objetivo,
                                    'Meta_PDI': 'N/D',
                                    'Indicador': indicador,
                                    'Cumplimiento': cumpl_ind,
                                    'Total_Indicadores': 1
                                })

    return pd.DataFrame(cascada)


def exportar_a_excel(df, nombre_archivo="informe_poli.xlsx"):
    """
    Exporta un DataFrame a Excel.
    """
    import io
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Datos', index=False)
    return buffer.getvalue()
