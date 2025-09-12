"""
Updater simple usando solo librerías básicas de Python.
"""
import sys
import os
import time
import shutil
import subprocess
import urllib.request
import json
from pathlib import Path

def main():
    """
    Updater simple que verifica actualizaciones y ejecuta la aplicación.
    """
    print("[UPDATER] Verificando actualizaciones...")
    
    # Determinar directorio base
    if hasattr(sys, 'frozen'):
        current_dir = Path(sys.executable).parent
    else:
        current_dir = Path.cwd()
    
    try:
        # Configuración
        github_repo = "GerzaFM/Autosol2"
        current_version = "0.2.2"
        
        # Verificar actualizaciones usando urllib
        update_info = check_for_updates(github_repo, current_version)
        
        if update_info:
            print(f"[UPDATER] Nueva versión disponible: {update_info['version']}")
            
            # Buscar autoforms.exe
            autoforms_exe = current_dir / "Autoforms.exe"
            
            if not autoforms_exe.exists():
                print("[UPDATER] No se encontró Autoforms.exe")
            else:
                print("[UPDATER] Descargando actualización...")
                if download_and_replace(update_info['download_url'], autoforms_exe):
                    print("[UPDATER] Actualización completada")
                else:
                    print("[UPDATER] Error en la actualización")
        else:
            print("[UPDATER] No hay actualizaciones disponibles")
        
        # Ejecutar Autoforms.exe
        launch_app(current_dir)
        
    except Exception as e:
        print(f"[UPDATER] Error: {e}")
        # Si hay error, intentar ejecutar la aplicación principal
        launch_app(current_dir)

def check_for_updates(repo, current_version):
    """
    Verifica actualizaciones usando urllib.
    """
    try:
        # Intentar con releases/latest
        url = f"https://api.github.com/repos/{repo}/releases/latest"
        
        try:
            with urllib.request.urlopen(url, timeout=10) as response:
                data = json.loads(response.read().decode())
        except urllib.error.HTTPError as e:
            if e.code == 404:
                # Si no hay latest, buscar en todas las releases
                url = f"https://api.github.com/repos/{repo}/releases"
                with urllib.request.urlopen(url, timeout=10) as response:
                    releases = json.loads(response.read().decode())
                    if not releases:
                        return None
                    data = releases[0]  # Tomar la primera (más reciente)
            else:
                raise
        
        latest_version = data.get('tag_name', '').lstrip('v')
        
        # Comparar versiones (simple)
        if is_newer_version(latest_version, current_version):
            # Buscar URL de descarga
            download_url = None
            for asset in data.get('assets', []):
                if asset.get('name', '').lower().endswith('.exe'):
                    download_url = asset.get('browser_download_url')
                    break
            
            if download_url:
                return {
                    'version': latest_version,
                    'download_url': download_url
                }
        
        return None
        
    except Exception as e:
        print(f"[UPDATER] Error verificando actualizaciones: {e}")
        return None

def is_newer_version(latest, current):
    """
    Comparación simple de versiones.
    """
    try:
        latest_parts = [int(x) for x in latest.split('.')]
        current_parts = [int(x) for x in current.split('.')]
        
        # Igualar longitud
        max_len = max(len(latest_parts), len(current_parts))
        latest_parts.extend([0] * (max_len - len(latest_parts)))
        current_parts.extend([0] * (max_len - len(current_parts)))
        
        return latest_parts > current_parts
    except:
        return False

def download_and_replace(url, target_exe):
    """
    Descarga y reemplaza el EXE.
    """
    try:
        print(f"[UPDATER] Descargando desde: {url}")
        
        # Descargar a temporal
        temp_file = target_exe.with_suffix('.exe.new')
        
        with urllib.request.urlopen(url) as response:
            with open(temp_file, 'wb') as f:
                shutil.copyfileobj(response, f)
        
        # Crear backup
        backup_file = target_exe.with_suffix('.exe.backup')
        if target_exe.exists():
            if backup_file.exists():
                backup_file.unlink()
            shutil.copy2(target_exe, backup_file)
        
        # Reemplazar
        if target_exe.exists():
            target_exe.unlink()
        shutil.move(temp_file, target_exe)
        
        print(f"[UPDATER] EXE actualizado: {target_exe}")
        return True
        
    except Exception as e:
        print(f"[UPDATER] Error descargando: {e}")
        return False

def launch_app(base_path):
    """
    Ejecuta la aplicación principal.
    """
    autoforms_exe = base_path / "Autoforms.exe"
    
    if autoforms_exe.exists():
        print("[UPDATER] Iniciando Autoforms...")
        subprocess.Popen([str(autoforms_exe)], cwd=base_path)
    else:
        print("[UPDATER] No se pudo encontrar Autoforms.exe")
        input("Presiona Enter para salir...")

if __name__ == "__main__":
    main()