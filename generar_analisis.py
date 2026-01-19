"""
Script para pre-generar analisis con IA y guardarlo en un archivo JSON.
Ejecutar localmente: python generar_analisis.py

Los analisis se guardan en Data/analisis_cache.json y se cargan
automaticamente en la aplicacion sin necesidad de llamar a la API.
"""

import os
import json
import time
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configurar API de Gemini (nuevo paquete google.genai)
from google import genai

api_key = os.environ.get("GOOGLE_API_KEY")
if not api_key:
    print("ERROR: No se encontro GOOGLE_API_KEY en las variables de entorno")
    print("Crea un archivo .env con: GOOGLE_API_KEY=tu_api_key")
    exit(1)

# Crear cliente de Gemini
client = genai.Client(api_key=api_key)

# Listar modelos disponibles y elegir uno
print("Buscando modelos disponibles...")
modelos_preferidos = ['gemini-2.0-flash-lite', 'gemini-1.5-flash-8b', 'gemini-1.5-flash', 'gemini-2.0-flash']
modelo_nombre = None

try:
    modelos_disponibles = [m.name for m in client.models.list()]
    print(f"Modelos disponibles: {len(modelos_disponibles)}")

    for m in modelos_preferidos:
        nombre_completo = f"models/{m}"
        if nombre_completo in modelos_disponibles:
            modelo_nombre = nombre_completo
            break

    if not modelo_nombre and modelos_disponibles:
        # Usar el primer modelo flash disponible
        for m in modelos_disponibles:
            if 'flash' in m.lower():
                modelo_nombre = m
                break
except Exception as e:
    print(f"Error listando modelos: {e}")
    modelo_nombre = 'models/gemini-2.0-flash-lite'

if not modelo_nombre:
    print("ERROR: No se encontro ningun modelo disponible")
    exit(1)

print(f"Usando modelo: {modelo_nombre}")

# Cargar datos
import pandas as pd

base_path = Path(__file__).parent
data_path = base_path / 'Data' / 'Dataset_Unificado.xlsx'

print(f"Cargando datos de: {data_path}")
df_base = pd.read_excel(data_path, sheet_name='Base_Indicadores', engine='openpyxl')
df_unificado = pd.read_excel(data_path, sheet_name='Unificado', engine='openpyxl')

# Limpiar nombres de columnas
df_base.columns = df_base.columns.str.strip()
df_unificado.columns = df_unificado.columns.str.strip()

print(f"Indicadores cargados: {df_unificado['Indicador'].nunique()}")

# Archivo de cache
cache_path = base_path / 'Data' / 'analisis_cache.json'

# Cargar cache existente si existe
cache = {}
if cache_path.exists():
    with open(cache_path, 'r', encoding='utf-8') as f:
        cache = json.load(f)
    print(f"Cache existente cargado: {len(cache)} analisis")


def generar_prompt_indicador(indicador, linea, objetivo, sentido, historico):
    """Genera el prompt para analizar un indicador."""
    historico_texto = "\n".join([
        f"- {item['periodo']}: Meta: {item['meta']:.2f}, Ejecucion: {item['ejecucion']:.2f}, Cumplimiento: {item['cumplimiento']:.1f}%"
        for item in historico
    ]) if historico else "No hay datos historicos"

    return f"""Eres un analista estrategico del Politecnico Grancolombiano. Analiza el siguiente indicador del PDI 2021-2025:

**Indicador:** {indicador}
**Linea Estrategica:** {linea}
**Objetivo:** {objetivo}
**Sentido:** {sentido} (el indicador se considera positivo si {'aumenta' if sentido == 'Creciente' else 'disminuye'})

**Historico de Desempeno:**
{historico_texto}

Genera un ANALISIS de maximo 100 palabras que incluya:
1. Evaluacion de la tendencia
2. Identificacion de brechas significativas
3. Una recomendacion especifica y accionable

Se conciso, profesional y enfocado en la accion. Escribe en espanol."""


def obtener_historico(df, indicador):
    """Obtiene el historico de un indicador."""
    df_ind = df[df['Indicador'] == indicador].copy()
    if df_ind.empty:
        return []

    historico = []
    for _, row in df_ind.iterrows():
        try:
            periodo = str(int(row['Año'])) if pd.notna(row.get('Año')) else ''
            if 'Semestre' in row and pd.notna(row['Semestre']) and row['Semestre'] not in ['', 0]:
                periodo = f"{int(row['Año'])}-{int(row['Semestre'])}"

            meta = float(row['Meta']) if pd.notna(row.get('Meta')) else 0
            ejecucion = float(row['Ejecución']) if pd.notna(row.get('Ejecución')) else 0
            cumplimiento = (ejecucion / meta * 100) if meta > 0 else 0

            if periodo:
                historico.append({
                    'periodo': periodo,
                    'meta': meta,
                    'ejecucion': ejecucion,
                    'cumplimiento': cumplimiento
                })
        except Exception:
            continue

    return sorted(historico, key=lambda x: x['periodo'])


def generar_analisis(prompt):
    """Genera analisis usando Gemini."""
    try:
        response = client.models.generate_content(
            model=modelo_nombre,
            contents=prompt,
            config={
                'max_output_tokens': 500,
                'temperature': 0.7
            }
        )
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"


def main():
    """Genera analisis para todos los indicadores."""
    indicadores = df_unificado['Indicador'].unique()
    total = len(indicadores)
    generados = 0
    errores = 0

    print(f"\nGenerando analisis para {total} indicadores...")
    print("="*50)

    for i, indicador in enumerate(indicadores, 1):
        # Verificar si ya existe en cache
        if indicador in cache:
            print(f"[{i}/{total}] {indicador[:50]}... (ya existe)")
            continue

        # Obtener metadatos
        df_ind = df_unificado[df_unificado['Indicador'] == indicador]
        if df_ind.empty:
            continue

        linea = df_ind['Linea'].iloc[0] if 'Linea' in df_ind.columns else 'N/D'
        objetivo = df_ind['Objetivo'].iloc[0] if 'Objetivo' in df_ind.columns else 'N/D'

        # Obtener sentido de df_base
        sentido = 'Creciente'
        if 'Indicador' in df_base.columns:
            ind_base = df_base[df_base['Indicador'] == indicador]
            if not ind_base.empty and 'Sentido' in ind_base.columns:
                sentido = str(ind_base['Sentido'].iloc[0]) if pd.notna(ind_base['Sentido'].iloc[0]) else 'Creciente'

        # Obtener historico
        historico = obtener_historico(df_unificado, indicador)

        # Generar prompt y analisis
        prompt = generar_prompt_indicador(indicador, linea, objetivo, sentido, historico)

        print(f"[{i}/{total}] Generando: {indicador[:50]}...")

        analisis = generar_analisis(prompt)

        if analisis.startswith("Error:"):
            print(f"  ERROR: {analisis}")
            errores += 1
            # Esperar si hay error de cuota
            if "429" in analisis:
                print("  Esperando 30 segundos por limite de cuota...")
                time.sleep(30)
        else:
            cache[indicador] = {
                'analisis': analisis,
                'linea': linea,
                'objetivo': objetivo,
                'sentido': sentido,
                'fecha_generacion': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            generados += 1

            # Guardar cache despues de cada analisis exitoso
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(cache, f, ensure_ascii=False, indent=2)

        # Esperar entre llamadas para evitar limite de cuota (5 seg para tier gratuito)
        time.sleep(5)

    print("="*50)
    print(f"Completado: {generados} generados, {errores} errores")
    print(f"Cache guardado en: {cache_path}")


if __name__ == "__main__":
    main()
