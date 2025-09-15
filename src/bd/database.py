"""
Configuración y gestión de base de datos PostgreSQL.
Sistema actualizado para usar exclusivamente PostgreSQL.
"""

import os
import logging
from pathlib import Path
from peewee import (
    PostgresqlDatabase, 
    Database,
    OperationalError,
    IntegrityError
)

from config.settings import config

logger = logging.getLogger(__name__)

class DatabaseManager:
    """
    Gestor de conexiones de base de datos PostgreSQL.
    """
    
    def __init__(self):
        self.db = None
        self._connection_config = config.database
        self._initialize_database()
    
    def _initialize_database(self):
        """Inicializa la conexión de base de datos PostgreSQL."""
        # Obtener información de conexión
        conn_info = self._connection_config.get_connection_info()
        
        logger.info(f"Configurando PostgreSQL para entorno: {conn_info['environment'].upper()}")
        
        try:
            db = PostgresqlDatabase(
                database=self._connection_config.pg_database,
                host=self._connection_config.pg_host,
                port=self._connection_config.pg_port,
                user=self._connection_config.pg_user,
                password=self._connection_config.pg_password,
                autorollback=True,
                autocommit=True,
                # Configuración de codificación para Windows
                options="-c client_encoding=utf8"
            )
            
            # Probar conexión
            db.connect()
            logger.info(f"OK - Conectado a PostgreSQL: {conn_info['host']}:{conn_info['port']}/{conn_info['database']}")
            db.close()
            
            self.db = db
            logger.info(f"Base de datos inicializada: PostgreSQL ({conn_info['environment'].upper()})")
            
        except Exception as e:
            logger.error(f"Error conectando a PostgreSQL ({conn_info['environment'].upper()}): {e}")
            raise Exception(f"No se pudo conectar a la base de datos PostgreSQL: {e}")
    
    def _create_postgresql_connection(self) -> PostgresqlDatabase:
        """Crea conexión a PostgreSQL."""
        try:
            db = PostgresqlDatabase(
                database=self._connection_config.pg_database,
                host=self._connection_config.pg_host,
                port=self._connection_config.pg_port,
                user=self._connection_config.pg_user,
                password=self._connection_config.pg_password,
                autorollback=True,
                autocommit=True,
                # Configuración de codificación para Windows
                options="-c client_encoding=utf8"
            )
            
            # Probar conexión
            db.connect()
            logger.info(f"Conectado a PostgreSQL: {self._connection_config.pg_host}:{self._connection_config.pg_port}/{self._connection_config.pg_database}")
            db.close()
            
            return db
            
        except Exception as e:
            logger.error(f"Error conectando a PostgreSQL: {e}")
            raise Exception(f"No se pudo conectar a la base de datos PostgreSQL: {e}")
    
    def get_connection(self) -> Database:
        """Obtiene la conexión de base de datos."""
        return self.db
    
    def test_connection(self) -> bool:
        """Prueba la conexión de base de datos."""
        try:
            if self.db.is_closed():
                self.db.connect()
            
            # Ejecutar una consulta simple
            self.db.execute_sql("SELECT 1;")
            
            if not self.db.is_closed():
                self.db.close()
            
            return True
            
        except Exception as e:
            logger.error(f"Error probando conexión: {e}")
            return False
    
    def create_tables(self, models: list):
        """Crea las tablas en la base de datos."""
        try:
            self.db.create_tables(models, safe=True)
            logger.info(f"Tablas creadas/verificadas: {len(models)} modelos")
            return True
        except Exception as e:
            logger.error(f"Error creando tablas: {e}")
            return False
    
    def backup_database(self) -> str:
        """Crea un backup de la base de datos PostgreSQL."""
        return self._backup_postgresql()
    
    def _backup_postgresql(self) -> str:
        """Crea backup de PostgreSQL usando pg_dump."""
        try:
            import subprocess
            from datetime import datetime
            
            backup_dir = Path(self._connection_config.backup_dir)
            backup_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = backup_dir / f"tcm_matehuala_backup_{timestamp}.sql"
            
            # Comando pg_dump
            cmd = [
                'pg_dump',
                f"--host={self._connection_config.pg_host}",
                f"--port={self._connection_config.pg_port}",
                f"--username={self._connection_config.pg_user}",
                f"--dbname={self._connection_config.pg_database}",
                '--verbose',
                '--clean',
                '--no-owner',
                '--no-privileges',
                f"--file={backup_file}"
            ]
            
            # Configurar variable de entorno para password
            env = os.environ.copy()
            env['PGPASSWORD'] = self._connection_config.pg_password
            
            # Ejecutar pg_dump
            result = subprocess.run(cmd, env=env, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"Backup PostgreSQL creado: {backup_file}")
                return str(backup_file)
            else:
                logger.error(f"Error en pg_dump: {result.stderr}")
                return None
                
        except Exception as e:
            logger.error(f"Error creando backup PostgreSQL: {e}")
            return None
    
    def migrate_data(self, source_db_path: str = None):
        """Migra datos desde otra base de datos."""
        if not source_db_path:
            logger.warning("No se especificó ruta de base de datos origen para migración")
            return
        
        logger.info(f"Iniciando migración desde: {source_db_path}")
        
        # Esta función se implementará más tarde cuando creemos el script de migración
        pass
    
    def close(self):
        """Cierra la conexión de base de datos."""
        if self.db and not self.db.is_closed():
            self.db.close()
            logger.info("Conexión de base de datos cerrada")

# Instancia global del gestor de base de datos
db_manager = DatabaseManager()
db = db_manager.get_connection()
