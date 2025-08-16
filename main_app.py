"""
Punto de entrada principal de la aplicación TCM Matehuala.
"""
import sys
import os
import logging
from pathlib import Path

# Agregar el directorio raíz al path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import config, LOGS_DIR
from app.core.application import Application
from app.utils.logger import setup_logging

def setup_environment():
    """Configura el entorno de la aplicación."""
    # Crear directorios necesarios
    LOGS_DIR.mkdir(exist_ok=True)
    
    # Configurar logging
    setup_logging(config.log_level, config.log_file)
    
    logger = logging.getLogger(__name__)
    logger.info(f"Iniciando {config.app_name} v{config.version}")
    logger.info(f"Directorio de trabajo: {PROJECT_ROOT}")

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
