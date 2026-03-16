# -*- coding: utf-8 -*-
"""
pdf_colors.py — Paleta de colores, constantes de líneas y glosario PDI.
"""
from __future__ import annotations

from typing import Dict, List

from reportlab.lib import colors


# ============================================================
# PALETA DE COLORES
# ============================================================

# ── Semáforo (valores actualizados al sistema de diseño) ──────
C_VERDE   = colors.HexColor('#10B981')   # GREEN_SOLID
C_NARANJA = colors.HexColor('#F59E0B')   # AMBER_SOLID
C_ROJO    = colors.HexColor('#EF4444')   # RED_SOLID

# ── Institucionales ───────────────────────────────────────────
C_NAVY    = colors.HexColor('#0a2240')
C_ACCENT  = colors.HexColor('#1e88e5')
C_WHITE   = colors.white
C_BG      = colors.HexColor('#F8FAFC')
C_DARK    = colors.HexColor('#1E293B')   # TEXT_PRIMARY
C_GRAY    = colors.HexColor('#64748B')   # TEXT_SECONDARY
C_LIGHT   = colors.HexColor('#E2EAF4')   # TABLE_BORDER
C_SHADOW  = colors.HexColor('#cbd5e1')
C_RING_BG     = colors.HexColor('#e8ecef')
C_TABLE_ROW_ALT = colors.HexColor('#F0F5FB')
C_HDR_GRAD_END  = colors.HexColor('#1a3a5c')

# ── Paleta global del sistema de diseño ───────────────────────
NAVY_DARK      = colors.HexColor('#0a2240')
NAVY_MID       = colors.HexColor('#1a3a5c')
TEAL_ACCENT    = colors.HexColor('#00c9b1')
BG_PAGE        = colors.HexColor('#F8FAFC')
GREEN_SOLID    = colors.HexColor('#10B981')
GREEN_BG       = colors.HexColor('#DCFCE7')
GREEN_TEXT     = colors.HexColor('#166534')
AMBER_SOLID    = colors.HexColor('#F59E0B')
AMBER_BG       = colors.HexColor('#FEF3C7')
AMBER_TEXT     = colors.HexColor('#92400E')
RED_SOLID      = colors.HexColor('#EF4444')
RED_BG         = colors.HexColor('#FEE2E2')
RED_TEXT       = colors.HexColor('#991B1B')
GRAY_ND        = colors.HexColor('#94A3B8')
TABLE_BORDER   = colors.HexColor('#E2EAF4')
TEXT_PRIMARY   = colors.HexColor('#1E293B')
TEXT_SECONDARY = colors.HexColor('#64748B')
TEXT_MUTED     = colors.HexColor('#94A3B8')
AI_BORDER_COL  = colors.HexColor('#0891B2')
AI_BADGE_END   = colors.HexColor('#7C3AED')
AI_BG_COL      = colors.HexColor('#F0F9FF')
AI_TEXT_COL    = colors.HexColor('#334155')

# ── Orden obligatorio de líneas en todo el documento ──────────
ORDEN_LINEAS: List[str] = [
    'Calidad',
    'Expansión',
    'Educación para toda la vida',
    'Experiencia',
    'Transformación Organizacional',
    'Sostenibilidad',
]

# Por línea estratégica (con y sin tilde)
COLOR_LINEAS: Dict[str, colors.Color] = {
    'Expansión':                         colors.HexColor('#FBAF17'),
    'Expansion':                         colors.HexColor('#FBAF17'),
    'Transformación Organizacional':     colors.HexColor('#42F2F2'),
    'Transformacion Organizacional':     colors.HexColor('#42F2F2'),
    'Calidad':                           colors.HexColor('#EC0677'),
    'Experiencia':                       colors.HexColor('#1FB2DE'),
    'Sostenibilidad':                    colors.HexColor('#A6CE38'),
    'Educación para toda la vida':       colors.HexColor('#0F385A'),
    'Educacion para toda la vida':       colors.HexColor('#0F385A'),
}

GLOSARIO = {
    'PDI':    'Plan de Desarrollo Institucional',
    'KPI':    'Key Performance Indicator (Indicador Clave de Desempeño)',
    'B2B':    'Business to Business (Negocio a Negocio)',
    'B2G':    'Business to Government (Negocio a Gobierno)',
    'NPS':    'Net Promoter Score (Índice de Satisfacción)',
    'EBITDA': 'Earnings Before Interest, Taxes, Depreciation and Amortization',
    'ANS':    'Acuerdo de Nivel de Servicio',
    'IA':     'Inteligencia Artificial',
}
