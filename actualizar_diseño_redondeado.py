"""
Script para actualizar el diseño del PDF con elementos más redondeados y sombras
==================================================================================
"""

import re

# Leer el archivo actual
with open('utils/pdf_generator_mejorado.py', 'r', encoding='utf-8') as f:
    contenido = f.read()

# ============================================================================
# CAMBIOS A REALIZAR
# ============================================================================

# 1. Aumentar el radio de redondeo en TODAS las tarjetas (de 3-4 a 6-8)
contenido = contenido.replace(', 3, \'F\')', ', 8, \'F\')')  # Tarjetas rellenas
contenido = contenido.replace(', 4, \'F\')', ', 8, \'F\')')  # Tarjetas rellenas
contenido = contenido.replace(', 3, \'D\')', ', 6, \'D\')')  # Bordes
contenido = contenido.replace(', 4, \'D\')', ', 6, \'D\')')  # Bordes

# 2. Aumentar offset de sombras (de 2 a 3)
contenido = contenido.replace('+ 2, card_y + 2', '+ 3, card_y + 3')
contenido = contenido.replace('+2, cy+2', '+3, cy+3')
contenido = contenido.replace('+1, cy + 1', '+2, cy + 2')
contenido = contenido.replace('+2, Y_', '+3, Y_')
contenido = contenido.replace('+2, y_a + 2', '+3, y_a + 3')
contenido = contenido.replace('+2, analisis_y+2', '+3, analisis_y+3')

# 3. Hacer sombras más oscuras (de 200,200,200 a 180,180,180)
contenido = contenido.replace('(200, 200, 200)', '(180, 180, 180)')
contenido = contenido.replace('(220, 220, 220)', '(190, 190, 190)')

# 4. Aumentar radio de barras de progreso (más pill-shaped)
contenido = re.sub(r'rounded_rect\(x, y, w, h, h/2', 'rounded_rect(x, y, w, h, h/1.5', contenido)
contenido = re.sub(r'rounded_rect\(x, y, progreso_w, h, h/2', 'rounded_rect(x, y, progreso_w, h, h/1.5', contenido)

# 5. Redondear mini barras de progreso
contenido = re.sub(r'rounded_rect\(([^,]+), ([^,]+), ([^,]+), 3, 1\.5', r'rounded_rect(\1, \2, \3, 3, 2', contenido)

print("✅ Cambios aplicados:")
print("  • Radio de redondeo aumentado de 3-4px a 6-8px")
print("  • Sombras más marcadas (offset de 2px a 3px)")
print("  • Sombras más oscuras (RGB 200 a 180)")
print("  • Barras de progreso más redondeadas")

# Guardar archivo actualizado
with open('utils/pdf_generator_mejorado.py', 'w', encoding='utf-8') as f:
    f.write(contenido)

print("\n✅ Archivo actualizado exitosamente!")
print("\n📄 Prueba el nuevo diseño ejecutando:")
print("   python generar_pdf_mejorado_ejemplo.py")
