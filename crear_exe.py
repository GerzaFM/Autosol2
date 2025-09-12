#!/usr/bin/env python3
"""
Script automático para crear el ejecutable de Autoforms
Ejecutar: python crear_exe.py
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def ejecutar_comando(comando, descripcion):
    """Ejecuta un comando y maneja errores"""
    print(f"\n[EXEC] {descripcion}...")
    try:
        resultado = subprocess.run(comando, shell=True, check=True, 
                                 capture_output=True, text=True, encoding='utf-8')
        print(f"[OK] {descripcion} - Completado")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Error en {descripcion}:")
        print(f"   Comando: {comando}")
        print(f"   Error: {e.stderr}")
        return False

def eliminar_directorio_seguro(directorio):
    """Elimina un directorio de forma segura, manejando archivos bloqueados"""
    if not os.path.exists(directorio):
        return
    
    print(f"[CLEAN] Eliminando directorio {directorio}...")
    
    # Intentar primero con shutil.rmtree
    try:
        shutil.rmtree(directorio)
        print(f"[OK] {directorio} eliminado exitosamente")
        return
    except PermissionError:
        print(f"[WARN] Archivos bloqueados en {directorio}, intentando método alternativo...")
    
    # Método alternativo usando comandos del sistema
    try:
        if os.name == 'nt':  # Windows
            subprocess.run(['rmdir', '/s', '/q', directorio], shell=True, check=True)
        else:  # Unix/Linux
            subprocess.run(['rm', '-rf', directorio], check=True)
        print(f"[OK] {directorio} eliminado con método alternativo")
    except:
        print(f"[WARN] No se pudo eliminar {directorio} completamente, continuando...")

def crear_spec_file():
    """Crea el archivo .spec para PyInstaller"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('src', 'src')],
    hiddenimports=[
        # Dependencias principales
        'decouple', 'python_decouple',
        'ttkbootstrap', 'tkinter', 'tkinter.ttk', 'tkinter.messagebox', 'tkinter.filedialog',
        'sqlite3', 'pandas', 'openpyxl', 'xlsxwriter', 'reportlab',
        'PyPDF2', 'pdfplumber', 'PyPDFForm', 'xml.etree.ElementTree', 'requests',
        'lxml', 'lxml.etree', 'lxml.html',
        'Pillow', 'PIL', 'PIL.Image', 'PIL.ImageTk',
        'fpdf', 'fpdf2',
        'charset_normalizer',
        'urllib3',
        'certifi',
        'six',
        'packaging',
        'pyparsing',
        'python_dateutil',
        'pytz',
        'et_xmlfile',
        'defusedxml',
        'chardet',
        'idna',
        
        # Módulos del proyecto
        'app', 'app.core', 'app.core.application', 'app.core.database',
        'app.ui', 'app.utils',
        'config', 'config.app_config', 'config.development', 'config.settings',
        'models', 'models.solicitud',
        'services', 'services.validation',
        'views', 'views.components',
        
        # Módulos de solicitudapp
        'src.solicitudapp',
        'src.solicitudapp.config',
        'src.solicitudapp.config.app_config',
        'src.solicitudapp.config.database_config',
        'src.solicitudapp.config.settings',
        'src.solicitudapp.services',
        'src.solicitudapp.services.database_service',
        'src.solicitudapp.services.export_service',
        'src.solicitudapp.services.pdf_service',
        'src.solicitudapp.services.validation_service',
        'src.solicitudapp.views',
        'src.solicitudapp.views.main_view',
        'src.solicitudapp.views.export_view',
        'src.solicitudapp.views.components',
        'src.solicitudapp.views.components.table_component',
        'src.solicitudapp.views.components.filter_component',
        'src.solicitudapp.models',
        'src.solicitudapp.models.solicitud',
        'src.solicitudapp.models.database',
        'src.solicitudapp.utils',
        'src.solicitudapp.utils.helpers',
        'src.solicitudapp.utils.validators',
        
        # Otros módulos del src
        'src.buscarapp',
        'src.chequeapp',
        'src.bd'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Autoforms',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Sin consola (GUI)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
'''
    
    with open('autosol2.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    print("[OK] Archivo autosol2.spec creado")

def main():
    """Función principal que automatiza todo el proceso"""
    print("[INFO] Iniciando creación automática del ejecutable Autoforms")
    print("=" * 70)
    
    # Verificar que estamos en el directorio correcto
    if not os.path.exists('main.py'):
        print("[ERROR] No se encontró main.py. Ejecuta este script desde el directorio del proyecto.")
        sys.exit(1)
    
    # Verificar entorno virtual
    venv_python = Path('.venv/Scripts/python.exe')
    if venv_python.exists():
        python_cmd = str(venv_python)
        print("[OK] Usando entorno virtual: .venv")
    else:
        python_cmd = 'python'
        print("[WARN] Usando Python del sistema (recomendado usar entorno virtual)")
    
    # Paso 1: Verificar PyInstaller
    print(f"\n[CHECK] Verificando PyInstaller...")
    try:
        result = subprocess.run([python_cmd, '-c', 'import PyInstaller; print(PyInstaller.__version__)'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"[OK] PyInstaller encontrado: v{result.stdout.strip()}")
        else:
            raise ImportError
    except:
        print("[INFO] Instalando PyInstaller...")
        if not ejecutar_comando(f'{python_cmd} -m pip install PyInstaller', 
                               "Instalación de PyInstaller"):
            sys.exit(1)
    
    # Paso 2: Crear archivo .spec
    crear_spec_file()
    
    # Paso 3: Limpiar builds anteriores
    eliminar_directorio_seguro('build')
    eliminar_directorio_seguro('dist')
    
    # Paso 4: Crear el ejecutable
    build_cmd = f'{python_cmd} -m PyInstaller autosol2.spec --clean --noconfirm'
    if not ejecutar_comando(build_cmd, "Construcción del ejecutable"):
        print("[ERROR] Error al crear el ejecutable")
        sys.exit(1)
    
    # Paso 5: Verificar resultado
    exe_path = Path('dist/Autoforms.exe')
    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print(f"\n[SUCCESS] ¡Ejecutable creado exitosamente!")
        print(f"[INFO] Ubicación: {exe_path.absolute()}")
        print(f"[INFO] Tamaño: {size_mb:.1f} MB")
        
        # Paso 6: Probar el ejecutable
        print(f"\n[TEST] Probando el ejecutable...")
        try:
            # Iniciar el proceso y verificar que se ejecute
            proceso = subprocess.Popen([str(exe_path)], 
                                     stdout=subprocess.PIPE, 
                                     stderr=subprocess.PIPE)
            
            # Esperar un poco para ver si se inicia correctamente
            import time
            time.sleep(3)
            
            # Verificar si el proceso sigue corriendo
            if proceso.poll() is None:
                print("[OK] Ejecutable iniciado correctamente")
                proceso.terminate()  # Cerrar el proceso de prueba
                print("[SUCCESS] ¡Proceso de creación completado con éxito!")
            else:
                stdout, stderr = proceso.communicate()
                print("[WARN] El ejecutable se cerró inmediatamente")
                if stderr:
                    print(f"Error: {stderr.decode('utf-8', errors='ignore')}")
        except Exception as e:
            print(f"[WARN] No se pudo probar el ejecutable automáticamente: {e}")
            print("   Prueba manualmente ejecutando el archivo .exe")
    else:
        print("[ERROR] No se pudo crear el ejecutable")
        sys.exit(1)

if __name__ == "__main__":
    main()
