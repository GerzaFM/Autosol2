"""
Punto de entrada principal de la aplicación TCM Matehuala.
"""
import sys
import os
import logging
from pathlib import Path

# Agregar el directorio raíz y src al path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / 'src'))

from config.settings import config, LOGS_DIR
from app.core.application import Application
from app.utils.logger import setup_logging
from src.bd.database import db_manager

def setup_environment():
    """Configura el entorno de la aplicación."""
    # Crear directorios necesarios
    LOGS_DIR.mkdir(exist_ok=True)
    
    # Configurar logging
    setup_logging(config.log_level, config.log_file)
    
    logger = logging.getLogger(__name__)
    logger.info(f"Iniciando {config.app_name} v{config.version}")
    logger.info(f"Directorio de trabajo: {PROJECT_ROOT}")
    
    # Probar conexión de base de datos
    if not db_manager.test_connection():
        logger.error("No se pudo establecer conexión con la base de datos")
        raise ConnectionError("Base de datos no disponible")
    
    # Crear tablas si es necesario
    from src.bd.models import ALL_MODELS
    db_manager.create_tables(ALL_MODELS)
    logger.info("Base de datos inicializada correctamente")

def main():
    """Función principal de la aplicación."""
    try:
        setup_environment()
         
        # Crear e iniciar la aplicación
        app = Application()
        app.run()
        
    except Exception as e:
        logging.error(f"Error crítico en la aplicación: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
