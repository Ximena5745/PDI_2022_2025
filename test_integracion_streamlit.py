"""
Script de Prueba - Integración con Streamlit
============================================

Verifica que la integración del PDF mejorado en Streamlit funcione correctamente.
Este script simula la ejecución sin necesidad de correr Streamlit.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from utils.data_loader import (
    cargar_datos,
    calcular_metricas_generales,
    obtener_cumplimiento_por_linea,
    obtener_cumplimiento_cascada
)
from utils.pdf_generator_mejorado import exportar_informe_pdf_mejorado
from utils.ai_analysis import (
    generar_analisis_general,
    preparar_lineas_para_analisis,
    generar_analisis_linea
)


def test_integracion():
    """Prueba la integración completa."""
    print("\n" + "="*70)
    print("  TEST DE INTEGRACIÓN - PDF MEJORADO EN STREAMLIT")
    print("="*70 + "\n")

    # 1. Cargar datos
    print("📊 1. Cargando datos del sistema...")
    try:
        df_base, df_unificado, _ = cargar_datos()
        if df_unificado is None or df_unificado.empty:
            print("❌ Error: No se pudieron cargar los datos")
            return False
        print(f"✅ Datos cargados: {len(df_unificado)} registros\n")
    except Exception as e:
        print(f"❌ Error al cargar datos: {e}")
        return False

    # 2. Calcular métricas
    print("🔢 2. Calculando métricas...")
    try:
        año_actual = 2025
        if 'Año' in df_unificado.columns:
            año_actual = int(df_unificado['Año'].max())

        metricas = calcular_metricas_generales(df_unificado, año_actual)
        df_lineas = obtener_cumplimiento_por_linea(df_unificado, año_actual)

        print(f"✅ Métricas calculadas:")
        print(f"   • Cumplimiento global: {metricas['cumplimiento_promedio']:.1f}%")
        print(f"   • Total indicadores: {metricas['total_indicadores']}")
        print(f"   • Líneas estratégicas: {len(df_lineas)}\n")
    except Exception as e:
        print(f"❌ Error al calcular métricas: {e}")
        return False

    # 3. Preparar datos para PDF
    print("📋 3. Preparando datos para PDF...")
    try:
        df_año_pdf = df_unificado[df_unificado['Año'] == año_actual] if 'Año' in df_unificado.columns else df_unificado
        if 'Fuente' in df_año_pdf.columns:
            df_año_pdf = df_año_pdf[df_año_pdf['Fuente'] == 'Avance']

        df_cascada_pdf = obtener_cumplimiento_cascada(
            df_unificado, df_base, año_actual, max_niveles=4
        )

        print(f"✅ Datos preparados:")
        print(f"   • Registros para PDF: {len(df_año_pdf)}")
        print(f"   • Niveles de cascada: {len(df_cascada_pdf)}\n")
    except Exception as e:
        print(f"❌ Error al preparar datos: {e}")
        return False

    # 4. Generar análisis IA
    print("🤖 4. Generando análisis IA...")
    try:
        lineas_data = preparar_lineas_para_analisis(df_unificado, año_actual)
        analisis_pdf = generar_analisis_general(metricas, lineas_data)

        # Análisis por línea
        analisis_lineas_pdf = {}
        for _, lr in df_lineas.iterrows():
            nom = str(lr.get('Linea', lr.get('Línea', '')))
            cumpl_l = float(lr.get('Cumplimiento', 0) or 0)
            n_ind_l = int(lr.get('Total_Indicadores', 0) or 0)

            # Objetivos de esta línea
            objs_l = []
            if df_cascada_pdf is not None and not df_cascada_pdf.empty:
                mask = (df_cascada_pdf['Nivel'] == 2) & (df_cascada_pdf['Linea'] == nom)
                for _, or_ in df_cascada_pdf[mask].iterrows():
                    objs_l.append({
                        'objetivo': str(or_.get('Objetivo', '')),
                        'cumplimiento': float(or_.get('Cumplimiento', 0) or 0),
                        'indicadores': int(or_.get('Total_Indicadores', 0) or 0),
                    })

            texto_l = generar_analisis_linea(nom, n_ind_l, cumpl_l, objs_l)
            analisis_lineas_pdf[nom] = texto_l

        print(f"✅ Análisis generado:")
        print(f"   • Análisis general: {len(analisis_pdf)} caracteres")
        print(f"   • Análisis por línea: {len(analisis_lineas_pdf)} líneas\n")
    except Exception as e:
        print(f"⚠️ Error al generar análisis IA (continuando sin análisis): {e}\n")
        analisis_pdf = "Análisis no disponible en esta ejecución de prueba."
        analisis_lineas_pdf = {}

    # 5. Generar PDF mejorado
    print("📄 5. Generando PDF mejorado...")
    try:
        from datetime import datetime

        pdf_bytes = exportar_informe_pdf_mejorado(
            metricas=metricas,
            df_lineas=df_lineas,
            df_indicadores=df_año_pdf,
            analisis_texto=analisis_pdf,
            año=año_actual,
            df_cascada=df_cascada_pdf,
            analisis_lineas=analisis_lineas_pdf
        )

        # Guardar archivo de prueba
        nombre_archivo = f"TEST_Informe_Streamlit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        with open(nombre_archivo, 'wb') as f:
            f.write(pdf_bytes)

        tamaño_kb = len(pdf_bytes) / 1024

        print(f"✅ PDF generado exitosamente:")
        print(f"   • Tamaño: {tamaño_kb:.1f} KB")
        print(f"   • Archivo: {nombre_archivo}\n")
    except Exception as e:
        print(f"❌ Error al generar PDF: {e}")
        import traceback
        traceback.print_exc()
        return False

    # 6. Resumen
    print("="*70)
    print("  ✅ INTEGRACIÓN EXITOSA")
    print("="*70)
    print(f"""
🎉 La integración del PDF mejorado funciona correctamente!

📊 Datos procesados:
  • Año: {año_actual}
  • Cumplimiento global: {metricas['cumplimiento_promedio']:.1f}%
  • Total indicadores: {metricas['total_indicadores']}
  • Líneas estratégicas: {len(df_lineas)}

📄 PDF generado:
  • Archivo: {nombre_archivo}
  • Tamaño: {tamaño_kb:.1f} KB
  • Páginas: Portada + Resumen + {len(df_lineas)} líneas + Tablas + Conclusiones

🚀 Próximos pasos:
  1. Revisa el PDF generado: {nombre_archivo}
  2. Ejecuta tu app Streamlit: streamlit run app.py
  3. Ve al tab "Datos y Exportación"
  4. Selecciona "PDF Mejorado" y descarga
  5. Compara ambas versiones (Clásico vs Mejorado)

💡 Nota: Si encuentras algún error, ejecuta:
    python validar_sistema_pdf.py
""")
    print("="*70 + "\n")

    return True


if __name__ == '__main__':
    import sys
    exito = test_integracion()
    sys.exit(0 if exito else 1)
