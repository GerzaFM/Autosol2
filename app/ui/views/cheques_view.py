"""
Vista de Cheques para la aplicación principal
"""
import logging
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from typing import Optional

# Importar la nueva aplicación profesional de cheques
import sys
import os
# Agregar el path de src para poder importar chequeapp
src_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from chequeapp.cheque_app_professional import ChequeAppProfessional
from app.utils.logger import get_logger


class ChequesView(tb.Frame):
    """
    Vista principal para la gestión de cheques
    Integra la aplicación profesional de cheques (frame vacío)
    """
    
    def __init__(self, parent, db_manager=None):
        """
        Inicializa la vista de cheques
        
        Args:
            parent: Widget padre
            db_manager: Gestor de base de datos (opcional)
        """
        super().__init__(parent)
        self.db_manager = db_manager
        self.logger = get_logger(__name__)
        
        # Aplicación de cheques integrada
        self.cheque_app: Optional[ChequeAppProfessional] = None
        
        self._create_layout()
        self.logger.info("Vista de cheques inicializada (frame vacío)")
    
    def _create_layout(self):
        """Crea el layout de la vista"""
        try:
            # Integrar directamente la aplicación profesional de cheques
            self.cheque_app = ChequeAppProfessional(self)
            # No necesitamos pack() adicional porque ChequeAppProfessional ya hace pack() internamente
            
            self.logger.info("Layout de vista de cheques creado correctamente")
            
        except Exception as e:
            self.logger.error(f"Error creando layout de vista de cheques: {e}")
            
            # Mostrar mensaje de error en caso de fallo
            error_frame = tb.Frame(self, padding=20)
            error_frame.pack(fill=BOTH, expand=True)
            
            error_label = tb.Label(
                error_frame,
                text=f"❌ Error al cargar la vista de cheques:\n{str(e)}",
                font=("Segoe UI", 12),
                bootstyle="danger",
                justify=CENTER
            )
            error_label.pack(expand=True)
    
    
    def refresh(self):
        """Refresca la vista de cheques"""
        try:
            if self.cheque_app:
                # Refrescar la aplicación profesional
                self.cheque_app.refresh()
                self.logger.info("Vista de cheques refrescada")
        except Exception as e:
            self.logger.error(f"Error refrescando vista de cheques: {e}")
    
    def get_stats(self):
        """Obtiene estadísticas de cheques para el dashboard (placeholder)"""
        try:
            # Retornar estadísticas vacías para el frame vacío
            return {
                'total_cheques': 0,
                'pendientes': 0,
                'cobrados': 0,
                'cancelados': 0
            }
            
        except Exception as e:
            self.logger.error(f"Error obteniendo estadísticas de cheques: {e}")
            return {
                'total_cheques': 0,
                'pendientes': 0,
                'cobrados': 0,
                'cancelados': 0
            }
