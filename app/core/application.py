"""
Clase principal de la aplicación que maneja la inicialización y coordinación general.
"""
import logging
import ttkbootstrap as tb
from typing import Optional

from config.settings import config
from app.ui.views.main_window import MainWindow
from app.utils.logger import get_logger

class Application:
    """
    Clase principal que coordina todos los componentes de la aplicación.
    """
    
    def __init__(self):
        """Inicializa la aplicación."""
        self.logger = get_logger(__name__)
        self.window: Optional[MainWindow] = None
        
        self._initialize_components()
    
    def _initialize_components(self):
        """Inicializa los componentes principales de la aplicación."""
        try:
            # Inicializar ventana principal
            self.window = MainWindow(
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
            
            if not self.window:
                raise RuntimeError("La ventana principal no está inicializada")
            
            # Configurar eventos de cierre
            self.window.protocol("WM_DELETE_WINDOW", self._on_closing)
            
            # Iniciar el bucle principal
            self.window.mainloop()
            
        except Exception as e:
            self.logger.error(f"Error al ejecutar la aplicación: {e}")
            raise
    
    def _on_closing(self):
        """Maneja el cierre de la aplicación."""
        try:
            self.logger.info("Cerrando aplicación")
            
            # Cerrar ventana
            if self.window:
                self.window.quit()
                self.window.destroy()
                
        except Exception as e:
            self.logger.error(f"Error al cerrar la aplicación: {e}")
        finally:
            # Asegurar que la aplicación se cierre
            import sys
            sys.exit(0)
