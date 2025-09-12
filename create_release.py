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

def compile_executable():
    """Compila el ejecutable usando crear_exe.py"""
    try:
        print("[COMPILE] Ejecutando crear_exe.py...")
        result = subprocess.run([sys.executable, 'crear_exe.py'], 
                              capture_output=True, text=True, cwd=PROJECT_ROOT)
        
        if result.returncode == 0:
            print("[OK] Ejecutable compilado exitosamente")
            return True
        else:
            print(f"[ERROR] Error compilando ejecutable: {result.stderr}")
            return False
    except Exception as e:
        print(f"[ERROR] Error inesperado compilando ejecutable: {e}")
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
    
    # Compilar ejecutable si se solicita
    exe_path = None
    if include_exe:
        print(f"\n[BUILD] Compilando ejecutable...")
        if not compile_executable():
            print("[ERROR] Error al compilar ejecutable")
            return False
        
        exe_path = Path('dist/Autoforms.exe')
        if not exe_path.exists():
            print("[ERROR] Ejecutable no encontrado después de compilar")
            return False
        
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print(f"[OK] Ejecutable compilado: {size_mb:.1f} MB")
    
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
    if include_exe and exe_path and exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        exe_info = f"""

### [EXECUTABLE] Ejecutable incluido:
- **Autoforms.exe** ({size_mb:.1f} MB) - Versión standalone, no requiere Python instalado
- Compatible con Windows 10/11
- Incluye todas las dependencias"""

    release_body = f"""## [RELEASE] Autoforms v{version}

### [FEATURES] Características principales:
- [UPDATE] Sistema de actualización automática desde GitHub Releases
- [UI] Interfaz moderna con ttkbootstrap y tema darkly
- [DB] Soporte para bases de datos PostgreSQL
- [REPORTS] Sistema de gestión de solicitudes y reportes
- [AUTH] Sistema de autenticación de usuarios
- [SPLASH] Pantalla de splash profesional{exe_info}

### [TECH] Tecnologías utilizadas:
- Python 3.13+
- ttkbootstrap (UI Framework)
- PostgreSQL (Base de datos)
- Peewee ORM
- PyPDF2 (Procesamiento PDF)

### 📥 Instalación:

#### 🚀 Opción 1: Ejecutable (Recomendado)
1. Descargar `Autoforms.exe` de los assets
2. Ejecutar directamente - No requiere instalación

#### 🛠️ Opción 2: Código fuente
1. Descargar el código fuente
2. Instalar dependencias: `pip install -r requirements.txt`
3. Configurar base de datos en `config/settings.py`
4. Ejecutar: `python main.py`

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
            
            # Subir ejecutable si está disponible
            if include_exe and exe_path and exe_path.exists():
                print(f"\n[UPLOAD] Subiendo ejecutable...")
                # Usar el mismo token que para crear la release
                if upload_asset_to_release(release_info['id'], exe_path, github_token):
                    print("[OK] Ejecutable subido a la release")
                else:
                    print("[WARN] Release creada pero ejecutable no subido")
            
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
    prerelease = False
    include_exe = True
    
    # Verificar argumentos
    if len(sys.argv) > 1:
        if "--prerelease" in sys.argv or "--pre" in sys.argv:
            prerelease = True
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
                print("[INCLUDE] Incluye: Ejecutable compilado automáticamente")
            else:
                print("[INCLUDE] Incluye: Solo código fuente")
            print("")
            print("[OPTIONS] Opciones disponibles:")
            print("  --confirm          Confirmar y crear release")
            print("  --prerelease       Marcar como pre-release")
            print("  --pre              Alias para --prerelease")
            print("  --no-exe           No incluir ejecutable (solo código fuente)")
            print("")
            print("[EXAMPLES] Ejemplos:")
            print("  python create_release.py --confirm")
            print("  python create_release.py --prerelease --confirm")
            print("  python create_release.py --no-exe --confirm")
    else:
        print("[WARN] Este script creará una release en GitHub")
        print(f"[TAG] Tag: v{config.version}")
        print(f"[NAME] Nombre: Autoforms v{config.version}")
        print("[INCLUDE] Incluye: Ejecutable compilado automáticamente")
        print("")
        print("[OPTIONS] Opciones disponibles:")
        print("  --confirm          Confirmar y crear release")
        print("  --prerelease       Marcar como pre-release")
        print("  --pre              Alias para --prerelease")
        print("  --no-exe           No incluir ejecutable (solo código fuente)")
        print("")
        print("[EXAMPLES] Ejemplos:")
        print("  python create_release.py --confirm")
        print("  python create_release.py --prerelease --confirm")
        print("  python create_release.py --no-exe --confirm")