"""
Vista de Cheques para la aplicación principal
"""
import logging
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from typing import Optional

# Importar la aplicación completa de cheques
import sys
import os
# Agregar el path de src para poder importar chequeapp
src_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from chequeapp import ChequeAppComplete
from app.utils.logger import get_logger


class ChequesView(tb.Frame):
    """
    Vista principal para la gestión de cheques
    Integra la aplicación completa de cheques en la interfaz principal
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
        self.cheque_app: Optional[ChequeAppComplete] = None
        
        self._create_layout()
        self.logger.info("Vista de cheques inicializada")
    
    def _create_layout(self):
        """Crea el layout de la vista"""
        try:
            # Frame principal con padding
            main_frame = tb.Frame(self, padding=10)
            main_frame.pack(fill=BOTH, expand=True)
            
            # Título de la sección
            title_frame = tb.Frame(main_frame)
            title_frame.pack(fill=X, pady=(0, 10))
            
            title_label = tb.Label(
                title_frame,
                text="🏦 Gestión de Cheques",
                font=("Segoe UI", 16, "bold"),
                bootstyle="primary"
            )
            title_label.pack(side=LEFT)
            
            # Línea separadora
            separator = tb.Separator(main_frame, orient=HORIZONTAL)
            separator.pack(fill=X, pady=(0, 10))
            
            # Integrar la aplicación completa de cheques
            self.cheque_app = ChequeAppComplete(main_frame)
            # No necesitamos pack() aquí porque ChequeAppComplete ya hace pack() internamente
            
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
                # Refrescar la búsqueda inicial
                self.cheque_app._perform_initial_search()
                self.logger.info("Vista de cheques refrescada")
        except Exception as e:
            self.logger.error(f"Error refrescando vista de cheques: {e}")
    
    def get_stats(self):
        """Obtiene estadísticas de cheques para el dashboard"""
        try:
            if not self.cheque_app or not self.cheque_app.cheque_controller:
                return {
                    'total_cheques': 0,
                    'pendientes': 0,
                    'cobrados': 0,
                    'cancelados': 0
                }
            
            state = self.cheque_app.cheque_controller.get_state()
            
            total = len(state.all_cheques)
            pendientes = len([c for c in state.all_cheques if c.estado == 'PENDIENTE'])
            cobrados = len([c for c in state.all_cheques if c.estado == 'COBRADO'])
            cancelados = len([c for c in state.all_cheques if c.estado == 'CANCELADO'])
            
            return {
                'total_cheques': total,
                'pendientes': pendientes,
                'cobrados': cobrados,
                'cancelados': cancelados
            }
            
        except Exception as e:
            self.logger.error(f"Error obteniendo estadísticas de cheques: {e}")
            return {
                'total_cheques': 0,
                'pendientes': 0,
                'cobrados': 0,
                'cancelados': 0
            }
