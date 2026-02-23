"""
Script para actualizar el generador de PDF a diseño 3D moderno
===============================================================
Este script aplica las mejoras solicitadas:
1. Elimina páginas en blanco
2. Agrega gráficos circulares donut
3. Mejora fondos con gradientes
4. Agrega análisis por línea
5. Crea tabla de contenidos con enlaces
"""

import re

print("=" * 70)
print(" ACTUALIZACIÓN A DISEÑO 3D MODERNO - PDF GENERADOR")
print("=" * 70)

# Leer archivo actual
print("\n📄 Leyendo archivo actual...")
with open('utils/pdf_generator_mejorado.py', 'r', encoding='utf-8') as f:
    contenido = f.read()

cambios_aplicados = []

# 1. Agregar imports necesarios para enlaces
print("\n🔧 Agregando capacidades de enlaces internos...")
if 'from math import pi, sin, cos' not in contenido:
    imports_linea = contenido.find('from fpdf import FPDF')
    contenido = contenido[:imports_linea] + 'from math import pi, sin, cos\n' + contenido[imports_linea:]
    cambios_aplicados.append("✓ Imports matemáticos para gráficos circulares")

# 2. Agregar función para gráficos circulares/donut
print("🔧 Agregando función para gráficos circulares donut 3D...")
funcion_donut = '''

def dibujar_grafico_donut_3d(pdf, x, y, radio_ext, radio_int, porcentaje, color_rgb, texto_centro=""):
    """
    Dibuja un gráfico circular tipo donut con efecto 3D.
    
    Args:
        pdf: Instancia del PDF
        x, y: Centro del círculo
        radio_ext: Radio exterior del donut
        radio_int: Radio interior del donut
        porcentaje: Valor de 0 a 100+
        color_rgb: Tupla (R, G, B) del color principal
        texto_centro: Texto a mostrar en el centro
    """
    # Sombra del donut (círculo desplazado más oscuro)
    pdf.set_fill_color(180, 180, 180)
    pdf.ellipse(x + 2, y + 2, radio_ext * 2, radio_ext * 2, 'F')
    
    # Fondo gris claro (círculo completo)
    pdf.set_fill_color(230, 230, 230)
    pdf.ellipse(x, y, radio_ext * 2, radio_ext * 2, 'F')
    
    # Círculo de progreso (solo el porcentaje completado)
    # fpdf2 no soporta arcos parciales nativamente, así que dibujamos polígono aproximado
    if porcentaje > 0:
        pdf.set_fill_color(*color_rgb)
        # Aproximar arco con polígonos
        angulo_final = (porcentaje / 100) * 360
        segmentos = int(angulo_final / 5) + 1  # Un punto cada 5 grados
        
        puntos = [(x + radio_ext, y + radio_ext)]  # Centro
        for i in range(segmentos + 1):
            angulo = (i / segmentos) * angulo_final - 90  # -90 para empezar arriba
            rad = angulo * (pi / 180)
            px = x + radio_ext + radio_ext * cos(rad)
            py = y + radio_ext + radio_ext * sin(rad)
            puntos.append((px, py))
        
        # Dibujar polígono del progreso (aproximación del arco)
        # Nota: fpdf2 no tiene método polygon directo, usamos múltiples líneas
        pdf.set_line_width(radio_ext - radio_int)
        pdf.set_draw_color(*color_rgb)
        for i in range(1, len(puntos)):
            pdf.line(puntos[i-1][0], puntos[i-1][1], puntos[i][0], puntos[i][1])
    
    # Círculo interior (crea el efecto donut)
    pdf.set_fill_color(255, 255, 255)
    pdf.ellipse(x + (radio_ext - radio_int), y + (radio_ext - radio_int), 
                radio_int * 2, radio_int * 2, 'F')
    
    # Texto en el centro
    if texto_centro:
        pdf.set_xy(x, y + radio_ext - 3)
        pdf.set_font('Helvetica', 'B', 14)
        pdf.set_text_color(*color_rgb)
        pdf.cell(radio_ext * 2, 6, texto_centro, 0, 0, 'C')
'''

# Insertar función después de las funciones auxiliares existentes
pos_insertar = contenido.find('def obtener_icono_estado(')
if pos_insertar > 0 and 'def dibujar_grafico_donut_3d' not in contenido:
    contenido = contenido[:pos_insertar] + funcion_donut + '\n\n' + contenido[pos_insertar:]
    cambios_aplicados.append("✓ Función de gráficos donut 3D")

# 3. Agregar función para fondo con gradiente
print("🔧 Agregando fondo con gradiente y profundidad...")
funcion_fondo = '''

def aplicar_fondo_con_profundidad(pdf):
    """
    Aplica un fondo con gradiente y elementos decorativos para dar profundidad.
    """
    # Fondo base azul oscuro
    pdf.set_fill_color(10, 22, 40)  # #0a1628
    pdf.rect(0, 0, 210, 297, 'F')
    
    # Círculos decorativos en esquinas (efecto bokeh)
    # Esquina superior izquierda
    pdf.set_fill_color(15, 35, 60, 30)  # Semi-transparente (30% opacity simulada)
    pdf.ellipse(-20, -20, 80, 80, 'F')
    
    # Esquina inferior derecha
    pdf.set_fill_color(10, 25, 50, 25)
    pdf.ellipse(160, 240, 100, 100, 'F')
    
    # Líneas de cuadrícula tenues (efecto grid 3D)
    pdf.set_draw_color(255, 255, 255, 5)  # Blanco muy tenue
    pdf.set_line_width(0.1)
    for i in range(0, 210, 20):
        pdf.line(i, 0, i, 297)
    for i in range(0, 297, 20):
        pdf.line(0, i, 210, i)
'''

pos_insertar_fondo = contenido.find('def generar_portada(')
if pos_insertar_fondo > 0 and 'def aplicar_fondo_con_profundidad' not in contenido:
    contenido = contenido[:pos_insertar_fondo] + funcion_fondo + '\n\n' + contenido[pos_insertar_fondo:]
    cambios_aplicados.append("✓ Función de fondo con profundidad")

print("\n💾 Guardando cambios...")
with open('utils/pdf_generator_mejorado.py', 'w', encoding='utf-8') as f:
    f.write(contenido)

# Resumen
print("\n" + "=" * 70)
print(" RESUMEN DE CAMBIOS APLICADOS")
print("=" * 70)
for cambio in cambios_aplicados:
    print(f"  {cambio}")

print("\n⚠️  NOTA IMPORTANTE:")
print("  Este es el PRIMER PASO de la actualización.")
print("  Para completar el rediseño 3D completo, necesitas:")
print("  1. ✅ Funciones base agregadas (gráficos donut, fondos)")
print("  2. ⏳ Reemplazar páginas vacías con contenido")
print("  3. ⏳ Agregar análisis por línea estratégica")
print("  4. ⏳ Crear tabla de contenidos con enlaces")
print("  5. ⏳ Implementar barras 3D cilíndricas")
print("\n  Continúa con los siguientes scripts para completar el rediseño.")
print("=" * 70)
