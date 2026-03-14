"""
Configuración central del Dashboard Estratégico POLI.
Constantes corporativas, paleta de colores y catálogos del PDI.
"""

# ---------------------------------------------------------------------------
# Paleta corporativa
# ---------------------------------------------------------------------------
COLORS: dict[str, str] = {
    "primary":       "#003d82",
    "secondary":     "#0066cc",
    "accent":        "#4a90e2",
    "light":         "#e8f1f9",
    "gray":          "#666666",
    "success":       "#28a745",
    "warning":       "#ffc107",
    "danger":        "#dc3545",
    "white":         "#ffffff",
    "standby":       "#6c757d",
    "unclassified":  "#A0522D",
}

# ---------------------------------------------------------------------------
# Colores por línea estratégica
# ---------------------------------------------------------------------------
COLORES_LINEAS: dict[str, str] = {
    "Expansión":                        "#FBAF17",
    "Transformación organizacional":    "#42F2F2",
    "Transformación_Organizacional":    "#42F2F2",
    "Calidad":                          "#EC0677",
    "Experiencia":                      "#1FB2DE",
    "Sostenibilidad":                   "#A6CE38",
    "Educación para toda la vida":      "#0F385A",
    "Educación_para_toda_la_vida":      "#0F385A",
}

# ---------------------------------------------------------------------------
# Catálogo de líneas estratégicas PDI 2021-2025
# ---------------------------------------------------------------------------
LINEAS_ESTRATEGICAS: list[str] = [
    "Calidad",
    "Expansión",
    "Experiencia",
    "Educación para toda la vida",
    "Transformación organizacional",
    "Sostenibilidad",
]

# ---------------------------------------------------------------------------
# Años válidos del PDI (excluye 2021 que es línea base)
# ---------------------------------------------------------------------------
AÑOS_PDI: list[int] = [2022, 2023, 2024, 2025, 2026]
AÑO_LINEA_BASE: int = 2021

# ---------------------------------------------------------------------------
# Umbrales del semáforo
# ---------------------------------------------------------------------------
UMBRAL_CUMPLIDO: float = 100.0
UMBRAL_ALERTA: float = 80.0

# ---------------------------------------------------------------------------
# Objetivos con estado especial
# ---------------------------------------------------------------------------
OBJETIVO_STANDBY: str = (
    "Incursionar en los niveles de educación media y de educación "
    "para el trabajo y el desarrollo humano"
)

# ---------------------------------------------------------------------------
# Fuentes de datos válidas
# ---------------------------------------------------------------------------
FUENTE_AVANCE: str = "Avance"
FUENTE_CIERRE: str = "Cierre"

# ---------------------------------------------------------------------------
# Ruta del dataset principal (relativa a la raíz del proyecto)
# ---------------------------------------------------------------------------
DATA_DIR: str = "data"
DATASET_FILENAME: str = "Dataset_Unificado.xlsx"
SHEET_BASE: str = "Base_Indicadores"
SHEET_UNIFICADO: str = "Unificado"
CACHE_ANALISIS_PATH: str = "data/cache/analisis_cache.json"
