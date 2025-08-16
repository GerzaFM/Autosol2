"""
Clase principal de la aplicación que maneja la inicialización y coordinación general.
"""
import logging
import ttkbootstrap as tb
from typing import Optional

from config.settings import config
from mainapp import MainApp
from app.utils.logger import get_logger

class Application:
    """
    Clase principal que coordina todos los componentes de la aplicación.
    """
    
    def __init__(self):
        """Inicializa la aplicación."""
        self.logger = get_logger(__name__)
        self.app: Optional[MainApp] = None
        
        self._initialize_components()
    
    def _initialize_components(self):
        """Inicializa los componentes principales de la aplicación."""
        try:
            # Inicializar aplicación principal
            self.app = MainApp(
                title=config.app_name,
                size=config.ui.window_size,
                theme=config.ui.theme
            )
            self.logger.info("Ventana principal inicializada")
            
        except Exception as e:
            self.logger.error(f"Error al inicializar componentes: {e}")
            raise
    
    def run(self):
        """Ejecuta la aplicación."""
        try:
            self.logger.info("Iniciando aplicación")
            
            if not self.app:
                raise RuntimeError("La aplicación principal no está inicializada")
            
            # Configurar eventos de cierre
            self.app.main_window.protocol("WM_DELETE_WINDOW", self._on_closing)
            
            # Iniciar el bucle principal
            self.app.run()
            
        except Exception as e:
            self.logger.error(f"Error al ejecutar la aplicación: {e}")
            raise
    
    def _on_closing(self):
        """Maneja el cierre de la aplicación."""
        try:
            self.logger.info("Cerrando aplicación")
            
            # Cerrar aplicación
            if self.app and self.app.main_window:
                self.app.main_window.quit()
                self.app.main_window.destroy()
                
        except Exception as e:
            self.logger.error(f"Error al cerrar la aplicación: {e}")
        finally:
            # Asegurar que la aplicación se cierre
            import sys
            sys.exit(0)
