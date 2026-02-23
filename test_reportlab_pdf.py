"""
Script de Prueba - Generador PDF ReportLab
==========================================
Prueba rápida del nuevo generador 3D antes de usar en Streamlit.
"""

import sys
import pandas as pd
from datetime import datetime

# Configurar encoding UTF-8 para Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

from utils.pdf_generator_reportlab import exportar_informe_pdf_reportlab

print("=" * 70)
print(" TEST - Generador PDF Ejecutivo 3D con ReportLab")
print("=" * 70)

# Datos de prueba
print("\n[INFO] Preparando datos de ejemplo...")

metricas = {
    'cumplimiento_promedio': 104.0,
    'total_indicadores': 34,
    'indicadores_cumplidos': 27,
    'en_progreso': 7,
    'no_cumplidos': 0
}

df_lineas = pd.DataFrame({
    'Linea': ['Expansión', 'Calidad', 'Sostenibilidad', 'Experiencia',
              'Transformacion_Organizacional', 'Educacion_para_toda_la_vida'],
    'Cumplimiento': [106.7, 103.3, 95.9, 103.4, 109.4, 105.6],
    'Total_Indicadores': [10, 4, 7, 4, 5, 4]
})

df_indicadores = pd.DataFrame({
    'Indicador': ['Total Población', 'Estudiantes Presencial', 'Estudiantes Virtual',
                  'Productos de investigación', 'Estudiantes vinculados a investigación'],
    'Linea': ['Expansión', 'Expansión', 'Expansión', 'Calidad', 'Calidad'],
    'Meta': [55756, 16981, 92409, 2531, 5],
    'Ejecucion': [56807, 17472, 95964, 2383, 5.86],
    'Cumplimiento': [101.9, 102.9, 103.8, 94.2, 117.2]
})

analisis_texto = """
El PDI 2021-2025 exhibe un cumplimiento general del 104.0%, superando las metas establecidas.
Las líneas estratégicas de Expansión (106.7%) y Transformación Organizacional (109.4%)
muestran el mejor desempeño. La tendencia general es positiva, sugiriendo una ejecución exitosa.
"""

analisis_lineas = {
    'Expansión': 'La línea alcanzó un 106.7% de cumplimiento, impulsada por el crecimiento en matrículas B2B y B2G.',
    'Calidad': 'Con un 103.3% de cumplimiento, mantiene la acreditación institucional vigente.',
    'Sostenibilidad': 'Presenta un 95.9% de cumplimiento, con oportunidades de mejora en eficiencia energética.'
}

print("✓ Datos preparados")

# Generar PDF
print("\n🎯 Generando PDF con ReportLab...")
try:
    pdf_bytes = exportar_informe_pdf_reportlab(
        metricas=metricas,
        df_lineas=df_lineas,
        df_indicadores=df_indicadores,
        analisis_texto=analisis_texto,
        año=2026,
        df_cascada=df_lineas,
        analisis_lineas=analisis_lineas
    )

    # Guardar archivo
    filename = f'Test_PDF_Ejecutivo_3D_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
    with open(filename, 'wb') as f:
        f.write(pdf_bytes)

    tamaño_kb = len(pdf_bytes) / 1024

    print("\n" + "=" * 70)
    print(" ✅ PDF GENERADO EXITOSAMENTE")
    print("=" * 70)
    print(f"\n  📄 Archivo: {filename}")
    print(f"  📊 Tamaño: {tamaño_kb:.1f} KB")
    print(f"  🎯 Características:")
    print(f"     • Gráficos circulares 3D")
    print(f"     • Tabla de contenidos con enlaces")
    print(f"     • Barras de progreso 3D")
    print(f"     • Análisis por línea estratégica")
    print(f"     • Glosario de siglas")
    print(f"     • Diseño ejecutivo moderno")
    print("\n" + "=" * 70)

except Exception as e:
    print("\n" + "=" * 70)
    print(" ❌ ERROR AL GENERAR PDF")
    print("=" * 70)
    print(f"\n  Error: {str(e)}")

    import traceback
    print("\n  Detalles:")
    print(traceback.format_exc())
    print("\n" + "=" * 70)
