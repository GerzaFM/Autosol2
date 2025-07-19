"""
Gestor de base de datos centralizado para la aplicación.
"""
import logging
from pathlib import Path
from typing import Optional, List
import shutil
from datetime import datetime

from config.settings import config
from app.utils.logger import get_logger

# Importar los modelos existentes
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

try:
    from bd.bd_control import DBManager as OriginalDBManager
    from bd.models import Factura, Proveedor, Reparto, RepartoFavorito
except ImportError as e:
    logging.warning(f"No se pudieron importar los modelos originales: {e}")
    OriginalDBManager = None

class DatabaseManager:
    """
    Gestor centralizado de base de datos que encapsula las operaciones de BD.
    """
    
    def __init__(self):
        """Inicializa el gestor de base de datos."""
        self.logger = get_logger(__name__)
        self.db_path = Path(config.database.path)
        self.backup_dir = Path(config.database.backup_dir)
        
        # Crear directorio de backup si no existe
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Inicializar el gestor original si está disponible
        self.original_manager: Optional[OriginalDBManager] = None
        if OriginalDBManager:
            try:
                self.original_manager = OriginalDBManager()
                self.logger.info("Gestor de base de datos inicializado correctamente")
            except Exception as e:
                self.logger.error(f"Error al inicializar el gestor de BD original: {e}")
        else:
            self.logger.warning("Gestor de BD original no disponible")
    
    def create_backup(self) -> bool:
        """
        Crea una copia de seguridad de la base de datos.
        
        Returns:
            True si el backup fue exitoso, False en caso contrario
        """
        try:
            if not self.db_path.exists():
                self.logger.warning("No existe base de datos para respaldar")
                return False
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = self.backup_dir / f"facturas_backup_{timestamp}.db"
            
            shutil.copy2(self.db_path, backup_file)
            self.logger.info(f"Backup creado: {backup_file}")
            
            # Mantener solo los últimos 10 backups
            self._cleanup_old_backups()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error al crear backup: {e}")
            return False
    
    def _cleanup_old_backups(self, max_backups: int = 10):
        """
        Elimina backups antiguos manteniendo solo los más recientes.
        
        Args:
            max_backups: Número máximo de backups a mantener
        """
        try:
            backup_files = list(self.backup_dir.glob("facturas_backup_*.db"))
            backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            # Eliminar backups antiguos
            for old_backup in backup_files[max_backups:]:
                old_backup.unlink()
                self.logger.info(f"Backup antiguo eliminado: {old_backup}")
                
        except Exception as e:
            self.logger.error(f"Error al limpiar backups antiguos: {e}")
    
    def get_database_info(self) -> dict:
        """
        Obtiene información sobre la base de datos.
        
        Returns:
            Diccionario con información de la BD
        """
        info = {
            "exists": self.db_path.exists(),
            "path": str(self.db_path),
            "size": 0,
            "last_modified": None,
            "backup_dir": str(self.backup_dir),
            "backup_count": 0
        }
        
        try:
            if info["exists"]:
                stat = self.db_path.stat()
                info["size"] = stat.st_size
                info["last_modified"] = datetime.fromtimestamp(stat.st_mtime)
            
            # Contar backups
            backup_files = list(self.backup_dir.glob("facturas_backup_*.db"))
            info["backup_count"] = len(backup_files)
            
        except Exception as e:
            self.logger.error(f"Error al obtener información de BD: {e}")
        
        return info
    
    # Métodos de acceso a datos (delegando al gestor original)
    
    def guardar_factura(self, proveedor_data: dict, solicitud_data: dict, 
                       conceptos_data: list, totales_data: dict, 
                       categorias_data: dict, comentarios_data: dict):
        """
        Guarda una factura en la base de datos.
        """
        if not self.original_manager:
            raise RuntimeError("Gestor de BD no disponible")
        
        return self.original_manager.guardar_solicitud(
            proveedor_data, solicitud_data, conceptos_data,
            totales_data, categorias_data, comentarios_data
        )
    
    def obtener_favoritos_usuario(self, usuario_id: int) -> List:
        """
        Obtiene los favoritos de un usuario.
        """
        if not self.original_manager:
            return []
        
        return self.original_manager.obtener_favoritos_usuario(usuario_id)
    
    def obtener_favorito_por_posicion(self, usuario_id: int, posicion: int):
        """
        Obtiene un favorito específico por posición.
        """
        if not self.original_manager:
            return None
        
        return self.original_manager.obtener_favorito_por_posicion(usuario_id, posicion)
    
    def guardar_reparto_favorito(self, usuario_id: int, posicion: int, 
                                nombre: str, categorias: dict):
        """
        Guarda un reparto como favorito.
        """
        if not self.original_manager:
            return None
        
        return self.original_manager.guardar_reparto_favorito(
            usuario_id, posicion, nombre, categorias
        )
    
    def close(self):
        """
        Cierra la conexión a la base de datos.
        """
        try:
            if self.original_manager:
                # El gestor original maneja sus propias conexiones
                pass
            self.logger.info("Conexión a base de datos cerrada")
        except Exception as e:
            self.logger.error(f"Error al cerrar conexión a BD: {e}")
