"""
Frame de filtros específicos para cheques
"""
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from typing import Dict, Any, Callable, Optional
import logging
from datetime import datetime


class ChequeFilterFrame:
    """Frame que contiene los controles de filtros específicos para cheques"""
    
    def __init__(self, parent, search_callback: Callable, clear_callback: Callable):
        self.parent = parent
        self.search_callback = search_callback
        self.clear_callback = clear_callback
        self.logger = logging.getLogger(__name__)
        
        # Variables de filtros
        self.numero_cheque_var = ttk.StringVar()
        self.beneficiario_var = ttk.StringVar()
        self.banco_var = ttk.StringVar()
        self.estado_var = ttk.StringVar()
        self.monto_minimo_var = ttk.StringVar()
        self.monto_maximo_var = ttk.StringVar()
        
        # Datos para comboboxes
        self.bancos_data = [
            "BBVA Bancomer", "Banamex", "Santander", "Banorte", 
            "HSBC", "Scotiabank", "Inbursa", "Azteca", "BanBajío", "Otro"
        ]
        self.estados_data = ["", "PENDIENTE", "COBRADO", "CANCELADO"]
        
        # Crear frame principal
        self.main_frame = ttk.Frame(parent)
        self._create_widgets()
    
    def _create_widgets(self):
        """Crea los controles de filtros"""
        # Frame principal de filtros
        filters_main = ttk.LabelFrame(self.main_frame, text="Filtros de Búsqueda", padding=10)
        filters_main.pack(fill="x", pady=5)
        
        # Primera fila
        row1_frame = ttk.Frame(filters_main)
        row1_frame.pack(fill="x", pady=(0, 10))
        
        # Fecha Inicial
        ttk.Label(row1_frame, text="Fecha Inicial:", font=("Segoe UI", 10)).pack(side="left", padx=(0, 5))
        self.fecha_inicial_entry = ttk.DateEntry(
            row1_frame,
            dateformat='%Y-%m-%d',
            width=12
        )
        self.fecha_inicial_entry.pack(side="left", padx=(0, 15))
        
        # Fecha Final
        ttk.Label(row1_frame, text="Fecha Final:", font=("Segoe UI", 10)).pack(side="left", padx=(0, 5))
        self.fecha_final_entry = ttk.DateEntry(
            row1_frame,
            dateformat='%Y-%m-%d',
            width=12
        )
        self.fecha_final_entry.pack(side="left", padx=(0, 15))
        
        # Estado
        ttk.Label(row1_frame, text="Estado:", font=("Segoe UI", 10)).pack(side="left", padx=(0, 5))
        self.estado_combo = ttk.Combobox(
            row1_frame,
            textvariable=self.estado_var,
            values=self.estados_data,
            width=12,
            state="readonly"
        )
        self.estado_combo.pack(side="left", padx=(0, 15))
        
        # Segunda fila
        row2_frame = ttk.Frame(filters_main)
        row2_frame.pack(fill="x", pady=(0, 10))
        
        # Número de Cheque
        ttk.Label(row2_frame, text="No. Cheque:", font=("Segoe UI", 10)).pack(side="left", padx=(0, 5))
        self.numero_cheque_entry = ttk.Entry(
            row2_frame,
            textvariable=self.numero_cheque_var,
            width=15
        )
        self.numero_cheque_entry.pack(side="left", padx=(0, 15))
        
        # Beneficiario
        ttk.Label(row2_frame, text="Beneficiario:", font=("Segoe UI", 10)).pack(side="left", padx=(0, 5))
        self.beneficiario_entry = ttk.Entry(
            row2_frame,
            textvariable=self.beneficiario_var,
            width=25
        )
        self.beneficiario_entry.pack(side="left", padx=(0, 15))
        
        # Banco
        ttk.Label(row2_frame, text="Banco:", font=("Segoe UI", 10)).pack(side="left", padx=(0, 5))
        self.banco_combo = ttk.Combobox(
            row2_frame,
            textvariable=self.banco_var,
            values=[""] + self.bancos_data,
            width=15
        )
        self.banco_combo.pack(side="left", padx=(0, 15))
        
        # Tercera fila
        row3_frame = ttk.Frame(filters_main)
        row3_frame.pack(fill="x", pady=(0, 10))
        
        # Monto Mínimo
        ttk.Label(row3_frame, text="Monto Mín:", font=("Segoe UI", 10)).pack(side="left", padx=(0, 5))
        self.monto_minimo_entry = ttk.Entry(
            row3_frame,
            textvariable=self.monto_minimo_var,
            width=12
        )
        self.monto_minimo_entry.pack(side="left", padx=(0, 15))
        
        # Monto Máximo
        ttk.Label(row3_frame, text="Monto Máx:", font=("Segoe UI", 10)).pack(side="left", padx=(0, 5))
        self.monto_maximo_entry = ttk.Entry(
            row3_frame,
            textvariable=self.monto_maximo_var,
            width=12
        )
        self.monto_maximo_entry.pack(side="left", padx=(0, 15))
        
        # Botones
        buttons_frame = ttk.Frame(row3_frame)
        buttons_frame.pack(side="right", padx=(20, 0))
        
        # Botón Buscar
        self.search_btn = ttk.Button(
            buttons_frame,
            text="Buscar",
            command=self._on_search_clicked,
            bootstyle="primary",
            width=10
        )
        self.search_btn.pack(side="left", padx=(0, 5))
        
        # Botón Limpiar
        self.clear_btn = ttk.Button(
            buttons_frame,
            text="Limpiar",
            command=self._on_clear_clicked,
            bootstyle="secondary",
            width=10
        )
        self.clear_btn.pack(side="left")
    
    def _on_search_clicked(self):
        """Maneja el evento de búsqueda"""
        self.search_callback()
    
    def _on_clear_clicked(self):
        """Maneja el evento de limpiar filtros"""
        self.clear_filters()
        self.clear_callback()
    
    def get_filters(self) -> Dict[str, Any]:
        """Obtiene los filtros actuales"""
        filters = {
            'fecha_inicial': self.fecha_inicial_entry.entry.get(),
            'fecha_final': self.fecha_final_entry.entry.get(),
            'numero_cheque': self.numero_cheque_var.get(),
            'beneficiario': self.beneficiario_var.get(),
            'banco': self.banco_var.get(),
            'estado': self.estado_var.get(),
            'monto_minimo': self.monto_minimo_var.get(),
            'monto_maximo': self.monto_maximo_var.get()
        }
        return filters
    
    def clear_filters(self):
        """Limpia todos los filtros"""
        # Limpiar DateEntry widgets
        self.fecha_inicial_entry.entry.delete(0, 'end')
        self.fecha_final_entry.entry.delete(0, 'end')
        
        # Limpiar StringVars
        self.numero_cheque_var.set('')
        self.beneficiario_var.set('')
        self.banco_var.set('')
        self.estado_var.set('')
        self.monto_minimo_var.set('')
        self.monto_maximo_var.set('')
