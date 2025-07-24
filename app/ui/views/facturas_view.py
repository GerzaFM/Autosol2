"""
Vista de facturas contenedora que encapsula la funcionalidad de BuscarApp Refactorizada.
"""
import ttkbootstrap as tb
from ttkbootstrap.constants import *
import sys
import os
from typing import Optional, Any

from app.utils.logger import get_logger

# Importar la clase de búsqueda de facturas refactorizada
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

try:
    from buscarapp.buscar_app_refactored import BuscarAppRefactored
except ImportError as e:
    BuscarAppRefactored = None

class FacturasView(tb.Frame):
    """
    Vista contenedora para la funcionalidad de búsqueda de facturas.
    Encapsula BuscarAppRefactored y la integra en la nueva arquitectura.
    """
    
    def __init__(self, parent, db_manager, **kwargs):
        """
        Inicializa la vista de facturas.
        
        Args:
            parent: Widget padre
            db_manager: Gestor de base de datos
        """
        super().__init__(parent, **kwargs)
        
        self.logger = get_logger(__name__)
        self.db_manager = db_manager
        self.buscar_app: Optional[Any] = None
        
        self._create_buscar_component()
    
    def _create_buscar_component(self):
        """Crea e integra el componente de búsqueda de facturas refactorizado."""
        try:
            if BuscarAppRefactored is None:
                self._show_error("BuscarAppRefactored no está disponible")
                return
            
            # Crear una instancia de BuscarAppRefactored dentro de este frame
            self.buscar_app = BuscarAppRefactored(master=self)
            self.buscar_app.pack(fill=BOTH, expand=True)
            
            self.logger.info("Componente de búsqueda de facturas refactorizado creado correctamente")
            
        except Exception as e:
            self.logger.error(f"Error al crear componente de búsqueda refactorizado: {e}")
            self._show_error(f"Error al cargar búsqueda de facturas: {str(e)}")
    
    def _show_error(self, error_message: str):
        """
        Muestra un mensaje de error en lugar del componente de búsqueda.
        
        Args:
            error_message: Mensaje de error a mostrar
        """
        error_frame = tb.Frame(self)
        error_frame.pack(fill=BOTH, expand=True)
        
        error_label = tb.Label(
            error_frame,
            text="Error al cargar búsqueda de facturas",
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
        """Reintenta cargar el componente de búsqueda."""
        # Limpiar el frame
        for widget in self.winfo_children():
            widget.destroy()
        
        # Intentar crear el componente nuevamente
        self._create_buscar_component()
    
    def get_buscar_app(self) -> Optional[Any]:
        """
        Obtiene la instancia de BuscarAppRefactored.
        
        Returns:
            La instancia de BuscarAppRefactored o None si no está disponible
        """
        return self.buscar_app
    
    def refresh(self):
        """Método público para refrescar la vista."""
        if self.buscar_app and hasattr(self.buscar_app, '_load_initial_data'):
            self.buscar_app._load_initial_data()
    
    def search(self, term: str):
        """Método público para realizar búsqueda."""
        if self.buscar_app and hasattr(self.buscar_app, 'search_frame'):
            if hasattr(self.buscar_app.search_frame, 'texto_busqueda_var'):
                self.buscar_app.search_frame.texto_busqueda_var.set(term)
                # Trigger search if there's a search method
                if hasattr(self.buscar_app, '_on_search'):
                    filters = self.buscar_app.search_frame.get_filters()
                    self.buscar_app._on_search(filters)
