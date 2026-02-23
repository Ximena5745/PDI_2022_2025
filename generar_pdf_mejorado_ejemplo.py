"""
Script de ejemplo para generar el PDF mejorado del informe estratégico POLI
===========================================================================

Este script demuestra cómo usar el nuevo generador de PDF mejorado
con datos de ejemplo del PDI 2021-2025.

Características incluidas:
✓ Resumen ejecutivo con tarjetas visuales
✓ Barra de progreso global del 104%
✓ Heatmap de líneas estratégicas 
✓ Páginas dedicadas por línea con colores distintivos
✓ Análisis IA por línea
✓ Tabla de indicadores mejorada y agrupada
✓ Conclusiones y glosario de siglas

Uso:
    python generar_pdf_mejorado_ejemplo.py
"""

from datetime import datetime
from utils.pdf_generator_mejorado import (
    exportar_informe_pdf_mejorado,
    generar_datos_ejemplo
)


def main():
    """Función principal para generar el PDF de ejemplo."""
    print("=" * 70)
    print("  GENERADOR DE INFORME ESTRATÉGICO POLI - VERSIÓN MEJORADA")
    print("  Plan de Desarrollo Institucional 2021-2025")
    print("=" * 70)
    print()

    print("🔄 Preparando datos de ejemplo...")

    # Generar datos de ejemplo
    (metricas, df_lineas, df_indicadores,
     analisis_texto, df_cascada, analisis_lineas) = generar_datos_ejemplo()

    print("✓ Datos cargados:")
    print(f"  • Cumplimiento global: {metricas['cumplimiento_promedio']}%")
    print(f"  • Total indicadores: {metricas['total_indicadores']}")
    print(f"  • Líneas estratégicas: {len(df_lineas)}")
    print()

    print("📄 Generando PDF mejorado...")

    # Generar PDF
    try:
        pdf_bytes = exportar_informe_pdf_mejorado(
            metricas=metricas,
            df_lineas=df_lineas,
            df_indicadores=df_indicadores,
            analisis_texto=analisis_texto,
            año=2025,
            df_cascada=df_cascada,
            analisis_lineas=analisis_lineas
        )

        # Guardar archivo
        fecha_actual = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_archivo = f'Informe_Estrategico_POLI_{fecha_actual}.pdf'

        with open(nombre_archivo, 'wb') as f:
            f.write(pdf_bytes)

        print()
        print("✅ ¡PDF generado exitosamente!")
        print()
        print("📊 Detalles del archivo:")
        print(f"  • Nombre: {nombre_archivo}")
        print(f"  • Tamaño: {len(pdf_bytes) / 1024:.1f} KB")
        print(f"  • Ubicación: {nombre_archivo}")
        print()
        print("📋 Estructura del PDF:")
        print("  1. Portada institucional")
        print("  2. Resumen ejecutivo visual")
        print("  3. Detalle por línea estratégica (6 líneas)")
        print("  4. Tabla de indicadores mejorada")
        print("  5. Conclusiones y glosario")
        print()
        print("🎯 Características incluidas:")
        print("  ✓ Tarjetas redondeadas con colores")
        print("  ✓ Barras de progreso visuales")
        print("  ✓ Heatmap de líneas estratégicas")
        print("  ✓ Íconos Unicode (✓ ⚠ ✗)")
        print("  ✓ Análisis IA por línea")
        print("  ✓ Glosario de siglas del PDI")
        print("  ✓ Conclusiones ejecutivas")
        print()
        print("=" * 70)

    except Exception as e:
        print()
        print("❌ Error al generar el PDF:")
        print(f"   {str(e)}")
        print()
        print("💡 Verifica que:")
        print("  • La librería fpdf2 esté instalada: pip install fpdf2")
        print("  • Tengas permisos de escritura en el directorio actual")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
