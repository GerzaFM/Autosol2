"""
Vista para el frame de búsqueda y filtros - Aplicación de Cheques
Adaptado de buscar_app_refactored
"""
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from typing import Dict, Any, Callable, Optional
import logging
from datetime import datetime

# Importar componentes de búsqueda desde solicitudapp
try:
    import sys
    import os
    solicitudapp_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'solicitudapp')
    sys.path.insert(0, solicitudapp_path)
    from search_components import SearchEntry
    SEARCH_ENTRY_AVAILABLE = True
except Exception as e:
    SearchEntry = None
    SEARCH_ENTRY_AVAILABLE = False


class SearchFrame:
    """Frame que contiene los controles de búsqueda para la aplicación de cheques"""
    
    def __init__(self, parent, search_callback: Callable, clear_callback: Callable):
        self.parent = parent
        self.search_callback = search_callback
        self.clear_callback = clear_callback
        self.logger = logging.getLogger(__name__)
        
        # Variables de búsqueda
        self.solo_pagado_var = ttk.BooleanVar()
        self.solo_cargado_var = ttk.BooleanVar()
        self.no_vale_var = ttk.StringVar()
        self.clase_var = ttk.StringVar()
        self.texto_busqueda_var = ttk.StringVar()
        
        # Datos para componentes de búsqueda
        self.proveedores_data = []
        self.tipos_data = []
        
        # Referencias a widgets
        self.proveedor_search_widget = None
        self.tipo_search = None
        
        # Crear frame principal
        self.main_frame = ttk.Frame(parent)
        self._create_widgets()
    
    def _create_widgets(self):
        """Crea los controles de búsqueda"""
        # Frame principal de filtros
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
        ttk.Label(row1_frame, text="Tipo Vale:  ", font=("Segoe UI", 10)).pack(side="left", padx=(0, 5))
        
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
            # Configurar fuente blanca para mejor contraste
            self.tipo_search.entry.configure(foreground="white")
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
        
        # No Vale
        ttk.Label(row1_frame, text="No Vale:", font=("Segoe UI", 10)).pack(side="left", padx=(0, 5))
        self.no_vale_entry = ttk.Entry(
            row1_frame,
            textvariable=self.no_vale_var,
            font=("Segoe UI", 11),
            width=15
        )
        self.no_vale_entry.pack(side="left", padx=(0, 15))
        
        # Solo Cargada (primera fila)
        self.solo_cargado_check = ttk.Checkbutton(
            row1_frame,
            text="Solo Cargado",
            variable=self.solo_cargado_var,
            bootstyle="success-round-toggle"
        )
        self.solo_cargado_check.pack(side="left", padx=(0, 15))
        
        # Segunda fila de filtros
        row2_frame = ttk.Frame(filters_main)
        row2_frame.pack(fill="x", pady=(0, 10))
        
        # Fecha Final (segunda fila)
        ttk.Label(row2_frame, text="Fecha Final:  ", font=("Segoe UI", 10)).pack(side="left", padx=(0, 5))
        self.fecha_final_entry = ttk.DateEntry(
            row2_frame,
            dateformat='%Y-%m-%d',
            width=12
        )
        self.fecha_final_entry.pack(side="left", padx=(0, 15))
        
        # Proveedor (en segunda fila)
        ttk.Label(row2_frame, text="Proveedor:", font=("Segoe UI", 10)).pack(side="left", padx=(0, 5))
        
        if SEARCH_ENTRY_AVAILABLE and SearchEntry is not None:
            self.proveedor_search_widget = SearchEntry(
                parent=row2_frame,
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
            # Configurar fuente blanca para mejor contraste
            self.proveedor_search_widget.entry.configure(foreground="white")
            self.proveedor_search_widget.pack(side="left", padx=(0, 15), fill="x", expand=False)
        else:
            # Fallback al combobox anterior
            self.proveedor_entry = ttk.Entry(row2_frame, width=25)
            self.proveedor_entry.pack(side="left", padx=(0, 15))
        
        # Clase (a la derecha del proveedor, debajo de No Vale)
        ttk.Label(row2_frame, text="Clase:    ", font=("Segoe UI", 10)).pack(side="left", padx=(0, 5))
        self.clase_entry = ttk.Entry(
            row2_frame,
            textvariable=self.clase_var,
            font=("Segoe UI", 11),
            width=15
        )
        self.clase_entry.pack(side="left", padx=(0, 15))
        
        # Solo Pagada (segunda fila, a la derecha de clase)
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
            bootstyle="success",  # Verde
            command=self.search_callback,
            width=15
        )
        self.buscar_btn.pack(side="right", padx=(10, 0))
        
        self.limpiar_btn = ttk.Button(
            row2_frame,
            text="Limpiar Filtros",
            bootstyle="danger",  # Rojo
            command=self.clear_callback,
            width=15
        )
        self.limpiar_btn.pack(side="right", padx=(10, 0))
        
        # Tercera fila - Búsqueda de texto
        row3_frame = ttk.Frame(filters_main)
        row3_frame.pack(fill="x", pady=(0, 10))
        
        # Búsqueda de texto
        ttk.Label(row3_frame, text="Buscar texto:", font=("Segoe UI", 10)).pack(side="left", padx=(0, 5))
        self.texto_busqueda_entry = ttk.Entry(
            row3_frame,
            textvariable=self.texto_busqueda_var,
            font=("Segoe UI", 11),
            width=30
        )
        self.texto_busqueda_entry.pack(side="left", padx=(0, 15))
    
    def get_filters(self) -> Dict[str, Any]:
        """
        Obtiene los valores actuales de todos los filtros
        
        Returns:
            Dict con los valores de los filtros
        """
        filters = {}
        
        try:
            # Fechas
            fecha_inicial = self.fecha_inicial_entry.entry.get()
            fecha_final = self.fecha_final_entry.entry.get()
            
            filters['fecha_inicio'] = datetime.strptime(fecha_inicial, '%Y-%m-%d').date() if fecha_inicial else None
            filters['fecha_fin'] = datetime.strptime(fecha_final, '%Y-%m-%d').date() if fecha_final else None
            
            # Tipo de vale
            if SEARCH_ENTRY_AVAILABLE and self.tipo_search:
                selected_tipo = self.tipo_search.get_selected_item()
                filters['tipo_filtro'] = selected_tipo.get('clave', '') if selected_tipo else ''
            else:
                filters['tipo_filtro'] = getattr(self, 'tipo_var', ttk.StringVar()).get()
            
            # No Vale
            filters['no_vale_filtro'] = self.no_vale_var.get().strip()
            
            # Proveedor
            if SEARCH_ENTRY_AVAILABLE and self.proveedor_search_widget:
                selected_proveedor = self.proveedor_search_widget.get_selected_item()
                filters['proveedor_filtro'] = selected_proveedor.get('nombre', '') if selected_proveedor else ''
            else:
                filters['proveedor_filtro'] = getattr(self.proveedor_entry, 'get', lambda: '')()
            
            # Clase
            filters['clase_filtro'] = self.clase_var.get().strip()
            
            # Texto de búsqueda
            filters['texto_busqueda'] = self.texto_busqueda_var.get().strip()
            
            # Checkboxes
            filters['solo_cargadas'] = self.solo_cargado_var.get()
            filters['solo_pagadas'] = self.solo_pagado_var.get()
            
        except Exception as e:
            self.logger.error(f"Error obteniendo filtros: {e}")
            # Retornar filtros vacíos en caso de error
            filters = {
                'fecha_inicio': None,
                'fecha_fin': None,
                'tipo_filtro': '',
                'no_vale_filtro': '',
                'proveedor_filtro': '',
                'clase_filtro': '',
                'texto_busqueda': '',
                'solo_cargadas': False,
                'solo_pagadas': False
            }
        
        return filters
    
    def clear_filters(self):
        """Limpia todos los filtros"""
        try:
            # Limpiar fechas
            self.fecha_inicial_entry.entry.delete(0, 'end')
            self.fecha_final_entry.entry.delete(0, 'end')
            
            # Limpiar tipo de vale
            if SEARCH_ENTRY_AVAILABLE and self.tipo_search:
                self.tipo_search.clear_selection()
            else:
                if hasattr(self, 'tipo_var'):
                    self.tipo_var.set('')
            
            # Limpiar No Vale
            self.no_vale_var.set('')
            
            # Limpiar proveedor
            if SEARCH_ENTRY_AVAILABLE and self.proveedor_search_widget:
                self.proveedor_search_widget.clear_selection()
            else:
                if hasattr(self, 'proveedor_entry'):
                    self.proveedor_entry.delete(0, 'end')
            
            # Limpiar clase
            self.clase_var.set('')
            
            # Limpiar búsqueda de texto
            self.texto_busqueda_var.set('')
            
            # Limpiar checkboxes
            self.solo_cargado_var.set(False)
            self.solo_pagado_var.set(False)
            
            self.logger.info("Filtros limpiados")
            
        except Exception as e:
            self.logger.error(f"Error limpiando filtros: {e}")
    
    def set_tipos_data(self, tipos_data):
        """
        Establece los datos de tipos de vale
        
        Args:
            tipos_data: Lista de diccionarios con datos de tipos
        """
        self.tipos_data = tipos_data or []
        if SEARCH_ENTRY_AVAILABLE and self.tipo_search:
            self.tipo_search.set_items(self.tipos_data)
            self.logger.info(f"Datos de tipos actualizados: {len(self.tipos_data)} tipos")
    
    def set_proveedores_data(self, proveedores_data):
        """
        Establece los datos de proveedores
        
        Args:
            proveedores_data: Lista de diccionarios con datos de proveedores
        """
        self.proveedores_data = proveedores_data or []
        if SEARCH_ENTRY_AVAILABLE and self.proveedor_search_widget:
            self.proveedor_search_widget.set_items(self.proveedores_data)
            self.logger.info(f"Datos de proveedores actualizados: {len(self.proveedores_data)} proveedores")
