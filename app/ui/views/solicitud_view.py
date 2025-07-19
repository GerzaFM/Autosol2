"""
Vista de solicitud refactorizada que encapsula la funcionalidad de SolicitudApp.
"""
import ttkbootstrap as tb
from ttkbootstrap.constants import *
import sys
import os
from typing import Optional

from app.utils.logger import get_logger

# Importar la clase original de solicitud
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

try:
    from solicitudapp.solicitud_app_professional import SolicitudApp
except ImportError as e:
    SolicitudApp = None
    
class SolicitudView(tb.Frame):
    """
    Vista contenedora para la funcionalidad de solicitudes.
    Encapsula SolicitudApp y la integra en la nueva arquitectura.
    """
    
    def __init__(self, parent, db_manager, **kwargs):
        """
        Inicializa la vista de solicitud.
        
        Args:
            parent: Widget padre
            db_manager: Gestor de base de datos
        """
        super().__init__(parent, **kwargs)
        
        self.logger = get_logger(__name__)
        self.db_manager = db_manager
        self.solicitud_app: Optional[SolicitudApp] = None
        
        self._create_solicitud_component()
    
    def _create_solicitud_component(self):
        """Crea e integra el componente de solicitud."""
        try:
            if SolicitudApp is None:
                self._show_error("SolicitudApp no está disponible")
                return
            
            # Crear una instancia de SolicitudApp dentro de este frame
            self.solicitud_app = SolicitudApp(master=self)
            self.solicitud_app.pack(fill=BOTH, expand=True)
            
            self.logger.info("Componente de solicitud creado correctamente")
            
        except Exception as e:
            self.logger.error(f"Error al crear componente de solicitud: {e}")
            self._show_error(f"Error al cargar solicitud: {str(e)}")
    
    def _show_error(self, error_message: str):
        """
        Muestra un mensaje de error en lugar del componente de solicitud.
        
        Args:
            error_message: Mensaje de error a mostrar
        """
        error_frame = tb.Frame(self)
        error_frame.pack(fill=BOTH, expand=True)
        
        error_label = tb.Label(
            error_frame,
            text="Error al cargar solicitud",
            font=("Segoe UI", 16, "bold"),
            bootstyle="danger"
        )
        error_label.pack(pady=50)
        
        message_label = tb.Label(
            error_frame,
            text=error_message,
            font=("Segoe UI", 12),
            bootstyle="inverse-dark"
        )
        message_label.pack(pady=20)
        
        retry_button = tb.Button(
            error_frame,
            text="Reintentar",
            bootstyle="primary",
            command=self._retry_load
        )
        retry_button.pack(pady=10)
    
    def _retry_load(self):
        """Reintenta cargar el componente de solicitud."""
        # Limpiar el frame
        for widget in self.winfo_children():
            widget.destroy()
        
        # Intentar crear el componente nuevamente
        self._create_solicitud_component()
    
    def get_solicitud_app(self) -> Optional[SolicitudApp]:
        """
        Obtiene la instancia de SolicitudApp.
        
        Returns:
            La instancia de SolicitudApp o None si no está disponible
        """
        return self.solicitud_app
