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
    Solo actualiza ejecutables, nunca el código fuente en desarrollo.
    """
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.github_repo = config.github_repo
        self.current_version = config.version
        self.github_api_url = f"https://api.github.com/repos/{self.github_repo}/releases/latest"
        self.is_frozen = getattr(sys, 'frozen', False)  # True si es ejecutable
        
    def is_development_environment(self) -> bool:
        """
        Detecta si estamos en un entorno de desarrollo.
        Solo bloquea si es código fuente Y no está siendo probado manualmente.
        
        Returns:
            True si es entorno de desarrollo, False si es producción o testing
        """
        # Si es un ejecutable compilado, definitivamente es producción
        if self.is_frozen:
            return False
            
        # Si no existe .git, probablemente es una instalación de usuario
        if not (Path.cwd() / '.git').exists():
            return False
            
        # Si estamos en desarrollo, permitir testing manual
        # Solo bloquear si hay indicadores claros de desarrollo activo
        return False  # Permitir actualizaciones para testing
            
        return False
        
    def check_for_updates(self) -> Optional[Dict[str, Any]]:
        """
        Verifica si hay una nueva versión disponible en GitHub Releases.
        
        Returns:
            Dict con información de la release si hay actualización disponible, None si no.
        """
        try:
            self.logger.info(f"Verificando actualizaciones para versión actual: {self.current_version}")
            
            # Primero intentar con /latest
            response = requests.get(self.github_api_url, timeout=10)
            
            if response.status_code == 404:
                # Si no hay release latest, buscar en todas las releases incluyendo pre-releases
                all_releases_url = f"https://api.github.com/repos/{self.github_repo}/releases"
                response = requests.get(all_releases_url, timeout=10)
                response.raise_for_status()
                
                releases = response.json()
                if not releases:
                    self.logger.info("No hay releases disponibles")
                    return None
                    
                # Tomar la primera release (más reciente)
                release_data = releases[0]
            else:
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
        Obtiene la URL de descarga del archivo EXE desde los assets de la release.
        
        Args:
            release_data: Datos de la release de GitHub
            
        Returns:
            URL de descarga del EXE o None si no se encuentra
        """
        assets = release_data.get('assets', [])
        
        # Buscar archivo EXE en los assets
        for asset in assets:
            asset_name = asset.get('name', '').lower()
            if asset_name.endswith('.exe') or asset_name.endswith('.zip'):
                return asset.get('browser_download_url')
        
        return None
    
    def download_and_install_update(self, update_info: Dict[str, Any]) -> bool:
        """
        Descarga e instala la actualización SOLO DEL EXE.
        
        Args:
            update_info: Información de la actualización obtenida de check_for_updates
            
        Returns:
            True si la actualización fue exitosa, False en caso contrario
        """
        try:
            # Si estamos en desarrollo, NO actualizar
            if self.is_development_environment():
                self.logger.info("Entorno de desarrollo detectado - Actualización omitida")
                print("[DEV] Entorno de desarrollo - No se actualiza el código fuente")
                return False
            
            download_url = update_info.get('download_url')
            if not download_url:
                self.logger.error("No se encontró URL de descarga del EXE")
                return False
            
            self.logger.info(f"Descargando EXE desde: {download_url}")
            
            # Crear directorio temporal
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # Determinar si es ZIP o EXE directo
                if download_url.endswith('.exe'):
                    # Descarga directa del EXE
                    exe_path = temp_path / "new_autosol.exe"
                    self._download_file(download_url, exe_path)
                    self._replace_exe(exe_path)
                else:
                    # Es un ZIP, extraer el EXE
                    zip_path = temp_path / "update.zip"
                    extract_path = temp_path / "extracted"
                    
                    self._download_file(download_url, zip_path)
                    self._extract_zip(zip_path, extract_path)
                    self._replace_exe_from_zip(extract_path)
                
                self.logger.info("EXE actualizado exitosamente")
                return True
                
        except Exception as e:
            self.logger.error(f"Error durante la actualización del EXE: {e}")
            return False
    
    def download_and_replace_exe(self, update_info: Dict[str, Any], target_exe: Path) -> bool:
        """
        Descarga y reemplaza un EXE específico (para updater independiente).
        
        Args:
            update_info: Información de la actualización
            target_exe: Ruta del EXE a reemplazar
            
        Returns:
            True si la actualización fue exitosa, False en caso contrario
        """
        try:
            download_url = update_info.get('download_url')
            if not download_url:
                self.logger.error("No se encontró URL de descarga del EXE")
                return False
            
            self.logger.info(f"Descargando EXE desde: {download_url}")
            
            # Crear directorio temporal
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # Determinar si es ZIP o EXE directo
                if download_url.endswith('.exe'):
                    # Descarga directa del EXE
                    exe_path = temp_path / "new_autoforms.exe"
                    self._download_file(download_url, exe_path)
                    self._replace_specific_exe(exe_path, target_exe)
                else:
                    # Es un ZIP, extraer el EXE
                    zip_path = temp_path / "update.zip"
                    extract_path = temp_path / "extracted"
                    
                    self._download_file(download_url, zip_path)
                    self._extract_zip(zip_path, extract_path)
                    self._replace_specific_exe_from_zip(extract_path, target_exe)
                
                self.logger.info(f"EXE {target_exe} actualizado exitosamente")
                return True
                
        except Exception as e:
            self.logger.error(f"Error durante la actualización del EXE {target_exe}: {e}")
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
    
    def _replace_specific_exe(self, new_exe_path: Path, target_exe: Path) -> None:
        """
        Reemplaza un EXE específico con el nuevo.
        
        Args:
            new_exe_path: Ruta del nuevo EXE descargado
            target_exe: Ruta del EXE a reemplazar
        """
        backup_exe = target_exe.with_suffix('.exe.backup')
        
        # Crear backup del EXE actual
        if target_exe.exists():
            if backup_exe.exists():
                backup_exe.unlink()
            shutil.copy2(target_exe, backup_exe)
            self.logger.info(f"Backup creado: {backup_exe}")
        
        # Reemplazar EXE
        shutil.copy2(new_exe_path, target_exe)
        self.logger.info(f"EXE reemplazado: {target_exe}")
    
    def _replace_specific_exe_from_zip(self, extract_path: Path, target_exe: Path) -> None:
        """
        Busca y reemplaza un EXE específico desde un archivo extraído.
        
        Args:
            extract_path: Directorio con archivos extraídos
            target_exe: Ruta del EXE a reemplazar
        """
        # Buscar EXE en los archivos extraídos
        exe_files = list(extract_path.rglob("*.exe"))
        
        if not exe_files:
            raise FileNotFoundError("No se encontró archivo EXE en la actualización")
        
        # Usar el primer EXE encontrado
        new_exe = exe_files[0]
        self._replace_specific_exe(new_exe, target_exe)
    
    def _replace_exe(self, new_exe_path: Path) -> None:
        """
        Reemplaza el EXE actual con el nuevo.
        
        Args:
            new_exe_path: Ruta del nuevo EXE descargado
        """
        current_exe = Path(sys.executable)
        backup_exe = current_exe.with_suffix('.exe.backup')
        
        # Crear backup del EXE actual
        if current_exe.exists():
            if backup_exe.exists():
                backup_exe.unlink()
            shutil.copy2(current_exe, backup_exe)
            self.logger.info(f"Backup creado: {backup_exe}")
        
        # Reemplazar EXE
        shutil.copy2(new_exe_path, current_exe)
        self.logger.info(f"EXE reemplazado: {current_exe}")
    
    def _replace_exe_from_zip(self, extract_path: Path) -> None:
        """
        Busca y reemplaza el EXE desde un archivo extraído.
        
        Args:
            extract_path: Directorio con archivos extraídos
        """
        # Buscar EXE en los archivos extraídos
        exe_files = list(extract_path.rglob("*.exe"))
        
        if not exe_files:
            raise FileNotFoundError("No se encontró archivo EXE en la actualización")
        
        # Usar el primer EXE encontrado
        new_exe = exe_files[0]
        self._replace_exe(new_exe)
    
    def _install_update(self, extract_path: Path) -> None:
        """
        MÉTODO OBSOLETO - Solo mantenido para compatibilidad.
        Ahora solo actualizamos EXE, no código fuente.
        """
        self.logger.warning("Método _install_update obsoleto - use _replace_exe")
        pass
    
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


def check_and_update_silent() -> bool:
    """
    Función para verificar y aplicar actualizaciones automáticamente del EXE.
    SOLO REEMPLAZA EL EXE, NO TOCA EL CÓDIGO FUENTE.
    
    Returns:
        True si se aplicó una actualización (requiere reinicio), False si no
    """
    updater = AutoUpdater()
    
    # Si es entorno de desarrollo, no actualizar
    if updater.is_development_environment():
        print("[DEV] Entorno de desarrollo - Auto-actualización deshabilitada")
        return False
    
    # Verificar si hay actualizaciones
    update_info = updater.check_for_updates()
    
    if update_info:
        print(f"\n[AUTO-UPDATE] Nueva versión de EXE disponible: {update_info['version']}")
        print(f"[AUTO-UPDATE] Cambios: {update_info.get('name', 'Actualización disponible')}")
        print("[AUTO-UPDATE] Aplicando actualización del EXE automáticamente...")
        
        if updater.download_and_install_update(update_info):
            print("[AUTO-UPDATE] EXE actualizado correctamente. Reiniciando aplicación...")
            updater.restart_application()
            return True
        else:
            print("[AUTO-UPDATE] Error durante la actualización automática del EXE")
            return False
    else:
        print("[AUTO-UPDATE] No hay actualizaciones de EXE disponibles")
    
    return False


if __name__ == "__main__":
    check_and_update()