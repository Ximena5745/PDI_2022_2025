"""
Script de Integración del Generador de PDF Mejorado
===================================================

Este script muestra cómo integrar el nuevo generador de PDF mejorado
con tu aplicación Streamlit existente del Dashboard Estratégico POLI.

Incluye:
- Carga de datos reales desde Dataset_Unificado.xlsx
- Generación de análisis IA por línea (opcional)
- Exportación del PDF mejorado
- Compatibilidad con el sistema actual
"""

from datetime import datetime
from typing import Dict, Optional
import pandas as pd

# Importar módulos del sistema existente
from utils.data_loader import (
    cargar_datos,
    calcular_metricas_generales,
    obtener_cumplimiento_por_linea,
    obtener_cumplimiento_cascada
)

# Importar el nuevo generador mejorado
from utils.pdf_generator_mejorado import exportar_informe_pdf_mejorado


def generar_analisis_ia_simple(df_lineas: pd.DataFrame,
                                 metricas: Dict) -> tuple:
    """
    Genera análisis IA simplificado (sin API de IA real).
    Reemplazar con tu módulo utils.ai_analysis si está disponible.

    Returns:
        tuple: (analisis_general, analisis_por_linea)
    """
    cumpl_global = metricas.get('cumplimiento_promedio', 0)
    total_ind = metricas.get('total_indicadores', 0)
    cumplidos = metricas.get('indicadores_cumplidos', 0)
    en_progreso = metricas.get('en_progreso', 0)

    # Análisis general
    analisis_general = f"""
El Plan de Desarrollo Institucional presenta un cumplimiento global del {cumpl_global:.1f}%,
evidenciando el compromiso institucional con la excelencia académica. De un total de {total_ind}
indicadores evaluados, {cumplidos} han alcanzado o superado su meta, mientras que {en_progreso}
se encuentran en progreso satisfactorio.

Los resultados reflejan el avance estratégico en las seis líneas del PDI, destacando
especialmente aquellas que superaron el 100% de cumplimiento. Se requiere mantener el
monitoreo continuo y fortalecer las áreas con oportunidades de mejora.
"""

    # Análisis por línea (básico)
    analisis_lineas = {}

    if df_lineas is not None and not df_lineas.empty:
        for _, row in df_lineas.iterrows():
            linea = row.get('Linea', '')
            cumpl = row.get('Cumplimiento', 0)
            n_ind = row.get('Total_Indicadores', 0)

            if cumpl >= 100:
                estado = "superando exitosamente las metas establecidas"
            elif cumpl >= 80:
                estado = "con avance satisfactorio hacia el cumplimiento de objetivos"
            else:
                estado = "requiriendo atención prioritaria y planes de acción específicos"

            analisis_lineas[linea] = (
                f"La línea estratégica '{linea}' registra un cumplimiento del {cumpl:.1f}% "
                f"con {n_ind} indicadores evaluados, {estado}. Se recomienda continuar con "
                f"el seguimiento sistemático y ajustes según corresponda."
            )

    return analisis_general.strip(), analisis_lineas


def generar_pdf_mejorado_con_datos_reales(año: int = 2025,
                                            usar_analisis_ia: bool = False) -> bytes:
    """
    Genera el PDF mejorado usando datos reales del sistema.

    Args:
        año: Año del informe (default: 2025)
        usar_analisis_ia: Si debe usar análisis IA real (requiere utils.ai_analysis)

    Returns:
        bytes: Contenido del PDF generado
    """
    print(f"\n{'='*70}")
    print(f"  GENERANDO INFORME ESTRATÉGICO MEJORADO - AÑO {año}")
    print(f"{'='*70}\n")

    # 1. CARGAR DATOS
    print("📊 Cargando datos del sistema...")
    df_base, df_unificado, _ = cargar_datos()

    if df_unificado is None or df_unificado.empty:
        raise ValueError("No se pudieron cargar los datos del sistema")

    print("✓ Datos cargados correctamente")

    # 2. CALCULAR MÉTRICAS
    print("🔢 Calculando métricas globales...")
    metricas = calcular_metricas_generales(df_unificado, año=año)

    print(f"✓ Cumplimiento global: {metricas['cumplimiento_promedio']:.1f}%")
    print(f"✓ Total indicadores: {metricas['total_indicadores']}")

    # 3. OBTENER CUMPLIMIENTO POR LÍNEA
    print("📈 Analizando cumplimiento por línea estratégica...")
    df_lineas = obtener_cumplimiento_por_linea(df_unificado, año=año)

    if df_lineas is not None and not df_lineas.empty:
        print(f"✓ {len(df_lineas)} líneas estratégicas procesadas")
    else:
        print("⚠ No se encontraron datos de líneas")

    # 4. OBTENER ESTRUCTURA CASCADA
    print("🌊 Generando estructura jerárquica (cascada)...")
    df_cascada = obtener_cumplimiento_cascada(
        df_unificado,
        df_base,
        año=año,
        max_niveles=4,
        filtro_tipo='indicadores'
    )

    if df_cascada is not None and not df_cascada.empty:
        print(f"✓ Estructura cascada generada: {len(df_cascada)} niveles")
    else:
        print("⚠ No se pudo generar estructura cascada")

    # 5. FILTRAR INDICADORES
    print("📋 Filtrando indicadores del año...")
    df_indicadores = df_unificado[
        (df_unificado['Año'] == año) &
        (df_unificado['Fuente'] == 'Avance') &
        (df_unificado['Proyectos'] == 0)
    ].copy()

    print(f"✓ {len(df_indicadores)} indicadores filtrados")

    # 6. GENERAR ANÁLISIS IA
    print("🤖 Generando análisis ejecutivo...")

    if usar_analisis_ia:
        try:
            # Intentar usar módulo de IA real
            from utils.ai_analysis import generar_analisis_completo
            analisis_general, analisis_lineas = generar_analisis_completo(
                df_unificado, df_lineas, año
            )
            print("✓ Análisis IA generado")
        except ImportError:
            print("⚠ Módulo de IA no disponible, usando análisis simplificado")
            analisis_general, analisis_lineas = generar_analisis_ia_simple(
                df_lineas, metricas
            )
    else:
        analisis_general, analisis_lineas = generar_analisis_ia_simple(
            df_lineas, metricas
        )
        print("✓ Análisis simplificado generado")

    # 7. GENERAR PDF
    print("\n📄 Generando PDF mejorado...")
    pdf_bytes = exportar_informe_pdf_mejorado(
        metricas=metricas,
        df_lineas=df_lineas,
        df_indicadores=df_indicadores,
        analisis_texto=analisis_general,
        año=año,
        df_cascada=df_cascada,
        analisis_lineas=analisis_lineas
    )

    print(f"✓ PDF generado: {len(pdf_bytes) / 1024:.1f} KB")

    return pdf_bytes


def agregar_boton_streamlit():
    """
    Ejemplo de código para agregar el botón en tu app Streamlit.
    Copiar este código en tu archivo principal de Streamlit.
    """
    codigo_ejemplo = """
# ============================================================================
# AGREGAR EN TU APP STREAMLIT (app.py o views/dashboard.py)
# ============================================================================

import streamlit as st
from datetime import datetime
from integracion_pdf_mejorado import generar_pdf_mejorado_con_datos_reales

# En la sección donde tienes los botones de exportación:

st.markdown("### 📥 Exportar Informes")

col1, col2 = st.columns(2)

with col1:
    # Botón del PDF original (mantener compatibilidad)
    if st.button("📄 Descargar PDF Original", use_container_width=True):
        # Usar generador original
        from utils.pdf_generator import exportar_informe_pdf
        pdf_bytes = exportar_informe_pdf(
            metricas=metricas,
            df_lineas=df_lineas,
            df_indicadores=df_indicadores,
            año=año_seleccionado
        )
        st.download_button(
            label="⬇️ Descargar",
            data=pdf_bytes,
            file_name=f"Informe_POLI_{año_seleccionado}.pdf",
            mime="application/pdf"
        )

with col2:
    # NUEVO: Botón del PDF mejorado
    if st.button("✨ Descargar PDF Mejorado", use_container_width=True, type="primary"):
        with st.spinner("Generando informe mejorado..."):
            try:
                pdf_bytes = generar_pdf_mejorado_con_datos_reales(
                    año=año_seleccionado,
                    usar_analisis_ia=True  # Cambiar a False si no tienes módulo IA
                )

                fecha_actual = datetime.now().strftime("%Y%m%d")
                nombre_archivo = f"Informe_Estrategico_POLI_{fecha_actual}.pdf"

                st.download_button(
                    label="⬇️ Descargar Informe Mejorado",
                    data=pdf_bytes,
                    file_name=nombre_archivo,
                    mime="application/pdf",
                    help="PDF con visualizaciones mejoradas, análisis IA y glosario"
                )

                st.success("✅ Informe generado exitosamente!")

            except Exception as e:
                st.error(f"❌ Error al generar el informe: {str(e)}")

# También puedes agregar un expander con información del PDF mejorado:
with st.expander("ℹ️ Características del PDF Mejorado"):
    st.markdown(\"\"\"
    **Mejoras incluidas:**
    - ✅ Tarjetas visuales con colores por KPI
    - ✅ Barras de progreso interactivas
    - ✅ Heatmap de líneas estratégicas
    - ✅ Análisis IA por línea
    - ✅ Tabla de indicadores agrupada
    - ✅ Glosario de siglas del PDI
    - ✅ Conclusiones ejecutivas

    **Estructura del informe:**
    1. Portada institucional
    2. Resumen ejecutivo visual
    3. Detalle por línea estratégica (6 líneas)
    4. Tabla de indicadores mejorada
    5. Conclusiones y glosario
    \"\"\")
"""
    return codigo_ejemplo


# ============================================================================
# SCRIPT PRINCIPAL DE PRUEBA
# ============================================================================

if __name__ == '__main__':
    """
    Ejecutar este script directamente para probar la integración
    con datos reales del sistema.
    """
    import sys

    print("\n" + "="*70)
    print("  INTEGRACIÓN PDF MEJORADO - PRUEBA CON DATOS REALES")
    print("="*70)

    try:
        # Generar PDF con datos reales
        pdf_bytes = generar_pdf_mejorado_con_datos_reales(
            año=2025,
            usar_analisis_ia=False  # Cambiar a True si tienes módulo de IA
        )

        # Guardar archivo
        fecha_actual = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_archivo = f'Informe_Estrategico_POLI_Real_{fecha_actual}.pdf'

        with open(nombre_archivo, 'wb') as f:
            f.write(pdf_bytes)

        print("\n" + "="*70)
        print("✅ ¡INTEGRACIÓN EXITOSA!")
        print("="*70)
        print(f"\n📄 Archivo generado: {nombre_archivo}")
        print(f"📊 Tamaño: {len(pdf_bytes) / 1024:.1f} KB")
        print("\n💡 Próximos pasos:")
        print("  1. Revisa el PDF generado")
        print("  2. Copia el código de 'agregar_boton_streamlit()' en tu app")
        print("  3. Prueba el botón en Streamlit")
        print("  4. Ajusta colores/textos según necesites")
        print("\n" + "="*70 + "\n")

        # Mostrar código de integración para Streamlit
        print("\n📋 CÓDIGO PARA STREAMLIT:\n")
        print(agregar_boton_streamlit())

    except Exception as e:
        print("\n" + "="*70)
        print("❌ ERROR EN LA INTEGRACIÓN")
        print("="*70)
        print(f"\nError: {str(e)}\n")

        import traceback
        traceback.print_exc()

        print("\n💡 Posibles soluciones:")
        print("  • Verifica que el archivo Dataset_Unificado.xlsx exista")
        print("  • Asegúrate de tener instalado: pip install fpdf2 pandas")
        print("  • Revisa que los módulos de utils/ estén disponibles")
        print("\n" + "="*70 + "\n")

        sys.exit(1)
