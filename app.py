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
    initial_sidebar_state="collapsed"
)

# Importar módulos propios
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from utils.data_loader import cargar_datos, calcular_metricas_generales, COLORS
from components.styling import inject_global_css

# CSS personalizado global
inject_global_css()



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
        ["📊 Dashboard General", "🎯 CMI Estratégico", "📈 Análisis por Línea", "🔍 Detalle de Indicadores"],
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
    **Periodo:** 2022-2025
    **Última actualización:** {datetime.now().strftime('%d/%m/%Y')}
    **Total Indicadores:** {total_indicadores}
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
            <small> ≥100% Meta cumplida</small>
        </div>
        <div style="margin: 5px 0;">
            <span style="display: inline-block; width: 12px; height: 12px; background: {COLORS['warning']}; border-radius: 50%;"></span>
            <small> 80-99% Alerta</small>
        </div>
        <div style="margin: 5px 0;">
            <span style="display: inline-block; width: 12px; height: 12px; background: {COLORS['danger']}; border-radius: 50%;"></span>
            <small> &lt;80% Peligro</small>
        </div>
    </div>
    """, unsafe_allow_html=True)


# Guardar página seleccionada en estado de sesión
st.session_state['pagina_actual'] = pagina


# Importar y mostrar la página correspondiente
if pagina == "📊 Dashboard General":
    from views import dashboard
    dashboard.mostrar_pagina()

elif pagina == "🎯 CMI Estratégico":
    from views import cmi_estrategico
    cmi_estrategico.mostrar_pagina()

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
