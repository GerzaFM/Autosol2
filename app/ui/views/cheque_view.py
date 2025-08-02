"""
Vista contenedora para la aplicación de Cheques.
Encapsula ChequeApp y la integra en la nueva arquitectura.
"""
import ttkbootstrap as tb
from ttkbootstrap.constants import *
import sys
import os

from app.utils.logger import get_logger

# Importar la clase de la aplicación de cheques
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

try:
    from chequeapp.cheque_app import ChequeApp
except ImportError as e:
    ChequeApp = None


class ChequeView(tb.Frame):
    """
    Vista contenedora para la funcionalidad de cheques.
    Encapsula ChequeApp y la integra en la nueva arquitectura.
    """
    
    def __init__(self, parent, db_manager, **kwargs):
        """
        Inicializa la vista de cheques.
        
        Args:
            parent: Widget padre
            db_manager: Gestor de base de datos
        """
        super().__init__(parent, **kwargs)
        
        self.logger = get_logger(__name__)
        self.db_manager = db_manager
        self.cheque_app = None
        
        self._create_cheque_component()
    
    def _create_cheque_component(self):
        """Crea e integra el componente de cheques."""
        try:
            if ChequeApp is None:
                self._show_error("ChequeApp no está disponible")
                return
            
            # Crear una instancia de ChequeApp dentro de este frame
            self.cheque_app = ChequeApp(master=self)
            self.cheque_app.pack(fill=BOTH, expand=True)
            
            self.logger.info("Componente de cheques creado correctamente")
            
        except Exception as e:
            self.logger.error(f"Error al crear componente de cheques: {e}")
            self._show_error(f"Error al cargar cheques: {str(e)}")
    
    def _show_error(self, error_message: str):
        """
        Muestra un mensaje de error en lugar del componente de cheques.
        
        Args:
            error_message: Mensaje de error a mostrar
        """
        error_frame = tb.Frame(self)
        error_frame.pack(fill=BOTH, expand=True)
        
        error_label = tb.Label(
            error_frame,
            text="Error al cargar aplicación de cheques",
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
        """Reintenta cargar el componente de cheques."""
        # Limpiar el frame
        for widget in self.winfo_children():
            widget.destroy()
        
        # Intentar crear el componente nuevamente
        self._create_cheque_component()
    
    def get_cheque_app(self):
        """
        Obtiene la instancia de ChequeApp.
        
        Returns:
            La instancia de ChequeApp o None si no está disponible
        """
        return self.cheque_app
