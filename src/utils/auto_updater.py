"""
Sistema de actualización automática desde GitHub Releases.
"""
import requests
import json
import os
import sys
import subprocess
import tempfile
import zipfile
import shutil
import time
from pathlib import Path
from packaging import version
from typing import Optional, Dict, Any
from app.utils.logger import get_logger
from config.settings import config

class AutoUpdater:
    """
    Clase para manejar actualizaciones automáticas desde GitHub Releases.
    """
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.github_repo = "GerzaFM/Autosol2"
        self.current_version = config.version
        self.github_api_url = f"https://api.github.com/repos/{self.github_repo}/releases/latest"
        
    def check_for_updates(self) -> Optional[Dict[str, Any]]:
        """
        Verifica si hay una nueva versión disponible en GitHub Releases.
        
        Returns:
            Dict con información de la release si hay actualización disponible, None si no.
        """
        try:
            self.logger.info(f"Verificando actualizaciones para versión actual: {self.current_version}")
            
            # Hacer petición a la API de GitHub
            response = requests.get(self.github_api_url, timeout=10)
            response.raise_for_status()
            
            release_data = response.json()
            latest_version = release_data.get('tag_name', '').lstrip('v')
            
            self.logger.info(f"Última versión disponible: {latest_version}")
            
            # Comparar versiones
            if self._is_newer_version(latest_version, self.current_version):
                self.logger.info(f"Nueva versión encontrada: {latest_version}")
                return {
                    'version': latest_version,
                    'tag_name': release_data.get('tag_name'),
                    'name': release_data.get('name'),
                    'body': release_data.get('body'),
                    'download_url': self._get_download_url(release_data),
                    'published_at': release_data.get('published_at')
                }
            else:
                self.logger.info("El programa está actualizado")
                return None
                
        except requests.exceptions.RequestException as e:
            self.logger.warning(f"Error al verificar actualizaciones: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Error inesperado al verificar actualizaciones: {e}")
            return None
    
    def _is_newer_version(self, latest: str, current: str) -> bool:
        """
        Compara dos versiones usando packaging.version.
        
        Args:
            latest: Versión más reciente
            current: Versión actual
            
        Returns:
            True si latest es mayor que current
        """
        try:
            return version.parse(latest) > version.parse(current)
        except Exception as e:
            self.logger.warning(f"Error al comparar versiones {latest} vs {current}: {e}")
            return False
    
    def _get_download_url(self, release_data: Dict[str, Any]) -> Optional[str]:
        """
        Obtiene la URL de descarga del archivo ZIP desde los assets de la release.
        
        Args:
            release_data: Datos de la release de GitHub
            
        Returns:
            URL de descarga del ZIP o None si no se encuentra
        """
        assets = release_data.get('assets', [])
        
        # Buscar archivo ZIP en los assets
        for asset in assets:
            if asset.get('name', '').endswith('.zip'):
                return asset.get('browser_download_url')
        
        # Si no hay assets, usar el zipball_url
        return release_data.get('zipball_url')
    
    def download_and_install_update(self, update_info: Dict[str, Any]) -> bool:
        """
        Descarga e instala la actualización.
        
        Args:
            update_info: Información de la actualización obtenida de check_for_updates
            
        Returns:
            True si la actualización fue exitosa, False en caso contrario
        """
        try:
            download_url = update_info.get('download_url')
            if not download_url:
                self.logger.error("No se encontró URL de descarga")
                return False
            
            self.logger.info(f"Descargando actualización desde: {download_url}")
            
            # Crear directorio temporal
            with tempfile.TemporaryDirectory() as temp_dir:
                zip_path = Path(temp_dir) / "update.zip"
                extract_path = Path(temp_dir) / "extracted"
                
                # Descargar archivo
                self._download_file(download_url, zip_path)
                
                # Extraer archivo
                self._extract_zip(zip_path, extract_path)
                
                # Instalar actualización
                self._install_update(extract_path)
                
                self.logger.info("Actualización instalada exitosamente")
                return True
                
        except Exception as e:
            self.logger.error(f"Error durante la actualización: {e}")
            return False
    
    def _download_file(self, url: str, destination: Path) -> None:
        """
        Descarga un archivo desde una URL.
        
        Args:
            url: URL del archivo a descargar
            destination: Ruta de destino para guardar el archivo
        """
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        
        with open(destination, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        progress = (downloaded / total_size) * 100
                        print(f"\rDescargando: {progress:.1f}%", end='', flush=True)
        
        print()  # Nueva línea después del progreso
        self.logger.info(f"Descarga completada: {destination}")
    
    def _extract_zip(self, zip_path: Path, extract_path: Path) -> None:
        """
        Extrae un archivo ZIP.
        
        Args:
            zip_path: Ruta del archivo ZIP
            extract_path: Directorio donde extraer
        """
        extract_path.mkdir(parents=True, exist_ok=True)
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_path)
        
        self.logger.info(f"Archivo extraído en: {extract_path}")
    
    def _install_update(self, extract_path: Path) -> None:
        """
        Instala la actualización copiando archivos.
        
        Args:
            extract_path: Directorio con los archivos extraídos
        """
        # Buscar el directorio raíz del proyecto en los archivos extraídos
        source_dirs = list(extract_path.iterdir())
        if len(source_dirs) == 1 and source_dirs[0].is_dir():
            source_path = source_dirs[0]
        else:
            source_path = extract_path
        
        current_dir = Path.cwd()
        backup_dir = current_dir.parent / f"{current_dir.name}_backup_{int(time.time())}"
        
        self.logger.info(f"Creando respaldo en: {backup_dir}")
        shutil.copytree(current_dir, backup_dir)
        
        # Lista de archivos/carpetas a excluir durante la actualización
        exclude_patterns = {
            '.env', 'config.ini', 'facturas.db', 'logs', 
            '__pycache__', '.git', '.venv', 'database/backups'
        }
        
        # Copiar archivos nuevos
        for item in source_path.iterdir():
            if item.name not in exclude_patterns:
                dest_path = current_dir / item.name
                
                if dest_path.exists():
                    if dest_path.is_dir():
                        shutil.rmtree(dest_path)
                    else:
                        dest_path.unlink()
                
                if item.is_dir():
                    shutil.copytree(item, dest_path)
                else:
                    shutil.copy2(item, dest_path)
        
        self.logger.info("Archivos actualizados correctamente")
    
    def restart_application(self) -> None:
        """
        Reinicia la aplicación actual.
        """
        self.logger.info("Reiniciando aplicación...")
        
        # Obtener el comando para reiniciar
        if getattr(sys, 'frozen', False):
            # Si es un ejecutable compilado
            os.execv(sys.executable, [sys.executable])
        else:
            # Si es un script de Python
            os.execv(sys.executable, [sys.executable] + sys.argv)


def check_and_update() -> bool:
    """
    Función principal para verificar y aplicar actualizaciones.
    
    Returns:
        True si se aplicó una actualización (requiere reinicio), False si no
    """
    updater = AutoUpdater()
    
    # Verificar si hay actualizaciones
    update_info = updater.check_for_updates()
    
    if update_info:
        print(f"\n[NEW] Nueva versión disponible: {update_info['version']}")
        print(f"[INFO] Cambios: {update_info.get('name', 'Actualización disponible')}")
        
        # Preguntar al usuario si desea actualizar
        response = input("\n¿Desea actualizar ahora? (s/n): ").lower().strip()
        
        if response in ['s', 'si', 'sí', 'y', 'yes']:
            print("\n[UPDATE] Iniciando actualización...")
            
            if updater.download_and_install_update(update_info):
                print("[OK] Actualización completada. Reiniciando aplicación...")
                updater.restart_application()
                return True
            else:
                print("[ERROR] Error durante la actualización")
                return False
        else:
            print("[SKIP] Actualización omitida")
    
    return False


if __name__ == "__main__":
    check_and_update()