"""
Script de Validación del Sistema de Generación de PDF
=====================================================

Verifica que todos los componentes necesarios estén instalados
y configurados correctamente antes de generar los informes PDF.

Ejecutar antes de usar el generador de PDF mejorado:
    python validar_sistema_pdf.py
"""

import sys
import os
from pathlib import Path


def print_header(texto):
    """Imprime encabezado con formato."""
    print("\n" + "="*70)
    print(f"  {texto}")
    print("="*70 + "\n")


def print_ok(texto):
    """Imprime mensaje de éxito."""
    print(f"  ✅ {texto}")


def print_error(texto):
    """Imprime mensaje de error."""
    print(f"  ❌ {texto}")


def print_warning(texto):
    """Imprime mensaje de advertencia."""
    print(f"  ⚠️  {texto}")


def print_info(texto):
    """Imprime mensaje informativo."""
    print(f"  ℹ️  {texto}")


def validar_python():
    """Valida la versión de Python."""
    print_header("VALIDANDO VERSIÓN DE PYTHON")

    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"

    print_info(f"Versión de Python: {version_str}")

    if version.major >= 3 and version.minor >= 8:
        print_ok(f"Python {version_str} es compatible")
        return True
    else:
        print_error(f"Python {version_str} es muy antiguo")
        print_info("Se requiere Python 3.8 o superior")
        return False


def validar_librerias():
    """Valida que las librerías necesarias estén instaladas."""
    print_header("VALIDANDO LIBRERÍAS PYTHON")

    librerias = {
        'fpdf': 'fpdf2',
        'pandas': 'pandas',
        'openpyxl': 'openpyxl (para leer Excel)'
    }

    errores = []
    warnings = []

    for modulo, nombre in librerias.items():
        try:
            if modulo == 'fpdf':
                from fpdf import FPDF
                # Verificar que es fpdf2 (no fpdf antiguo)
                if hasattr(FPDF, 'rounded_rect'):
                    print_ok(f"{nombre} instalado correctamente")
                else:
                    print_warning(f"Tienes 'fpdf' antiguo instalado, se necesita 'fpdf2'")
                    warnings.append(('fpdf2', 'pip install fpdf2'))
            elif modulo == 'pandas':
                import pandas as pd
                version = pd.__version__
                print_ok(f"{nombre} v{version} instalado")
            elif modulo == 'openpyxl':
                import openpyxl
                version = openpyxl.__version__
                print_ok(f"{nombre} v{version} instalado")

        except ImportError:
            print_error(f"{nombre} NO instalado")
            if modulo == 'fpdf':
                errores.append(('fpdf2', 'pip install fpdf2'))
            elif modulo == 'pandas':
                errores.append(('pandas', 'pip install pandas'))
            elif modulo == 'openpyxl':
                errores.append(('openpyxl', 'pip install openpyxl'))

    return errores, warnings


def validar_archivos():
    """Valida que los archivos necesarios existan."""
    print_header("VALIDANDO ARCHIVOS DEL PROYECTO")

    base_path = Path(__file__).parent

    archivos_necesarios = {
        'utils/pdf_generator_mejorado.py': 'Generador PDF mejorado',
        'utils/data_loader.py': 'Cargador de datos',
        'Data/Dataset_Unificado.xlsx': 'Dataset de datos',
    }

    archivos_opcionales = {
        'Portada.png': 'Imagen de portada (usa respaldo si no existe)',
        'utils/ai_analysis.py': 'Módulo de análisis IA (opcional)',
    }

    errores = []
    warnings = []

    # Archivos necesarios
    for archivo, descripcion in archivos_necesarios.items():
        ruta = base_path / archivo
        if ruta.exists():
            print_ok(f"{descripcion}: {archivo}")
        else:
            print_error(f"{descripcion}: {archivo} NO ENCONTRADO")
            errores.append(archivo)

    # Archivos opcionales
    for archivo, descripcion in archivos_opcionales.items():
        ruta = base_path / archivo
        if ruta.exists():
            print_ok(f"{descripcion}: {archivo}")
        else:
            print_warning(f"{descripcion}: {archivo} (opcional)")
            warnings.append(archivo)

    return errores, warnings


def validar_permisos():
    """Valida permisos de escritura."""
    print_header("VALIDANDO PERMISOS")

    base_path = Path(__file__).parent

    # Intentar crear archivo de prueba
    test_file = base_path / 'test_permisos.tmp'

    try:
        with open(test_file, 'w') as f:
            f.write('test')
        test_file.unlink()  # Eliminar archivo de prueba
        print_ok("Permisos de escritura en directorio actual")
        return True
    except Exception as e:
        print_error(f"No hay permisos de escritura: {e}")
        return False


def validar_datos():
    """Valida que se puedan cargar los datos."""
    print_header("VALIDANDO CARGA DE DATOS")

    try:
        from utils.data_loader import cargar_datos

        df_base, df_unificado, _ = cargar_datos()

        if df_unificado is None or df_unificado.empty:
            print_error("No se pudieron cargar los datos")
            return False

        print_ok(f"Datos cargados: {len(df_unificado)} registros")

        # Validar columnas necesarias
        columnas_necesarias = ['Año', 'Linea', 'Indicador', 'Cumplimiento']
        columnas_faltantes = [col for col in columnas_necesarias if col not in df_unificado.columns]

        if columnas_faltantes:
            print_error(f"Columnas faltantes: {', '.join(columnas_faltantes)}")
            return False

        print_ok("Todas las columnas necesarias están presentes")

        # Validar años disponibles
        años = sorted(df_unificado['Año'].unique())
        print_info(f"Años disponibles: {', '.join(map(str, años))}")

        return True

    except Exception as e:
        print_error(f"Error al cargar datos: {e}")
        return False


def generar_reporte_validacion():
    """Genera reporte completo de validación."""
    print("\n" + "="*70)
    print(" " * 15 + "VALIDACIÓN DEL SISTEMA DE GENERACIÓN DE PDF")
    print("="*70)

    resultados = {
        'python': False,
        'librerias': False,
        'archivos': False,
        'permisos': False,
        'datos': False
    }

    errores_totales = []
    warnings_totales = []

    # 1. Validar Python
    resultados['python'] = validar_python()

    # 2. Validar Librerías
    errores_lib, warnings_lib = validar_librerias()
    resultados['librerias'] = len(errores_lib) == 0
    errores_totales.extend(errores_lib)
    warnings_totales.extend(warnings_lib)

    # 3. Validar Archivos
    errores_arch, warnings_arch = validar_archivos()
    resultados['archivos'] = len(errores_arch) == 0
    errores_totales.extend([('archivo', f) for f in errores_arch])

    # 4. Validar Permisos
    resultados['permisos'] = validar_permisos()

    # 5. Validar Datos
    if resultados['archivos']:
        resultados['datos'] = validar_datos()
    else:
        print_header("VALIDANDO CARGA DE DATOS")
        print_warning("Omitido (archivos faltantes)")

    # =========================================================================
    # RESUMEN FINAL
    # =========================================================================
    print_header("RESUMEN DE VALIDACIÓN")

    total_checks = len(resultados)
    checks_ok = sum(resultados.values())

    print(f"  Verificaciones completadas: {checks_ok}/{total_checks}\n")

    # Mostrar estado de cada verificación
    estados = {
        'python': 'Versión de Python',
        'librerias': 'Librerías Python',
        'archivos': 'Archivos del proyecto',
        'permisos': 'Permisos de escritura',
        'datos': 'Carga de datos'
    }

    for key, nombre in estados.items():
        if resultados[key]:
            print_ok(f"{nombre}")
        else:
            print_error(f"{nombre}")

    # Mostrar errores críticos
    if errores_totales:
        print("\n" + "-"*70)
        print("  ❌ ERRORES CRÍTICOS A CORREGIR:\n")
        for tipo, info in errores_totales:
            if tipo == 'archivo':
                print(f"     • Archivo faltante: {info}")
            else:
                print(f"     • Instalar {tipo}: {info}")

    # Mostrar advertencias
    if warnings_totales:
        print("\n" + "-"*70)
        print("  ⚠️  ADVERTENCIAS (opcionales):\n")
        for warning in warnings_totales:
            if isinstance(warning, tuple):
                print(f"     • {warning[0]}: {warning[1]}")
            else:
                print(f"     • {warning}")

    # =========================================================================
    # RESULTADO FINAL
    # =========================================================================
    print("\n" + "="*70)

    if checks_ok == total_checks:
        print("  ✅ ¡SISTEMA VALIDADO CORRECTAMENTE!")
        print("="*70 + "\n")
        print("  🚀 Estás listo para generar informes PDF mejorados\n")
        print("  Próximos pasos:")
        print("    1. python generar_pdf_mejorado_ejemplo.py")
        print("    2. python comparacion_pdf_original_vs_mejorado.py")
        print("    3. python integracion_pdf_mejorado.py")
        print("\n" + "="*70 + "\n")
        return True

    else:
        print("  ❌ SISTEMA NO VALIDADO - Corrige los errores")
        print("="*70 + "\n")

        if errores_totales:
            print("  💡 SOLUCIONES:\n")

            # Comandos de instalación
            install_commands = set()
            for tipo, cmd in errores_totales:
                if 'pip install' in cmd:
                    install_commands.add(cmd)

            if install_commands:
                print("  Ejecuta estos comandos:\n")
                for cmd in install_commands:
                    print(f"    {cmd}")

            print()

        print("  Luego ejecuta nuevamente:")
        print("    python validar_sistema_pdf.py")
        print("\n" + "="*70 + "\n")
        return False


if __name__ == '__main__':
    """Ejecutar validación completa."""
    exito = generar_reporte_validacion()
    sys.exit(0 if exito else 1)
