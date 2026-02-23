# 🚀 Guía de Integración - PDF Mejorado en Streamlit

## ✅ Integración Completada R 

La integración del generador de PDF mejorado ya está **lista y funcionando** en tu aplicación Streamlit.

---

##  Cambios Realizados

### Archivo Modificado : [`views/dashboard.py`](views/dashboard.py)

#### 1. **Importaciones actualizadas** (Línea 29)
```python
# Antes:
from utils.pdf_generator import exportar_informe_pdf, previsualizar_html

# Ahora:
from utils.pdf_generator import exportar_informe_pdf as exportar_informe_pdf_original, previsualizar_html
from utils.pdf_generator_mejorado import exportar_informe_pdf_mejorado
```

#### 2. **Nueva interfaz de usuario** (Líneas 276-365)
- ✅ Selector de versión de PDF (Mejorado vs Clásico)
- ✅ Dos botones de descarga según la selección
- ✅ Información visual de características
- ✅ Mensajes de estado mejorados

---

## 🎯 Cómo Usar en Streamlit

### Paso 1: Iniciar la Aplicación
```bash
streamlit run app.py
```

### Paso 2: Navegar al Dashboard
1. La app se abrirá en tu navegador
2. Selecciona "📊 Dashboard General" (si no está ya seleccionado)

### Paso 3: Ir a la Pestaña de Exportación
1. Haz clic en la pestaña **"📥 Datos y Exportación"**
2. Verás la sección de "📄 Informe PDF Corporativo"

### Paso 4: Seleccionar Versión de PDF
Elige entre dos opciones:

#### Opción A: **✨ PDF Mejorado (Recomendado)**
```
[●] ✨ PDF Mejorado (Recomendado)
[ ] 📄 PDF Clásico
```

**Características del PDF Mejorado:**
- ✨ Tarjetas visuales con colores
- ✨ Barras de progreso animadas
- ✨ Heatmap de líneas estratégicas
- ✨ Análisis IA destacado por línea
- ✨ Tabla agrupada y mejorada
- ✨ Glosario de siglas del PDI
- ✨ Conclusiones ejecutivas (Top 3 logros + 2 críticos)

#### Opción B: **📄 PDF Clásico**
```
[ ] ✨ PDF Mejorado (Recomendado)
[●] 📄 PDF Clásico
```

**Características del PDF Clásico:**
- Portada corporativa
- KPIs principales
- Análisis por línea
- Detalle de indicadores
- Análisis ejecutivo IA

### Paso 5: Descargar el PDF
1. Haz clic en el botón correspondiente:
   - **"✨ Descargar PDF Mejorado"** (botón azul)
   - **"📄 Descargar PDF Clásico"** (botón gris)

2. El navegador descargará el archivo:
   - Mejorado: `Informe_Estrategico_POLI_Mejorado_2025_YYYYMMDD.pdf`
   - Clásico: `Informe_Estrategico_POLI_2025_YYYYMMDD.pdf`

3. Verás un mensaje de éxito con el tamaño del archivo:
   ```
   ✅ PDF generado exitosamente (XXX KB)
   ```

---

## 🧪 Probar la Integración (Sin Streamlit)

Si quieres verificar que todo funciona antes de usar Streamlit:

```bash
python test_integracion_streamlit.py
```

Esto generará un PDF de prueba sin necesidad de ejecutar Streamlit.

---

## 📊 Comparación Visual

### Interfaz Anterior
```
┌─────────────────────────────────┐
│ [📄 Descargar PDF Corporativo] │
└─────────────────────────────────┘
```

### Interfaz Nueva
```
┌──────────────────────────────────────────────────┐
│ Selecciona la versión del PDF:                  │
│                                                  │
│ (●) ✨ PDF Mejorado (Recomendado)               │
│ ( ) 📄 PDF Clásico                              │
│                                                  │
│ [✨ Descargar PDF Mejorado]                     │
│                                                  │
│ ✅ PDF generado exitosamente (XXX KB)           │
└──────────────────────────────────────────────────┘
```

---

## 🎨 Personalización Adicional

### Cambiar el Orden de las Opciones

Si quieres que el PDF Clásico sea el predeterminado, edita en [`views/dashboard.py`](views/dashboard.py) línea ~290:

```python
# Antes (Mejorado por defecto):
version_pdf = st.radio(
    "Selecciona la versión del PDF:",
    ["✨ PDF Mejorado (Recomendado)", "📄 PDF Clásico"],
    horizontal=True
)

# Después (Clásico por defecto):
version_pdf = st.radio(
    "Selecciona la versión del PDF:",
    ["📄 PDF Clásico", "✨ PDF Mejorado"],
    horizontal=True
)
```

### Ocultar el Selector (Solo PDF Mejorado)

Si quieres usar **solo** el PDF mejorado sin mostrar opciones:

1. Comenta/elimina el selector (líneas ~289-303)
2. Fuerza el uso del mejorado:

```python
# Forzar siempre PDF mejorado
version_pdf = "✨ PDF Mejorado (Recomendado)"
```

### Cambiar Colores/Textos del PDF

Edita [`utils/pdf_generator_mejorado.py`](utils/pdf_generator_mejorado.py):

```python
# Líneas 26-37: Colores institucionales
COLORES_INSTITUCIONALES = {
    'primary': '#TU_COLOR',  # Cambia aquí
    # ...
}

# Líneas 40-47: Colores por línea
COLORES_LINEAS = {
    "Tu Línea": "#TU_COLOR",  # Agrega/modifica aquí
    # ...
}

# Líneas 50-60: Glosario de siglas
GLOSARIO_SIGLAS = {
    'TU_SIGLA': 'Significado',  # Agrega aquí
    # ...
}
```

---

## 🐛 Solución de Problemas

### Error: "No module named 'pdf_generator_mejorado'"
**Solución:**
```bash
# Verifica que el archivo existe
ls utils/pdf_generator_mejorado.py

# Si no existe, regenera el archivo:
python generar_pdf_mejorado_ejemplo.py
```

### Error: "No se pudieron cargar los datos"
**Solución:**
```bash
# Verifica que el archivo Excel existe y no está abierto
ls Data/Dataset_Unificado.xlsx

# Cierra el Excel si está abierto
# Ejecuta la validación:
python validar_sistema_pdf.py
```

### El botón no aparece en Streamlit
**Solución:**
1. Reinicia el servidor de Streamlit (Ctrl+C y `streamlit run app.py`)
2. Limpia la caché: En la app, presiona **C** → "Clear cache"
3. Recarga la página: Presiona **R**

### PDF generado pero sin colores
**Solución:**
```bash
# Actualiza fpdf2
pip install --upgrade fpdf2

# Verifica la versión (debe ser >= 2.5)
python -c "import fpdf; print(fpdf.__version__)"
```

### Error de memoria al generar PDF
**Solución:**
- El PDF mejorado es ~30-50 KB más grande que el clásico
- Si tienes muchos indicadores (>100), considera:
  1. Filtrar por año específico
  2. Generar PDFs por línea estratégica
  3. Usar el PDF clásico

---

## 📈 Estadísticas de Uso

Para ver estadísticas de uso de cada versión, puedes agregar logging:

```python
# En views/dashboard.py, después de generar el PDF:

import logging
logging.info(f"PDF generado: {version_pdf}, Tamaño: {tamaño_kb:.1f} KB")
```

---

## 🔄 Volver a la Versión Anterior

Si por alguna razón necesitas volver al generador original únicamente:

1. Edita [`views/dashboard.py`](views/dashboard.py)
2. Revierte las importaciones:
   ```python
   from utils.pdf_generator import exportar_informe_pdf, previsualizar_html
   ```
3. Usa solo `exportar_informe_pdf()` en lugar del selector

**Nota:** No es necesario eliminar el archivo `pdf_generator_mejorado.py`

---

## ✨ Características Exclusivas del PDF Mejorado

| Característica | Clásico | Mejorado |
|----------------|---------|----------|
| Portada corporativa | ✅ | ✅ |
| Tarjetas visuales KPIs | ❌ | ✅ |
| Barra de progreso global | ❌ | ✅ |
| Heatmap de líneas | ❌ | ✅ |
| Colores distintivos por línea | Parcial | ✅ Completo |
| Barras de progreso por indicador | ❌ | ✅ |
| Análisis IA destacado | ✅ Básico | ✅ Mejorado |
| Tabla agrupada por línea | ❌ | ✅ |
| Separación KPIs vs Hitos | ❌ | ✅ |
| Glosario de siglas | ❌ | ✅ |
| Top 3 logros | ❌ | ✅ |
| Aspectos críticos | ❌ | ✅ |
| Corrección de tildes | Parcial | ✅ Completo |

---

## 📞 Soporte

Si encuentras algún problema:

1. ✅ Ejecuta: `python validar_sistema_pdf.py`
2. ✅ Ejecuta: `python test_integracion_streamlit.py`
3. ✅ Revisa los logs de Streamlit en la terminal
4. ✅ Lee [`README_PDF_MEJORADO.md`](README_PDF_MEJORADO.md) para más detalles

---

## 🎉 ¡Listo para Usar!

La integración está completa y lista para producción. Disfruta de los informes PDF mejorados!

**Generado con ❤️ para el Politécnico Grancolombiano**

Versión 2.0 - Febrero 2026
