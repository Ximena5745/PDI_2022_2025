# Generador de PDF Mejorado - Informe Estratégico POLI

## 📋 Descripción

Generador mejorado de reportes PDF profesionales para el Plan de Desarrollo Institucional (PDI) del Politécnico Grancolombiano, con visualizaciones avanzadas, barras de progreso, tarjetas redondeadas, heatmaps y análisis IA por línea estratégica.

## ✨ Mejoras Implementadas

### 1. **Resumen Ejecutivo Visual**
- ✅ Tarjetas (cards) con fondos de color por KPI
- ✅ Barra de progreso visual para el cumplimiento global (104%)
- ✅ Heatmap / tabla de calor con todas las líneas coloreadas
- ✅ Íconos Unicode: ✓ (cumplido), ⚠ (progreso), ✗ (atención)
- ✅ Gradiente de colores según nivel de cumplimiento

### 2. **Páginas por Línea Estratégica**
- ✅ Cada línea tiene su página dedicada con color distintivo:
  - **Expansión**: `#FBAF17` (Naranja)
  - **Transformación Organizacional**: `#42F2F2` (Cian)
  - **Calidad**: `#EC0677` (Magenta)
  - **Experiencia**: `#1FB2DE` (Azul cielo)
  - **Sostenibilidad**: `#A6CE38` (Verde lima)
  - **Educación para toda la vida**: `#0F385A` (Azul oscuro)
- ✅ Barra de progreso horizontal grande mostrando % de cumplimiento
- ✅ Barras de progreso individuales por cada indicador
- ✅ Bloque de "Análisis IA" por línea con texto interpretativo

### 3. **Tabla de Detalle de Indicadores Mejorada**
- ✅ Agrupación por línea estratégica (NO mezclados)
- ✅ Separación de KPIs cuantitativos vs. hitos de proyecto (100%/0%)
- ✅ Sección separada para indicadores N/D (sin meta definida)
- ✅ Ordenamiento: primero Atención, luego En Progreso, finalmente Cumplidos
- ✅ Mini barras de progreso en cada fila

### 4. **Lenguaje y Redacción**
- ✅ Corrección de tildes en títulos y textos (á, é, í, ó, ú, ñ)
- ✅ Nombres estandarizados de líneas (sin guiones bajos, con mayúsculas)
- ✅ Glosario de siglas al final:
  - PDI, KPI, B2B, B2G, SSI, NPS, EBITDA, ANS, IA
- ✅ Página de conclusiones ejecutivas con:
  - 3 mejores logros del período
  - 2 aspectos críticos para el próximo ciclo

### 5. **Diseño Visual**
- ✅ Paleta de colores institucional POLI
- ✅ Tarjetas con sombras y bordes redondeados
- ✅ Barras de progreso con colores semáforo
- ✅ Iconografía Unicode profesional
- ✅ Tipografía Helvetica (estándar PDF)

## 🎨 Paleta de Colores

```python
COLORES_INSTITUCIONALES = {
    'primary': '#0a2240',       # Azul marino POLI
    'accent': '#1e88e5',        # Azul claro
    'cumple': '#2e7d32',        # Verde (≥100%)
    'en_progreso': '#f57f17',   # Ámbar (80-99%)
    'atencion': '#c62828',      # Rojo (<80%)
    'fondo_tarjetas': '#f5f7fa',
}
```

## 🚀 Instalación

### Requisitos

```bash
pip install fpdf2 pandas
```

### Estructura de Archivos

```
PDI_2022_2025/
├── utils/
│   ├── pdf_generator_mejorado.py   # Generador mejorado
│   └── pdf_generator.py            # Generador original (mantener)
├── generar_pdf_mejorado_ejemplo.py # Script de ejemplo
├── Portada.png                     # Imagen de portada (mantener)
└── README_PDF_MEJORADO.md         # Esta documentación
```

## 📖 Uso

### Opción 1: Ejecutar Ejemplo con Datos de Prueba

```bash
python generar_pdf_mejorado_ejemplo.py
```

Esto generará un PDF de ejemplo: `Informe_Estrategico_POLI_YYYYMMDD_HHMMSS.pdf`

### Opción 2: Integración con Datos Reales

```python
from utils.pdf_generator_mejorado import exportar_informe_pdf_mejorado
from utils.data_loader import (
    cargar_datos,
    calcular_metricas_generales,
    obtener_cumplimiento_por_linea,
    obtener_cumplimiento_cascada
)

# Cargar datos reales
df_base, df_unificado, _ = cargar_datos()

# Calcular métricas
año_actual = 2025
metricas = calcular_metricas_generales(df_unificado, año=año_actual)
df_lineas = obtener_cumplimiento_por_linea(df_unificado, año=año_actual)
df_cascada = obtener_cumplimiento_cascada(
    df_unificado, df_base, año=año_actual, max_niveles=4
)

# Filtrar indicadores
df_indicadores = df_unificado[
    (df_unificado['Año'] == año_actual) &
    (df_unificado['Fuente'] == 'Avance') &
    (df_unificado['Proyectos'] == 0)
]

# Análisis IA (opcional - integrar con tu módulo de IA)
analisis_texto = "Texto de análisis ejecutivo general..."
analisis_lineas = {
    'Expansión': 'Análisis de la línea Expansión...',
    'Calidad': 'Análisis de la línea Calidad...',
    # ... otros análisis
}

# Generar PDF
pdf_bytes = exportar_informe_pdf_mejorado(
    metricas=metricas,
    df_lineas=df_lineas,
    df_indicadores=df_indicadores,
    analisis_texto=analisis_texto,
    año=año_actual,
    df_cascada=df_cascada,
    analisis_lineas=analisis_lineas
)

# Guardar
with open('Informe_Estrategico_POLI_2025.pdf', 'wb') as f:
    f.write(pdf_bytes)
```

### Opción 3: Integración con Streamlit

```python
import streamlit as st
from utils.pdf_generator_mejorado import exportar_informe_pdf_mejorado

# En tu app de Streamlit
if st.button("Descargar Informe Mejorado PDF"):
    pdf_bytes = exportar_informe_pdf_mejorado(
        metricas=metricas,
        df_lineas=df_lineas,
        df_indicadores=df_indicadores,
        analisis_texto=analisis_ai,
        año=año_seleccionado,
        df_cascada=df_cascada,
        analisis_lineas=analisis_por_linea
    )

    st.download_button(
        label="📥 Descargar Informe PDF Mejorado",
        data=pdf_bytes,
        file_name=f"Informe_Estrategico_POLI_{año_seleccionado}.pdf",
        mime="application/pdf"
    )
```

## 📊 Estructura de Datos Requerida

### `metricas` (dict)
```python
{
    'cumplimiento_promedio': 104.0,  # float
    'total_indicadores': 34,         # int
    'indicadores_cumplidos': 27,     # int
    'en_progreso': 7,                # int
    'no_cumplidos': 0,               # int
    'año_actual': 2025               # int
}
```

### `df_lineas` (DataFrame)
```python
   Linea                          Cumplimiento  Total_Indicadores
0  Transformación Organizacional  109.4         5
1  Expansión                      106.7         10
```

### `df_indicadores` (DataFrame)
```python
   Linea      Indicador                    Meta    Ejecución  Cumplimiento
0  Expansión  Estudiantes matriculados B2B  15000   16200     108.0
1  Calidad    Tasa de graduación oportuna   70      68        97.1
```

### `df_cascada` (DataFrame)
```python
   Nivel  Linea      Objetivo  Meta_PDI  Indicador  Cumplimiento
0  1      Expansión  -         -         -          106.7
1  2      Expansión  Obj1      -         -          107.0
2  3      Expansión  Obj1      Meta1.1   -          108.0
3  4      Expansión  Obj1      Meta1.1   Ind1       108.0
```

### `analisis_lineas` (dict, opcional)
```python
{
    'Expansión': 'La línea de Expansión alcanzó...',
    'Calidad': 'Con un 103.3% de cumplimiento...',
    # ... otros análisis por línea
}
```

## 🔧 Personalización

### Modificar Colores

Edita el diccionario `COLORES_INSTITUCIONALES` en `pdf_generator_mejorado.py`:

```python
COLORES_INSTITUCIONALES = {
    'primary': '#TU_COLOR_AQUI',
    'accent': '#TU_COLOR_AQUI',
    # ...
}
```

### Modificar Colores por Línea

Edita `COLORES_LINEAS`:

```python
COLORES_LINEAS = {
    "Expansión": "#FBAF17",
    "Tu Nueva Línea": "#ABCDEF",
    # ...
}
```

### Agregar Nuevas Siglas al Glosario

```python
GLOSARIO_SIGLAS = {
    'TU_SIGLA': 'Significado completo',
    # ...
}
```

## 📄 Diferencias con el Generador Original

| Característica                  | Original      | Mejorado       |
|---------------------------------|---------------|----------------|
| Portada                         | ✅ Imagen PNG | ✅ Mantenida   |
| Resumen con tarjetas            | ❌            | ✅             |
| Barras de progreso              | ❌            | ✅             |
| Heatmap de líneas               | ❌            | ✅             |
| Colores por línea               | Parcial       | ✅ Completo    |
| Análisis IA por línea           | ❌            | ✅             |
| Tabla agrupada por línea        | ❌            | ✅             |
| Ordenamiento por estado         | ❌            | ✅             |
| Glosario de siglas              | ❌            | ✅             |
| Página de conclusiones          | ❌            | ✅             |
| Corrección de tildes            | Parcial       | ✅ Completo    |
| Íconos Unicode                  | ❌            | ✅             |

## 🐛 Solución de Problemas

### Error: "No module named 'fpdf'"
```bash
pip install fpdf2
```

### Error: "No such file or directory: 'Portada.png'"
- Verifica que el archivo `Portada.png` exista en la raíz del proyecto
- El generador funcionará con una portada de respaldo si no encuentra la imagen

### PDF generado pero sin colores
- Verifica que estés usando `fpdf2` versión 2.5 o superior
- Actualiza: `pip install --upgrade fpdf2`

### Caracteres especiales no se muestran correctamente
- La función `limpiar_texto_pdf()` mantiene tildes pero elimina emojis problemáticos
- Si tienes problemas, verifica la codificación de tus datos de entrada (UTF-8)

## 📝 Notas Técnicas

- **Librería usada**: `fpdf2` (NO `fpdf` antigua ni `reportlab`)
- **Compatibilidad**: Funciona con fpdf2 >= 2.5
- **Tamaño típico del PDF**: 200-500 KB (dependiendo del número de indicadores)
- **Páginas generadas**: ~10-15 páginas (portada + 6 líneas + tablas + conclusiones)
- **Tiempo de generación**: < 3 segundos en hardware moderno

## 🤝 Integración con el Sistema Existente

Para usar el generador mejorado sin romper el existente:

1. **Mantener ambos generadores**:
   - `pdf_generator.py` → Original (para compatibilidad)
   - `pdf_generator_mejorado.py` → Nuevo (con mejoras)

2. **Botón adicional en Streamlit**:
   ```python
   col1, col2 = st.columns(2)
   with col1:
       # Botón del PDF original
       if st.button("Descargar PDF Original"):
           pdf = generar_pdf_fpdf(...)  # Función original
           st.download_button(...)

   with col2:
       # Botón del PDF mejorado
       if st.button("Descargar PDF Mejorado"):
           pdf = exportar_informe_pdf_mejorado(...)  # Nueva función
           st.download_button(...)
   ```

3. **Migración gradual**: Probar primero el mejorado en paralelo, luego reemplazar

## 📞 Contacto y Soporte

- **Proyecto**: Dashboard Estratégico POLI
- **Institución**: Politécnico Grancolombiano
- **Versión**: 2.0 (Mejorada)
- **Fecha**: Febrero 2026

## 📜 Licencia

Este código es propiedad del Politécnico Grancolombiano y está destinado exclusivamente
para uso interno en el sistema de monitoreo del Plan de Desarrollo Institucional.

---

**Generado con ❤️ para el Politécnico Grancolombiano**
