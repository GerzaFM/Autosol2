"""
Vista para el frame de búsqueda y filtros - VERSIÓN CORREGIDA
Copia exacta de la funcionalidad original de buscar_app.py
"""
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from typing import Dict, Any, Callable, Optional
import logging
from datetime import datetime

# Importar componentes de búsqueda
try:
    from ..search_components import SearchEntry
    SEARCH_ENTRY_AVAILABLE = True
except ImportError:
    try:
        # Intento directo desde el mismo directorio padre
        import sys
        import os
        parent_dir = os.path.dirname(os.path.dirname(__file__))
        sys.path.insert(0, parent_dir)
        from search_components import SearchEntry
        SEARCH_ENTRY_AVAILABLE = True
    except ImportError:
        try:
            # Última opción: importar desde solicitudapp
            solicitudapp_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'solicitudapp')
            sys.path.insert(0, solicitudapp_path)
            from search_components import SearchEntry
            SEARCH_ENTRY_AVAILABLE = True
        except Exception as e:
            SearchEntry = None
            SEARCH_ENTRY_AVAILABLE = False

class SearchFrame:
    """Frame que contiene los controles de búsqueda - COPIA EXACTA DE LA ORIGINAL"""
    
    def __init__(self, parent, on_search_callback: Callable, on_clear_callback: Callable):
        self.parent = parent
        self.on_search_callback = on_search_callback
        self.on_clear_callback = on_clear_callback
        self.logger = logging.getLogger(__name__)
        
        # Variables de búsqueda - EXACTO COMO EN ORIGINAL
        self.search_var = ttk.StringVar()
        self.solo_pagado_var = ttk.BooleanVar()
        self.solo_cargado_var = ttk.BooleanVar()
        self.no_vale_var = ttk.StringVar()
        self.texto_busqueda_var = ttk.StringVar()
        
        # Datos para componentes de búsqueda
        self.proveedores_data = []
        self.tipos_data = []
        
        # Referencias a widgets
        self.proveedor_search_widget = None
        self.tipo_search = None
        
        # Crear frame principal (FRAME NORMAL, NO LABELFRAME)
        self.main_frame = ttk.Frame(parent)
        self.main_frame.pack(fill="x", padx=5, pady=5)
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Crea los controles de búsqueda - COPIA EXACTA DE buscar_app.py"""
        # Frame principal de filtros con padding
        filters_main = ttk.Frame(self.main_frame)
        filters_main.pack(fill="x", pady=10)
        
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
        
        # Tipo de Vale
        ttk.Label(row1_frame, text="Tipo:", font=("Segoe UI", 10)).pack(side="left", padx=(0, 5))
        
        if SEARCH_ENTRY_AVAILABLE and SearchEntry is not None:
            # Usar SearchEntry para tipos de vale
            self.tipo_search = SearchEntry(
                parent=row1_frame,
                items=self.tipos_data,
                search_fields=["clave", "descripcion"],
                display_columns=[
                    {"name": "clave", "text": "Clave", "width": 80},
                    {"name": "descripcion", "text": "Descripción", "width": 200}
                ],
                entity_type="Tipo de Vale",
                placeholder_text="Seleccionar tipo...",
                width=25
            )
            self.tipo_search.pack(side="left", padx=(0, 15))
        else:
            # Fallback: usar Combobox tradicional
            self.tipo_var = ttk.StringVar()
            self.tipo_combobox = ttk.Combobox(
                row1_frame,
                textvariable=self.tipo_var,
                values=[""],
                width=25,
                state="readonly"
            )
            self.tipo_combobox.pack(side="left", padx=(0, 15))
        
        # Proveedor
        ttk.Label(row1_frame, text="Proveedor:", font=("Segoe UI", 10)).pack(side="left", padx=(0, 5))
        
        if SEARCH_ENTRY_AVAILABLE and SearchEntry is not None:
            self.proveedor_search_widget = SearchEntry(
                parent=row1_frame,
                items=self.proveedores_data,
                search_fields=['nombre', 'rfc'],
                display_columns=[
                    {'name': 'nombre', 'text': 'Nombre', 'width': 200},
                    {'name': 'rfc', 'text': 'RFC', 'width': 120},
                    {'name': 'telefono', 'text': 'Teléfono', 'width': 100},
                    {'name': 'email', 'text': 'Email', 'width': 150}
                ],
                entity_type="Proveedor",
                placeholder_text="Seleccionar proveedor...",
                width=25
            )
            self.proveedor_search_widget.pack(side="left", padx=(0, 15), fill="x", expand=False)
        else:
            # Fallback al combobox anterior
            self.proveedor_entry = ttk.Entry(row1_frame, width=25)
            self.proveedor_entry.pack(side="left", padx=(0, 15))
        
        # No Vale
        ttk.Label(row1_frame, text="No Vale:", font=("Segoe UI", 10)).pack(side="left", padx=(0, 5))
        self.no_vale_entry = ttk.Entry(
            row1_frame,
            textvariable=self.no_vale_var,
            font=("Segoe UI", 11),
            width=15
        )
        self.no_vale_entry.pack(side="left", padx=(0, 15))
        
        # Segunda fila - Fecha Final, Checkboxes y controles
        row2_frame = ttk.Frame(filters_main)
        row2_frame.pack(fill="x", pady=(0, 10))
        
        # Fecha Final
        ttk.Label(row2_frame, text="Fecha Final:  ", font=("Segoe UI", 10)).pack(side="left", padx=(0, 5))
        self.fecha_final_entry = ttk.DateEntry(
            row2_frame,
            dateformat='%Y-%m-%d',
            width=12
        )
        self.fecha_final_entry.pack(side="left", padx=(0, 15))
        
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
            bootstyle="primary",
            command=self._on_search_clicked
        )
        self.buscar_btn.pack(side="right", padx=(10, 0))
        
        self.limpiar_btn = ttk.Button(
            row2_frame,
            text="Limpiar Filtros",
            bootstyle="secondary-outline",
            command=self._on_clear_clicked
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
        
        # Label de estado (sin texto inicial)
        self.status_label = ttk.Label(
            row3_frame,
            text="",
            font=("Segoe UI", 10),
            bootstyle="info"
        )
        self.status_label.pack(side="left", padx=(10, 0))
    
    def _on_search_clicked(self):
        """Maneja el click del botón buscar"""
        filters = self.get_filters()
        self.on_search_callback(filters)
    
    def _on_clear_clicked(self):
        """Maneja el click del botón limpiar"""
        self.clear_filters()
        self.on_clear_callback()
    
    def get_filters(self) -> Dict[str, Any]:
        """Obtiene los filtros actuales"""
        # Obtener valor del tipo
        tipo_filtro = ""
        if hasattr(self, 'tipo_search') and self.tipo_search:
            selected_tipo = self.tipo_search.get_selected_item()
            if selected_tipo:
                tipo_filtro = selected_tipo.get('clave', '')
        elif hasattr(self, 'tipo_var'):
            tipo_filtro = self.tipo_var.get()
        
        # Obtener valor del proveedor
        proveedor_filtro = ""
        if hasattr(self, 'proveedor_search_widget') and self.proveedor_search_widget:
            selected_proveedor = self.proveedor_search_widget.get_selected_item()
            if selected_proveedor:
                proveedor_filtro = selected_proveedor.get('nombre', '')
        elif hasattr(self, 'proveedor_entry'):
            proveedor_filtro = self.proveedor_entry.get()
        
        return {
            'fecha_inicial': self.fecha_inicial_entry.entry.get(),
            'fecha_final': self.fecha_final_entry.entry.get(),
            'tipo_filtro': tipo_filtro,
            'proveedor_filtro': proveedor_filtro,
            'no_vale_filtro': self.no_vale_var.get(),
            'solo_cargado': self.solo_cargado_var.get(),
            'solo_pagado': self.solo_pagado_var.get(),
            'texto_busqueda': self.texto_busqueda_var.get()
        }
    
    def clear_filters(self):
        """Limpia todos los filtros"""
        self.fecha_inicial_entry.entry.delete(0, 'end')
        self.fecha_final_entry.entry.delete(0, 'end')
        
        if hasattr(self, 'tipo_search') and self.tipo_search:
            self.tipo_search.clear_selection()
        elif hasattr(self, 'tipo_var'):
            self.tipo_var.set("")
        
        if hasattr(self, 'proveedor_search_widget') and self.proveedor_search_widget:
            self.proveedor_search_widget.clear_selection()
        elif hasattr(self, 'proveedor_entry'):
            self.proveedor_entry.delete(0, 'end')
        
        self.no_vale_var.set("")
        self.solo_cargado_var.set(False)
        self.solo_pagado_var.set(False)
        self.texto_busqueda_var.set("")
    
    def set_proveedores_data(self, proveedores: list):
        """Actualiza los datos de proveedores"""
        self.proveedores_data = proveedores
        if hasattr(self, 'proveedor_search_widget') and self.proveedor_search_widget:
            self.proveedor_search_widget.update_items(proveedores)
    
    def set_tipos_data(self, tipos: list):
        """Actualiza los datos de tipos"""
        self.tipos_data = tipos
        if hasattr(self, 'tipo_search') and self.tipo_search:
            self.tipo_search.update_items(tipos)
    
    def set_status(self, message: str, style: str = "info"):
        """Establece el mensaje de estado"""
        if hasattr(self, 'status_label'):
            self.status_label.config(text=message, bootstyle=style)
    
    def enable_controls(self, enabled: bool = True):
        """Habilita o deshabilita los controles"""
        state = "normal" if enabled else "disabled"
        
        # Widgets que soportan la opción 'state'
        entry_widgets = [
            self.fecha_inicial_entry.entry,
            self.fecha_final_entry.entry,
            self.no_vale_entry,
            self.texto_busqueda_entry,
            self.buscar_btn,
            self.limpiar_btn
        ]
        
        for widget in entry_widgets:
            try:
                widget.config(state=state)
            except Exception:
                pass
        
        # Manejar tipo combobox si existe
        if hasattr(self, 'tipo_combobox'):
            try:
                self.tipo_combobox.config(state="readonly" if enabled else "disabled")
            except Exception:
                pass
        
        # Manejar proveedor entry si existe
        if hasattr(self, 'proveedor_entry'):
            try:
                self.proveedor_entry.config(state=state)
            except Exception:
                pass
    
    def get_frame(self):
        """Retorna el frame principal"""
        return self.main_frame
