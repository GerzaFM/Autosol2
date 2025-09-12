"""
Script para crear releases automáticamente en GitHub.
"""
import subprocess
import sys
import requests
import json
from pathlib import Path

# Agregar directorios al path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import config

def compile_executables():
    """Compila ambos ejecutables (Autoforms.exe y updater.exe) usando crear_exe.py"""
    try:
        print("[COMPILE] Ejecutando crear_exe.py...")
        result = subprocess.run([sys.executable, 'crear_exe.py'], 
                              capture_output=True, text=True, cwd=PROJECT_ROOT)
        
        if result.returncode == 0:
            print("[OK] Ejecutables compilados exitosamente")
            
            # Verificar que ambos ejecutables fueron creados
            autoforms_exe = Path('dist/Autoforms.exe')
            updater_exe = Path('dist/updater.exe')  # Ahora ambos están en dist/
            
            if autoforms_exe.exists() and updater_exe.exists():
                print("[OK] Ambos ejecutables encontrados en dist/")
                return True
            else:
                print("[ERROR] No se encontraron todos los ejecutables después de compilar")
                return False
        else:
            print(f"[ERROR] Error compilando ejecutables: {result.stderr}")
            return False
    except Exception as e:
        print(f"[ERROR] Error inesperado compilando ejecutables: {e}")
        return False

def upload_asset_to_release(release_id, file_path, github_token=None):
    """Sube un asset (archivo) a una release existente en GitHub"""
    if not github_token:
        print("[WARN] Token de GitHub no disponible, omitiendo subida de ejecutable")
        return True
    
    try:
        file_path = Path(file_path)
        if not file_path.exists():
            print(f"[ERROR] Archivo no encontrado: {file_path}")
            return False
        
        # URL para subir assets
        upload_url = f"https://uploads.github.com/repos/GerzaFM/Autosol2/releases/{release_id}/assets"
        
        headers = {
            'Authorization': f'token {github_token}',
            'Content-Type': 'application/octet-stream'
        }
        
        params = {
            'name': file_path.name
        }
        
        print(f"[UPLOAD] Subiendo {file_path.name}...")
        
        with open(file_path, 'rb') as f:
            response = requests.post(upload_url, headers=headers, params=params, data=f)
        
        if response.status_code == 201:
            print(f"[OK] {file_path.name} subido exitosamente")
            return True
        else:
            print(f"[ERROR] Error subiendo {file_path.name}: {response.status_code}")
            print(f"[RESPONSE] Respuesta: {response.text}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Error subiendo asset: {e}")
        return False

def get_github_token():
    """Obtiene el token de GitHub desde variable de entorno o input del usuario"""
    import os
    
    # Intentar obtener desde variable de entorno
    token = os.getenv('GITHUB_TOKEN')
    if token:
        print("[OK] Token de GitHub encontrado en variables de entorno")
        return token
    
    # Si no hay token, explicar al usuario
    print("\n[WARN] Para subir el ejecutable se necesita un token de GitHub")
    print("[INFO] Instrucciones:")
    print("1. Ve a: https://github.com/settings/tokens")
    print("2. Genera un token con permisos 'repo'")
    print("3. Configúralo como variable de entorno: GITHUB_TOKEN=tu_token")
    print("4. O ingrésalo ahora (será temporal)")
    
    while True:
        choice = input("\n¿Quieres ingresar el token ahora? (s/n/omitir): ").lower().strip()
        
        if choice in ['s', 'si', 'sí', 'y', 'yes']:
            token = input("Ingresa tu token de GitHub: ").strip()
            if token:
                return token
            else:
                print("[ERROR] Token vacío")
        elif choice in ['omitir', 'skip', 'o']:
            print("[WARN] Omitiendo subida de ejecutable")
            return None
        elif choice in ['n', 'no']:
            print("[WARN] Continuando sin subir ejecutable")
            return None
        else:
            print("[ERROR] Respuesta no válida")

def create_release(prerelease=False, include_exe=True):
    """Crea una nueva release en GitHub usando la API."""
    version = config.version
    tag_name = f"v{version}"
    release_name = f"Autoforms v{version}"
    
    if prerelease:
        release_name += " (Pre-release)"
        print(f"[PRERELEASE] Creando PRE-RELEASE: {tag_name}")
    else:
        print(f"[RELEASE] Creando release: {tag_name}")
    
    print(f"[INFO] Nombre: {release_name}")
    
    # Compilar ejecutables si se solicita
    exe_paths = []
    if include_exe:
        print(f"\n[BUILD] Compilando ejecutables...")
        if not compile_executables():
            print("[ERROR] Error al compilar ejecutables")
            return False
        
        # Verificar que ambos ejecutables existen
        autoforms_exe = Path('dist/Autoforms.exe')
        updater_exe = Path('dist/updater.exe')
        
        if not autoforms_exe.exists():
            print("[ERROR] Autoforms.exe no encontrado después de compilar")
            return False
        if not updater_exe.exists():
            print("[ERROR] updater.exe no encontrado después de compilar")
            return False
        
        exe_paths = [autoforms_exe, updater_exe]
        
        # Mostrar información de los ejecutables
        for exe_path in exe_paths:
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"[OK] {exe_path.name}: {size_mb:.1f} MB")
    
    # Verificar si git está configurado
    try:
        result = subprocess.run(['git', 'status'], capture_output=True, text=True)
        if result.returncode != 0:
            print("[ERROR] Error: No es un repositorio git o git no está disponible")
            return False
    except FileNotFoundError:
        print("[ERROR] Error: Git no está instalado")
        return False
    
    # Crear tag local
    print("[TAG] Creando tag local...")
    result = subprocess.run(['git', 'tag', '-a', tag_name, '-m', release_name], 
                          capture_output=True, text=True)
    if result.returncode != 0:
        if "already exists" in result.stderr:
            print("[WARN] Tag ya existe localmente, eliminando...")
            subprocess.run(['git', 'tag', '-d', tag_name], capture_output=True)
            result = subprocess.run(['git', 'tag', '-a', tag_name, '-m', release_name], 
                                  capture_output=True, text=True)
        if result.returncode != 0:
            print(f"[ERROR] Error creando tag: {result.stderr}")
            return False
    
    # Push tag
    print("[PUSH] Subiendo tag a GitHub...")
    result = subprocess.run(['git', 'push', 'origin', tag_name, '--force'], 
                          capture_output=True, text=True)
    if result.returncode != 0:
        print(f"[ERROR] Error subiendo tag: {result.stderr}")
        return False
    
    # Crear release usando GitHub API
    print("[RELEASE] Creando release en GitHub...")
    
    # Obtener información del último commit
    result = subprocess.run(['git', 'rev-parse', 'HEAD'], capture_output=True, text=True)
    target_commitish = result.stdout.strip()
    
    # Preparar descripción de la release
    exe_info = ""
    if include_exe and exe_paths:
        autoforms_size = exe_paths[0].stat().st_size / (1024 * 1024)  # Autoforms.exe
        updater_size = exe_paths[1].stat().st_size / (1024 * 1024)    # updater.exe
        exe_info = f"""

### [EXECUTABLES] Ejecutables incluidos:
- **updater.exe** ({updater_size:.1f} MB) - Ejecutable principal con auto-actualizador
- **Autoforms.exe** ({autoforms_size:.1f} MB) - Aplicación principal (se actualiza automáticamente)
- Compatible con Windows 10/11
- Incluye todas las dependencias
- **Instrucciones**: Ejecutar `updater.exe` como programa principal"""

    release_body = f"""## [PRE-RELEASE] Autoforms v{version} {'(Pre-release)' if prerelease else '(Release Estable)'}

### [NEW] Nuevas características en esta versión:
- [AUTO-UPDATE] ✨ **Sistema de actualización automática completamente funcional**
- [DUAL-EXE] 🔄 **Arquitectura dual-ejecutable** (updater.exe + Autoforms.exe)
- [SEAMLESS] 🚀 **Actualizaciones transparentes sin intervención del usuario**
- [SMART-LAUNCH] 🎯 **Lanzamiento inteligente con verificación de versiones**

### [FEATURES] Características principales:
- [UPDATE] Sistema de actualización automática desde GitHub Releases
- [UI] Interfaz moderna con ttkbootstrap y tema darkly
- [DB] Soporte para bases de datos PostgreSQL con configuración dual (TEST/PRODUCTION)
- [REPORTS] Sistema de gestión de solicitudes y reportes
- [AUTH] Sistema de autenticación de usuarios
- [SPLASH] Pantalla de splash profesional{exe_info}

### [TECH] Tecnologías utilizadas:
- Python 3.13+
- ttkbootstrap (UI Framework)
- PostgreSQL (Base de datos)
- Peewee ORM
- PyPDF2 (Procesamiento PDF)
- PyInstaller (Compilación de ejecutables)

### [AUTO-UPDATE] Cómo funciona el sistema de actualización:
1. **updater.exe** se ejecuta como programa principal
2. Verifica automáticamente si hay nuevas versiones en GitHub
3. Si hay actualizaciones disponibles, descarga el nuevo **Autoforms.exe**
4. Reemplaza la versión anterior automáticamente
5. Lanza la aplicación actualizada

### 📥 Instalación:

#### 🚀 Opción 1: Ejecutables (Recomendado)
1. Descargar **AMBOS** ejecutables de los assets: `updater.exe` y `Autoforms.exe`
2. Colocar ambos archivos en la misma carpeta
3. Ejecutar **`updater.exe`** como programa principal
4. El updater verificará actualizaciones y lanzará Autoforms automáticamente

#### 🛠️ Opción 2: Código fuente
1. Descargar el código fuente
2. Instalar dependencias: `pip install -r requirements.txt`
3. Configurar base de datos en `config/settings.py`
4. Ejecutar: `python main.py`

⚠️ **IMPORTANTE**: 
- Para el funcionamiento del auto-updater, ambos ejecutables deben estar en la misma carpeta
- {'Esta es una PRE-RELEASE para pruebas y desarrollo' if prerelease else 'Esta es una RELEASE ESTABLE para producción'}

---
**Desarrollado por Gerzahin Flores Martinez**
"""

    # Datos de la release
    release_data = {
        "tag_name": tag_name,
        "target_commitish": target_commitish,
        "name": release_name,
        "body": release_body,
        "draft": False,
        "prerelease": prerelease
    }
    
    # URL de la API de GitHub
    api_url = "https://api.github.com/repos/GerzaFM/Autosol2/releases"
    
    # Obtener token para la API
    github_token = get_github_token()
    if not github_token:
        print("[ERROR] No se puede crear release sin token de GitHub")
        return False
    
    # Headers con autenticación
    headers = {
        'Authorization': f'token {github_token}',
        'Accept': 'application/vnd.github.v3+json',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.post(api_url, json=release_data, headers=headers)
        
        if response.status_code == 201:
            release_info = response.json()
            print("[OK] Release creada exitosamente!")
            print(f"[URL] URL: {release_info['html_url']}")
            print(f"[ID] ID: {release_info['id']}")
            if prerelease:
                print("[PRERELEASE] Marcada como PRE-RELEASE")
            
            # Subir ejecutables si están disponibles
            if include_exe and exe_paths:
                print(f"\n[UPLOAD] Subiendo ejecutables...")
                
                for exe_path in exe_paths:
                    print(f"[UPLOAD] Subiendo {exe_path.name}...")
                    if upload_asset_to_release(release_info['id'], exe_path, github_token):
                        print(f"[OK] {exe_path.name} subido a la release")
                    else:
                        print(f"[WARN] {exe_path.name} no pudo subirse")
                
                print("[OK] Proceso de subida completado")
            
            return True
        else:
            print(f"[ERROR] Error creando release: {response.status_code}")
            print(f"[RESPONSE] Respuesta: {response.text}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Error de conexión: {e}")
        print("[TAG] Tag creado, pero release manual requerida")
        print(f"[URL] Crear manualmente en: https://github.com/GerzaFM/Autosol2/releases/new?tag={tag_name}")
        return False

if __name__ == "__main__":
    prerelease = True  # Por defecto siempre pre-release
    include_exe = True
    
    # Verificar argumentos
    if len(sys.argv) > 1:
        if "--release" in sys.argv or "--stable" in sys.argv:
            prerelease = False  # Solo si se especifica explícitamente
        if "--no-exe" in sys.argv:
            include_exe = False
        if "--confirm" in sys.argv:
            create_release(prerelease=prerelease, include_exe=include_exe)
        else:
            print("[WARN] Este script creará una release en GitHub")
            print(f"[TAG] Tag: v{config.version}")
            print(f"[NAME] Nombre: Autoforms v{config.version}")
            if prerelease:
                print("[TYPE] Tipo: PRE-RELEASE")
            else:
                print("[TYPE] Tipo: RELEASE ESTABLE")
            if include_exe:
                print("[INCLUDE] Incluye: Ejecutables compilados automáticamente (updater.exe + Autoforms.exe)")
            else:
                print("[INCLUDE] Incluye: Solo código fuente")
            print("")
            print("[OPTIONS] Opciones disponibles:")
            print("  --confirm          Confirmar y crear release")
            print("  --release          Crear release ESTABLE (por defecto es pre-release)")
            print("  --stable           Alias para --release")
            print("  --no-exe           No incluir ejecutables (solo código fuente)")
            print("")
            print("[EXAMPLES] Ejemplos:")
            print("  python create_release.py --confirm                    # Pre-release (por defecto)")
            print("  python create_release.py --release --confirm          # Release estable")
            print("  python create_release.py --no-exe --confirm           # Pre-release sin ejecutables")
    else:
        print("[WARN] Este script creará una release en GitHub")
        print(f"[TAG] Tag: v{config.version}")
        print(f"[NAME] Nombre: Autoforms v{config.version}")
        print("[INCLUDE] Incluye: Ejecutables compilados automáticamente (updater.exe + Autoforms.exe)")
        print("")
        print("[OPTIONS] Opciones disponibles:")
        print("  --confirm          Confirmar y crear release")
        print("  --release          Crear release ESTABLE (por defecto es pre-release)")
        print("  --stable           Alias para --release")
        print("  --no-exe           No incluir ejecutables (solo código fuente)")
        print("")
        print("[EXAMPLES] Ejemplos:")
        print("  python create_release.py --confirm                    # Pre-release (por defecto)")
        print("  python create_release.py --release --confirm          # Release estable")
        print("  python create_release.py --no-exe --confirm           # Pre-release sin ejecutables")