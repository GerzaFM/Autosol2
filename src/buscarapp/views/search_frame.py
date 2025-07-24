"""
Vista para el frame de búsqueda y filtros
"""
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.scrolled import ScrolledFrame
from typing import Dict, Any, Callable, Optional
import logging
from datetime import datetime


class SearchFrame:
    """Frame que contiene los controles de búsqueda y filtros"""
    
    def __init__(self, parent, on_search_callback: Optional[Callable] = None, 
                 on_clear_callback: Optional[Callable] = None):
        self.parent = parent
        self.on_search_callback = on_search_callback
        self.on_clear_callback = on_clear_callback
        self.logger = logging.getLogger(__name__)
        
        # Variables de los filtros
        self.fecha_inicial_var = ttk.StringVar()
        self.fecha_final_var = ttk.StringVar()
        self.tipo_filtro_var = ttk.StringVar()
        self.proveedor_filtro_var = ttk.StringVar()
        self.no_vale_filtro_var = ttk.StringVar()
        self.solo_cargado_var = ttk.BooleanVar()
        self.solo_pagado_var = ttk.BooleanVar()
        self.texto_busqueda_var = ttk.StringVar()
        
        # Crear frame principal
        self.main_frame = ttk.LabelFrame(
            parent, 
            text="🔍 Filtros de Búsqueda", 
            bootstyle="primary"
        )
        self.main_frame.pack(fill="x", padx=5, pady=5)
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Crea todos los widgets del frame de búsqueda"""
        
        # Frame principal de filtros con padding
        filters_main = ttk.Frame(self.main_frame)
        filters_main.pack(fill="x", padx=10, pady=10)
        
        # Primera fila de filtros
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
        
        # Tipo de Vale
        ttk.Label(row1_frame, text="Tipo:", font=("Segoe UI", 10)).pack(side="left", padx=(0, 5))
        self.tipo_combobox = ttk.Combobox(
            row1_frame,
            textvariable=self.tipo_filtro_var,
            values=self._get_tipos_factura(),
            state="readonly",
            width=25
        )
        self.tipo_combobox.pack(side="left", padx=(0, 15))
        
        # Proveedor
        ttk.Label(row1_frame, text="Proveedor:", font=("Segoe UI", 10)).pack(side="left", padx=(0, 5))
        self.proveedor_entry = ttk.Entry(
            row1_frame,
            textvariable=self.proveedor_filtro_var,
            width=25,
            font=("Segoe UI", 11)
        )
        self.proveedor_entry.pack(side="left", padx=(0, 15))
        
        # No Vale
        ttk.Label(row1_frame, text="No Vale:", font=("Segoe UI", 10)).pack(side="left", padx=(0, 5))
        self.no_vale_entry = ttk.Entry(
            row1_frame,
            textvariable=self.no_vale_filtro_var,
            width=15,
            font=("Segoe UI", 11)
        )
        self.no_vale_entry.pack(side="left")
        
        # Segunda fila de filtros
        row2_frame = ttk.Frame(filters_main)
        row2_frame.pack(fill="x", pady=(0, 10))
        
        # Solo Cargado
        self.solo_cargado_check = ttk.Checkbutton(
            row2_frame,
            text="Solo Cargado",
            variable=self.solo_cargado_var,
            bootstyle="success-round-toggle"
        )
        self.solo_cargado_check.pack(side="left", padx=(0, 15))
        
        # Solo Pagado
        self.solo_pagado_check = ttk.Checkbutton(
            row2_frame,
            text="Solo Pagado",
            variable=self.solo_pagado_var,
            bootstyle="info-round-toggle"
        )
        self.solo_pagado_check.pack(side="left", padx=(0, 15))
        
        # Espaciador
        spacer = ttk.Frame(row2_frame)
        spacer.pack(side="left", fill="x", expand=True)
        
        # Botones de acción
        self.buscar_btn = ttk.Button(
            row2_frame,
            text="Buscar",
            command=self._on_search_clicked,
            bootstyle="primary"
        )
        self.buscar_btn.pack(side="right", padx=(10, 0))
        
        self.limpiar_btn = ttk.Button(
            row2_frame,
            text="Limpiar Filtros",
            command=self._on_clear_clicked,
            bootstyle="secondary-outline"
        )
        self.limpiar_btn.pack(side="right", padx=(10, 0))
        
        # Tercera fila - Búsqueda de texto
        row3_frame = ttk.Frame(filters_main)
        row3_frame.pack(fill="x")
        
        # Campo de búsqueda general
        ttk.Label(row3_frame, text="Buscar:", font=("Segoe UI", 10)).pack(side="left", padx=(0, 5))
        self.texto_busqueda_entry = ttk.Entry(
            row3_frame,
            textvariable=self.texto_busqueda_var,
            font=("Segoe UI", 11),
            width=40
        )
        self.texto_busqueda_entry.pack(side="left", padx=(0, 10))
        
        # Información de resultados
        self.estado_label = ttk.Label(
            row3_frame,
            text="",
            font=("Segoe UI", 10),
            bootstyle="inverse-secondary"
        )
        self.estado_label.pack(side="right")
        
        # Configurar eventos Enter
        self._setup_enter_events()
    
    def _get_tipos_factura(self):
        """Obtiene la lista de tipos de factura disponibles"""
        return [
            "",  # Opción vacía
            "I - Ingreso",
            "E - Egreso", 
            "T - Traslado",
            "N - Nómina",
            "P - Pago"
        ]
    
    def _setup_enter_events(self):
        """Configura eventos para búsqueda con Enter"""
        widgets_para_enter = [
            self.fecha_inicial_entry,
            self.fecha_final_entry,
            self.proveedor_entry,
            self.no_vale_entry,
            self.texto_busqueda_entry
        ]
        
        for widget in widgets_para_enter:
            widget.bind('<Return>', lambda e: self._on_search_clicked())
    
    def _clear_dates(self):
        """Limpia las fechas seleccionadas"""
        if hasattr(self.fecha_inicial_entry, 'entry'):
            self.fecha_inicial_entry.entry.delete(0, 'end')
        if hasattr(self.fecha_final_entry, 'entry'):
            self.fecha_final_entry.entry.delete(0, 'end')
    
    def _on_search_clicked(self):
        """Maneja el evento de click en buscar"""
        if self.on_search_callback:
            filters = self.get_filters()
            self.on_search_callback(filters)
    
    def _on_clear_clicked(self):
        """Maneja el evento de click en limpiar"""
        self.clear_filters()
        if self.on_clear_callback:
            self.on_clear_callback()
    
    def get_filters(self) -> Dict[str, Any]:
        """
        Obtiene los valores actuales de todos los filtros
        
        Returns:
            Dict con los valores de los filtros
        """
        return {
            'fecha_inicial': self.fecha_inicial_entry.entry.get() if hasattr(self.fecha_inicial_entry, 'entry') else '',
            'fecha_final': self.fecha_final_entry.entry.get() if hasattr(self.fecha_final_entry, 'entry') else '',
            'tipo_filtro': self.tipo_filtro_var.get(),
            'proveedor_filtro': self.proveedor_filtro_var.get(),
            'no_vale_filtro': self.no_vale_filtro_var.get(),
            'solo_cargado': self.solo_cargado_var.get(),
            'solo_pagado': self.solo_pagado_var.get(),
            'texto_busqueda': self.texto_busqueda_var.get()
        }
    
    def clear_filters(self):
        """Limpia todos los filtros"""
        # Limpiar fechas usando el método correcto para DateEntry
        if hasattr(self.fecha_inicial_entry, 'entry'):
            self.fecha_inicial_entry.entry.delete(0, 'end')
        if hasattr(self.fecha_final_entry, 'entry'):  
            self.fecha_final_entry.entry.delete(0, 'end')
        
        self.tipo_filtro_var.set("")
        self.proveedor_filtro_var.set("")
        self.no_vale_filtro_var.set("")
        self.solo_cargado_var.set(False)
        self.solo_pagado_var.set(False)
        self.texto_busqueda_var.set("")
        self.set_status("Filtros limpiados")
    
    def set_status(self, mensaje: str, style: str = "info"):
        """
        Actualiza el mensaje de estado
        
        Args:
            mensaje: Mensaje a mostrar
            style: Estilo del mensaje (info, success, warning, danger)
        """
        self.estado_label.config(text=mensaje, bootstyle=style)
    
    def set_filters_from_dict(self, filters_dict: Dict[str, Any]):
        """
        Establece los filtros desde un diccionario
        
        Args:
            filters_dict: Diccionario con los valores de los filtros
        """
        # Establecer fechas
        fecha_inicial = filters_dict.get('fecha_inicial', '')
        fecha_final = filters_dict.get('fecha_final', '')
        
        if hasattr(self.fecha_inicial_entry, 'entry') and fecha_inicial:
            self.fecha_inicial_entry.entry.delete(0, 'end')
            self.fecha_inicial_entry.entry.insert(0, fecha_inicial)
        
        if hasattr(self.fecha_final_entry, 'entry') and fecha_final:
            self.fecha_final_entry.entry.delete(0, 'end')
            self.fecha_final_entry.entry.insert(0, fecha_final)
        
        self.tipo_filtro_var.set(filters_dict.get('tipo_filtro', ''))
        self.proveedor_filtro_var.set(filters_dict.get('proveedor_filtro', ''))
        self.no_vale_filtro_var.set(filters_dict.get('no_vale_filtro', ''))
        self.solo_cargado_var.set(filters_dict.get('solo_cargado', False))
        self.solo_pagado_var.set(filters_dict.get('solo_pagado', False))
        self.texto_busqueda_var.set(filters_dict.get('texto_busqueda', ''))
    
    def enable_controls(self, enabled: bool = True):
        """
        Habilita o deshabilita los controles
        
        Args:
            enabled: True para habilitar, False para deshabilitar
        """
        state = "normal" if enabled else "disabled"
        
        widgets_to_toggle = [
            self.fecha_inicial_entry,
            self.fecha_final_entry,
            self.tipo_combobox,
            self.proveedor_entry,
            self.no_vale_entry,
            self.texto_busqueda_entry,
            self.solo_cargado_check,
            self.solo_pagado_check,
            self.buscar_btn,
            self.limpiar_btn
        ]
        
        for widget in widgets_to_toggle:
            widget.config(state=state)
    
    def focus_search_entry(self):
        """Pone el foco en el campo de búsqueda de texto"""
        self.texto_busqueda_entry.focus()
    
    def get_frame(self):
        """Retorna el frame principal"""
        return self.main_frame
