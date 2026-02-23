# 🚀 Quick Start - Generador de PDF Mejorado

## Archivos Creados

```
📁 PDI_2022_2025/
├── 📄 utils/
│   └── pdf_generator_mejorado.py          # ⭐ Generador principal mejorado
│
├── 📄 generar_pdf_mejorado_ejemplo.py      # Script de prueba con datos de ejemplo
├── 📄 integracion_pdf_mejorado.py          # Script de integración con datos reales
├── 📄 comparacion_pdf_original_vs_mejorado.py  # Comparación lado a lado
│
├── 📖 README_PDF_MEJORADO.md               # Documentación completa
└── 📖 QUICK_START_PDF_MEJORADO.md         # Esta guía rápida
```

---

## ⚡ Inicio Rápido (3 pasos)

### 1️⃣ Instalar dependencias
```bash
pip install fpdf2 pandas
```

### 2️⃣ Probar con datos de ejemplo
```bash
python generar_pdf_mejorado_ejemplo.py
```

✅ Esto generará: `Informe_Estrategico_POLI_[fecha].pdf`

### 3️⃣ Ver la comparación
```bash
python comparacion_pdf_original_vs_mejorado.py
```

✅ Esto generará dos PDFs para comparar lado a lado

---

## 📊 Uso con Datos Reales

### Opción A: Script de integración
```bash
python integracion_pdf_mejorado.py
```

### Opción B: Desde Python
```python
from integracion_pdf_mejorado import generar_pdf_mejorado_con_datos_reales

# Generar PDF
pdf_bytes = generar_pdf_mejorado_con_datos_reales(año=2025)

# Guardar
with open('Informe_2025.pdf', 'wb') as f:
    f.write(pdf_bytes)
```

---

## 🎨 Características Principales

| Característica | Descripción |
|----------------|-------------|
| ✅ **Tarjetas Visuales** | KPIs con colores y sombras redondeadas |
| ✅ **Barras de Progreso** | Visualización del % de cumplimiento |
| ✅ **Heatmap** | Tabla de calor por línea estratégica |
| ✅ **Colores por Línea** | Cada línea con su color distintivo |
| ✅ **Análisis IA** | Bloques de análisis por línea |
| ✅ **Tabla Mejorada** | Agrupada, ordenada, con mini-barras |
| ✅ **Glosario** | Siglas del PDI explicadas |
| ✅ **Conclusiones** | Top 3 logros + 2 aspectos críticos |

---

## 🔗 Integración con Streamlit

Agrega este código en tu app Streamlit:

```python
import streamlit as st
from integracion_pdf_mejorado import generar_pdf_mejorado_con_datos_reales

if st.button("✨ Descargar PDF Mejorado"):
    pdf_bytes = generar_pdf_mejorado_con_datos_reales(año=2025)

    st.download_button(
        label="⬇️ Descargar Informe",
        data=pdf_bytes,
        file_name="Informe_POLI_2025.pdf",
        mime="application/pdf"
    )
```

---

## 🎨 Personalización

### Cambiar colores institucionales

Edita en `pdf_generator_mejorado.py`:

```python
COLORES_INSTITUCIONALES = {
    'primary': '#0a2240',    # Tu color aquí
    'accent': '#1e88e5',     # Tu color aquí
    # ...
}
```

### Cambiar colores por línea

```python
COLORES_LINEAS = {
    "Expansión": "#FBAF17",
    "Tu Línea": "#ABCDEF",  # Tu color aquí
    # ...
}
```

### Agregar siglas al glosario

```python
GLOSARIO_SIGLAS = {
    'TU_SIGLA': 'Significado completo',
    # ...
}
```

---

## 🐛 Problemas Comunes

| Problema | Solución |
|----------|----------|
| `No module named 'fpdf'` | `pip install fpdf2` |
| `No such file 'Portada.png'` | El generador usa una portada de respaldo |
| Caracteres especiales raros | Verifica que tus datos estén en UTF-8 |
| PDF sin colores | Actualiza fpdf2: `pip install --upgrade fpdf2` |

---

## 📞 Siguiente Paso

1. ✅ Ejecuta `python generar_pdf_mejorado_ejemplo.py`
2. ✅ Revisa el PDF generado
3. ✅ Ejecuta `python comparacion_pdf_original_vs_mejorado.py`
4. ✅ Compara ambas versiones
5. ✅ Ejecuta `python integracion_pdf_mejorado.py` con tus datos reales
6. ✅ Integra en tu app Streamlit

---

## 📖 Documentación Completa

Lee [README_PDF_MEJORADO.md](README_PDF_MEJORADO.md) para:
- Estructura detallada de datos
- Ejemplos avanzados de uso
- Solución de problemas
- Especificaciones técnicas

---

## ✨ Resultado Final

Tu PDF mejorado incluirá:

```
┌─────────────────────────────┐
│ 📄 Portada Institucional   │  Mantiene original
├─────────────────────────────┤
│ 📊 Resumen Ejecutivo       │  Tarjetas + Heatmap
├─────────────────────────────┤
│ 📈 Transformación Org.     │  Color #42F2F2
│ 📈 Expansión               │  Color #FBAF17
│ 📈 Educación p/ Vida       │  Color #0F385A
│ 📈 Experiencia             │  Color #1FB2DE
│ 📈 Calidad                 │  Color #EC0677
│ 📈 Sostenibilidad          │  Color #A6CE38
├─────────────────────────────┤
│ 📋 Tabla de Indicadores    │  Agrupada y mejorada
├─────────────────────────────┤
│ 📝 Conclusiones + Glosario │  Top logros + Siglas
└─────────────────────────────┘
```

---

**Generado con ❤️ para el Politécnico Grancolombiano**

Versión 2.0 - Febrero 2026
