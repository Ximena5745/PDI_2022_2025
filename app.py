"""
Dashboard Estratégico POLI - Aplicación Principal
Politécnico Grancolombiano - Plan de Desarrollo Institucional 2021-2025
"""

import streamlit as st
from datetime import datetime

# Configuración de la página - DEBE SER LO PRIMERO
st.set_page_config(
    page_title="Informe Estratégico POLI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Importar módulos propios
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from utils.data_loader import cargar_datos, calcular_metricas_generales, COLORS

# CSS personalizado global
st.markdown(f"""
<style>
    /* Fondo principal */
    .main {{
        background-color: #f8f9fa;
    }}

    /* Métricas de Streamlit */
    .stMetric {{
        background-color: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }}

    /* Tarjetas de KPI personalizadas */
    .metric-card {{
        background: linear-gradient(135deg, {COLORS['primary']} 0%, {COLORS['secondary']} 100%);
        padding: 25px;
        border-radius: 12px;
        color: white;
        margin: 10px 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.15);
        text-align: center;
    }}

    .metric-card-light {{
        background: white;
        padding: 25px;
        border-radius: 12px;
        color: {COLORS['primary']};
        margin: 10px 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border-left: 5px solid {COLORS['primary']};
        text-align: center;
    }}

    .metric-value {{
        font-size: 42px;
        font-weight: bold;
        margin: 10px 0;
    }}

    .metric-label {{
        font-size: 14px;
        opacity: 0.9;
        text-transform: uppercase;
        letter-spacing: 1px;
    }}

    /* Títulos */
    h1, h2, h3 {{
        color: {COLORS['primary']};
    }}

    /* Selectores */
    .stSelectbox label {{
        color: {COLORS['primary']};
        font-weight: 600;
    }}

    /* Badges de estado */
    .status-badge {{
        display: inline-block;
        padding: 5px 15px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: bold;
        margin: 5px;
    }}

    .status-green {{
        background-color: {COLORS['success']};
        color: white;
    }}

    .status-yellow {{
        background-color: {COLORS['warning']};
        color: #333;
    }}

    .status-red {{
        background-color: {COLORS['danger']};
        color: white;
    }}

    /* Info box personalizado */
    .info-box {{
        background-color: {COLORS['light']};
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid {COLORS['primary']};
        margin: 15px 0;
    }}

    /* Análisis IA container */
    .ai-analysis {{
        background: linear-gradient(135deg, #f8f9fa 0%, {COLORS['light']} 100%);
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid {COLORS['accent']};
        margin: 15px 0;
    }}

    /* Sidebar styling */
    [data-testid="stSidebar"] {{
        background-color: white;
    }}

    [data-testid="stSidebar"] .stMarkdown {{
        color: {COLORS['primary']};
    }}

    /* Expander styling */
    .streamlit-expanderHeader {{
        background-color: {COLORS['light']};
        border-radius: 5px;
    }}

    /* Data editor / tables */
    .stDataFrame {{
        border-radius: 10px;
        overflow: hidden;
    }}

    /* Botones */
    .stButton > button {{
        background-color: {COLORS['primary']};
        color: white;
        border: none;
        border-radius: 5px;
        padding: 10px 20px;
        font-weight: 600;
    }}

    .stButton > button:hover {{
        background-color: {COLORS['secondary']};
    }}

    /* Download buttons */
    .stDownloadButton > button {{
        background-color: {COLORS['success']};
        color: white;
    }}

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
    }}

    .stTabs [data-baseweb="tab"] {{
        background-color: {COLORS['light']};
        border-radius: 5px 5px 0 0;
        padding: 10px 20px;
    }}

    .stTabs [aria-selected="true"] {{
        background-color: {COLORS['primary']};
        color: white;
    }}

    /* Ocultar menú hamburguesa y footer */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}

    /* Header personalizado */
    .header-container {{
        background: linear-gradient(135deg, {COLORS['primary']} 0%, {COLORS['secondary']} 100%);
        padding: 30px;
        border-radius: 15px;
        color: white;
        margin-bottom: 20px;
        text-align: center;
    }}

    .header-title {{
        font-size: 36px;
        font-weight: bold;
        margin-bottom: 10px;
    }}

    .header-subtitle {{
        font-size: 16px;
        opacity: 0.9;
    }}
</style>
""", unsafe_allow_html=True)


# Cargar datos en estado de sesión para compartir entre páginas
@st.cache_data(ttl=3600)
def cargar_datos_cached():
    return cargar_datos()


# Inicializar datos si no existen en el estado de sesión
if 'datos_cargados' not in st.session_state:
    df_base, df_unificado, _ = cargar_datos_cached()
    st.session_state['df_base'] = df_base
    st.session_state['df_unificado'] = df_unificado
    st.session_state['datos_cargados'] = True


# Sidebar
with st.sidebar:
    # Logo placeholder
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, {COLORS['primary']} 0%, {COLORS['secondary']} 100%);
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        color: white;
        margin-bottom: 20px;
    ">
        <div style="font-size: 24px; font-weight: bold;">📊 POLI</div>
        <div style="font-size: 12px; opacity: 0.9;">Plan Estratégico 2021-2025</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Navegación
    pagina = st.radio(
        "📍 Navegación",
        ["📊 Dashboard General", "📈 Análisis por Línea", "🔍 Detalle de Indicadores"],
        label_visibility="visible"
    )

    st.markdown("---")

    # Información del informe
    st.markdown("### 📋 Información")

    df_unificado = st.session_state.get('df_unificado')
    total_indicadores = 0
    if df_unificado is not None and 'Indicador' in df_unificado.columns:
        total_indicadores = df_unificado['Indicador'].nunique()

    st.info(f"""
    **Periodo:** 2021-2025
    **Última actualización:** {datetime.now().strftime('%d/%m/%Y')}
    **Total indicadores:** {total_indicadores}
    """)

    st.markdown("---")

    # Botón de actualización
    if st.button("🔄 Actualizar Datos", use_container_width=True):
        st.cache_data.clear()
        for key in ['df_base', 'df_unificado', 'datos_cargados']:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

    # Leyenda de semáforo
    st.markdown("### 🚦 Semáforo")
    st.markdown(f"""
    <div style="padding: 10px; background: white; border-radius: 5px;">
        <div style="margin: 5px 0;">
            <span style="display: inline-block; width: 12px; height: 12px; background: {COLORS['success']}; border-radius: 50%;"></span>
            <small> ≥90% Meta cumplida</small>
        </div>
        <div style="margin: 5px 0;">
            <span style="display: inline-block; width: 12px; height: 12px; background: {COLORS['warning']}; border-radius: 50%;"></span>
            <small> 70-89% En progreso</small>
        </div>
        <div style="margin: 5px 0;">
            <span style="display: inline-block; width: 12px; height: 12px; background: {COLORS['danger']}; border-radius: 50%;"></span>
            <small> &lt;70% Requiere atención</small>
        </div>
    </div>
    """, unsafe_allow_html=True)


# Guardar página seleccionada en estado de sesión
st.session_state['pagina_actual'] = pagina


# Importar y mostrar la página correspondiente
if pagina == "📊 Dashboard General":
    from views import dashboard
    dashboard.mostrar_pagina()

elif pagina == "📈 Análisis por Línea":
    from views import analisis_linea
    analisis_linea.mostrar_pagina()

elif pagina == "🔍 Detalle de Indicadores":
    from views import detalle_indicador
    detalle_indicador.mostrar_pagina()


# Footer
st.markdown("---")
st.markdown(f"""
<div style="text-align: center; color: {COLORS['gray']}; font-size: 12px; padding: 20px;">
    <strong>Dashboard Estratégico POLI</strong> | Politécnico Grancolombiano | Plan de Desarrollo Institucional 2021-2025<br>
    <em>Generado automáticamente el {datetime.now().strftime('%d/%m/%Y a las %H:%M')}</em>
</div>
""", unsafe_allow_html=True)
