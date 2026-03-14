"""
Estilos CSS globales del Dashboard Estratégico POLI.
Extraído de app.py para mantener la presentación separada del routing.
"""

from __future__ import annotations

import streamlit as st
from core.config import COLORS


def inject_global_css() -> None:
    """Inyecta el CSS corporativo en la página activa de Streamlit."""
    st.markdown(_build_css(), unsafe_allow_html=True)


def _build_css() -> str:
    c = COLORS
    return f"""
<style>
    /* ── Fondo principal ── */
    .main {{ background-color: #f8f9fa; }}

    /* ── Métricas nativas ── */
    .stMetric {{
        background-color: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }}

    /* ── Tarjetas KPI (gradiente) ── */
    .metric-card {{
        background: linear-gradient(135deg, {c['primary']} 0%, {c['secondary']} 100%);
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
        color: {c['primary']};
        margin: 10px 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border-left: 5px solid {c['primary']};
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

    /* ── Títulos ── */
    h1, h2, h3 {{ color: {c['primary']}; }}

    /* ── Selectores ── */
    .stSelectbox label {{ color: {c['primary']}; font-weight: 600; }}

    /* ── Badges de estado ── */
    .status-badge {{
        display: inline-block;
        padding: 5px 15px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: bold;
        margin: 5px;
    }}
    .status-green {{ background-color: {c['success']}; color: white; }}
    .status-yellow {{ background-color: {c['warning']}; color: #333; }}
    .status-red {{ background-color: {c['danger']}; color: white; }}

    /* ── Info box ── */
    .info-box {{
        background-color: {c['light']};
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid {c['primary']};
        margin: 15px 0;
    }}

    /* ── Análisis IA ── */
    .ai-analysis {{
        background: linear-gradient(135deg, #f8f9fa 0%, {c['light']} 100%);
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid {c['accent']};
        margin: 15px 0;
    }}

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {{ background-color: white; }}
    [data-testid="stSidebar"] .stMarkdown {{ color: {c['primary']}; }}

    /* ── Expander ── */
    .streamlit-expanderHeader {{
        background-color: {c['light']};
        border-radius: 5px;
    }}

    /* ── Tablas ── */
    .stDataFrame {{ border-radius: 10px; overflow: hidden; }}

    /* ── Botones ── */
    .stButton > button {{
        background-color: {c['primary']};
        color: white;
        border: none;
        border-radius: 5px;
        padding: 10px 20px;
        font-weight: 600;
    }}
    .stButton > button:hover {{ background-color: {c['secondary']}; }}
    .stDownloadButton > button {{ background-color: {c['success']}; color: white; }}

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"] {{ gap: 8px; }}
    .stTabs [data-baseweb="tab"] {{
        background-color: {c['light']};
        border-radius: 5px 5px 0 0;
        padding: 10px 20px;
    }}
    .stTabs [aria-selected="true"] {{
        background-color: {c['primary']};
        color: white;
    }}

    /* ── Ocultar chrome de Streamlit ── */
    #MainMenu {{ visibility: hidden; }}
    footer {{ visibility: hidden; }}

    /* ── Header corporativo ── */
    .header-container {{
        background: linear-gradient(135deg, {c['primary']} 0%, {c['secondary']} 100%);
        padding: 30px;
        border-radius: 15px;
        color: white;
        margin-bottom: 20px;
        text-align: center;
    }}
    .header-title {{ font-size: 36px; font-weight: bold; margin-bottom: 10px; }}
    .header-subtitle {{ font-size: 16px; opacity: 0.9; }}
</style>
"""
