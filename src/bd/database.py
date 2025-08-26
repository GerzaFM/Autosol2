"""
Configuración y gestión de base de datos multi-plataforma.
Soporta SQLite (desarrollo) y PostgreSQL (producción).
"""

import os
import logging
from pathlib import Path
from peewee import (
    SqliteDatabase, 
    PostgresqlDatabase, 
    Database,
    OperationalError,
    IntegrityError
)

from config.settings import config

logger = logging.getLogger(__name__)

class DatabaseManager:
    """
    Gestor de conexiones de base de datos que soporta múltiples tipos.
    """
    
    def __init__(self):
        self.db = None
        self._connection_config = config.database
        self._initialize_database()
    
    def _initialize_database(self):
        """Inicializa la conexión de base de datos según la configuración."""
        db_type = self._connection_config.db_type.lower()
        
        # Forzar PostgreSQL para migración
        if db_type == "postgresql":
            logger.info("Configurando PostgreSQL...")
            try:
                db = PostgresqlDatabase(
                    database="tcm_matehuala",
                    host="localhost",
                    port=5432,
                    user="postgres",
                    password="Nissan#2024",
                    autorollback=True,
                    autocommit=True
                )
                
                # Probar conexión
                db.connect()
                logger.info(f"✓ Conectado a PostgreSQL: localhost:5432/tcm_matehuala")
                db.close()
                
                self.db = db
                logger.info(f"Base de datos inicializada: PostgreSQL")
                return
                
            except Exception as e:
                logger.error(f"Error conectando a PostgreSQL: {e}")
                logger.info("Fallback a SQLite")
        
        # Fallback a SQLite
        self.db = self._create_sqlite_connection()
        logger.info(f"Base de datos inicializada: SQLite")
    
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
            logger.info("Fallback a SQLite")
            return self._create_sqlite_connection()
    
    def _create_sqlite_connection(self) -> SqliteDatabase:
        """Crea conexión a SQLite."""
        db_path = self._connection_config.sqlite_path
        
        # Crear directorio si no existe
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        db = SqliteDatabase(
            db_path,
            pragmas={
                'journal_mode': 'wal',
                'cache_size': -1 * 64000,  # 64MB
                'foreign_keys': 1,
                'ignore_check_constraints': 0,
                'synchronous': 0
            }
        )
        
        logger.info(f"Configurado SQLite: {db_path}")
        return db
    
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
        """Crea un backup de la base de datos."""
        if isinstance(self.db, SqliteDatabase):
            return self._backup_sqlite()
        elif isinstance(self.db, PostgresqlDatabase):
            return self._backup_postgresql()
        else:
            logger.warning("Backup no soportado para este tipo de base de datos")
            return None
    
    def _backup_sqlite(self) -> str:
        """Crea backup de SQLite."""
        try:
            from datetime import datetime
            import shutil
            
            backup_dir = Path(self._connection_config.backup_dir)
            backup_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = backup_dir / f"facturas_backup_{timestamp}.db"
            
            # Copiar archivo de base de datos
            shutil.copy2(self._connection_config.sqlite_path, backup_file)
            
            logger.info(f"Backup SQLite creado: {backup_file}")
            return str(backup_file)
            
        except Exception as e:
            logger.error(f"Error creando backup SQLite: {e}")
            return None
    
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
            source_db_path = self._connection_config.sqlite_path
        
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
