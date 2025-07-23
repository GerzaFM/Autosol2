"""
Aplicación de búsqueda de facturas - Maneja la lógica principal de búsqueda y listado de facturas.
"""
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import ttk
from typing import Optional, List, Dict, Any
import logging

# Importar modelos de base de datos
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from bd.models import Factura, Proveedor, Layout, Concepto, db
    from bd.bd_control import DBManager as BdControl
    from solicitudapp.config.app_config import AppConfig
    
    # Intentar importar SearchEntry desde la ruta actual
    try:
        from search_components import SearchEntry
        print("✅ SearchEntry importado correctamente")
    except ImportError:
        # Si no se encuentra, intentar desde buscarapp
        try:
            from buscarapp.search_components import SearchEntry
            print("✅ SearchEntry importado desde buscarapp")
        except ImportError:
            # Si tampoco funciona, intentar ruta absoluta
            try:
                current_dir = os.path.dirname(__file__)
                components_path = os.path.join(current_dir, 'search_components.py')
                if os.path.exists(components_path):
                    import importlib.util
                    spec = importlib.util.spec_from_file_location("search_components", components_path)
                    search_components_module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(search_components_module)
                    SearchEntry = search_components_module.SearchEntry
                    print("✅ SearchEntry importado mediante ruta absoluta")
                else:
                    SearchEntry = None
                    print("❌ search_components.py no encontrado")
            except Exception as e:
                SearchEntry = None
                print(f"❌ Error cargando SearchEntry: {e}")
                
except ImportError as e:
    print(f"Error importando modelos: {e}")
    Factura = None
    BdControl = None
    AppConfig = None
    SearchEntry = None

class BuscarApp(tb.Frame):
    """
    Aplicación principal para búsqueda y listado de facturas.
    """
    
    def __init__(self, master=None, **kwargs):
        """
        Inicializa la aplicación de búsqueda.
        
        Args:
            master: Widget padre
        """
        super().__init__(master, **kwargs)
        
        # Variables de control
        self.facturas_data: List[Dict[str, Any]] = []
        self.filtered_data: List[Dict[str, Any]] = []
        self.proveedores_data: List[Dict[str, Any]] = []  # Datos de proveedores para búsqueda
        self.bd_control = None
        
        # Referencias a widgets
        self.search_var = tb.StringVar()
        self.proveedor_search_widget = None
        self.solo_pagado_var = tb.BooleanVar()
        self.solo_cargado_var = tb.BooleanVar()
        self.treeview: Optional[ttk.Treeview] = None
        self.status_label: Optional[tb.Label] = None
        
        self._initialize_db()
        self._create_layout()
        self._load_facturas()
        self._load_proveedores()  # Cargar proveedores para el filtro
    
    def _initialize_db(self):
        """Inicializa la conexión a la base de datos."""
        try:
            if BdControl is not None and Factura is not None:
                # Buscar la base de datos en la raíz del proyecto
                db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'facturas.db')
                db_path = os.path.abspath(db_path)
                
                if os.path.exists(db_path):
                    print(f"Base de datos encontrada en: {db_path}")
                    
                    # Inicializar la conexión con la ruta correcta
                    from bd.models import db as database
                    database.init(db_path)
                    
                    self.bd_control = BdControl()
                    print("Base de datos conectada correctamente")
                    
                    # Verificar que hay datos
                    try:
                        count = Factura.select().count()
                        print(f"Facturas encontradas en la BD: {count}")
                        if count == 0:
                            print("La base de datos está vacía")
                    except Exception as e:
                        print(f"Error al contar facturas: {e}")
                else:
                    print("No se encontró el archivo de base de datos en la raíz del proyecto")
                    self.bd_control = None
                    
            else:
                print("Modelos de BD no disponibles")
        except Exception as e:
            print(f"Error al conectar base de datos: {e}")
            self.bd_control = None
    
    def _create_layout(self):
        """Crea el layout de la aplicación."""
        # Frame principal con padding
        main_frame = tb.Frame(self, padding=20)
        main_frame.pack(fill=BOTH, expand=True)
        
        # Frame superior con controles de búsqueda
        search_frame = tb.Frame(main_frame)
        search_frame.pack(fill=X, pady=(0, 15))
        
        self._create_search_controls(search_frame)
        
        # Frame para la tabla
        table_frame = tb.Frame(main_frame)
        table_frame.pack(fill=BOTH, expand=True, pady=(0, 10))
        
        self._create_table(table_frame)
        
        # Frame inferior con botones y estado
        bottom_frame = tb.Frame(main_frame)
        bottom_frame.pack(fill=X)
        
        self._create_bottom_controls(bottom_frame)
    
    def _create_search_controls(self, parent):
        """Crea los controles de búsqueda y filtros."""
        # Frame principal de filtros con padding
        filters_main = tb.Frame(parent)
        filters_main.pack(fill=X, pady=10)
        
        # Primera fila de filtros
        row1_frame = tb.Frame(filters_main)
        row1_frame.pack(fill=X, pady=(0, 10))
        
        # Fecha Inicial
        tb.Label(row1_frame, text="Fecha Inicial:", font=("Segoe UI", 10)).pack(side=LEFT, padx=(0, 5))
        fecha_inicial_entry = tb.DateEntry(
            row1_frame,
            dateformat='%Y-%m-%d',
            width=12
        )
        fecha_inicial_entry.pack(side=LEFT, padx=(0, 15))
        self.fecha_inicial_entry = fecha_inicial_entry  # Guardar referencia
        
        # Fecha Final
        tb.Label(row1_frame, text="Fecha Final:", font=("Segoe UI", 10)).pack(side=LEFT, padx=(0, 5))
        fecha_final_entry = tb.DateEntry(
            row1_frame,
            dateformat='%Y-%m-%d',
            width=12
        )
        fecha_final_entry.pack(side=LEFT, padx=(0, 15))
        self.fecha_final_entry = fecha_final_entry  # Guardar referencia
        
        # Tipo de Vale
        tb.Label(row1_frame, text="Tipo:", font=("Segoe UI", 10)).pack(side=LEFT, padx=(0, 5))
        
        if SearchEntry is not None:
            # Crear datos para SearchEntry de tipos de vale
            tipos_data = []
            if AppConfig and hasattr(AppConfig, 'TIPO_VALE'):
                for k, v in AppConfig.TIPO_VALE.items():
                    tipos_data.append({"value": k, "descripcion": v})
            
            # Crear SearchEntry para tipos de vale
            self.tipo_search = SearchEntry(
                parent=row1_frame,
                items=tipos_data,
                search_fields=["value", "descripcion"],
                display_columns=[
                    {"name": "value", "text": "Tipo", "width": 80},
                    {"name": "descripcion", "text": "Descripción", "width": 200}
                ],
                entity_type="Tipo de Vale",
                placeholder_text="Seleccionar tipo...",
                width=25
            )
            self.tipo_search.pack(side=LEFT, padx=(0, 15))
        else:
            # Fallback: usar Combobox tradicional
            # Crear lista de tipos de vale desde la configuración
            tipos_vale = [""]  # Opción vacía para "todos"
            if AppConfig and hasattr(AppConfig, 'TIPO_VALE'):
                tipos_vale.extend([f"{k} - {v}" for k, v in AppConfig.TIPO_VALE.items()])
            
            self.tipo_var = tb.StringVar()
            tipo_combo = tb.Combobox(
                row1_frame,
                textvariable=self.tipo_var,
                values=tipos_vale,
                width=25,
                state="readonly"
            )
            tipo_combo.pack(side=LEFT, padx=(0, 15))
        
        # Proveedor
        tb.Label(row1_frame, text="Proveedor:", font=("Segoe UI", 10)).pack(side=LEFT, padx=(0, 5))
        
        # Widget de búsqueda de proveedor
        if SearchEntry is not None:
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
            self.proveedor_search_widget.pack(side=LEFT, padx=(0, 15), fill=X, expand=False)
        else:
            # Fallback al combobox anterior si no se puede importar el componente
            proveedor_combo = tb.Combobox(
                row1_frame,
                width=25
            )
            proveedor_combo.pack(side=LEFT, padx=(0, 15))
            self.proveedor_combo = proveedor_combo
        
        # Segunda fila - Checkboxes y controles
        row2_frame = tb.Frame(filters_main)
        row2_frame.pack(fill=X, pady=(0, 10))
        
        # Solo Cargado
        solo_cargado_check = tb.Checkbutton(
            row2_frame,
            text="Solo Cargado",
            variable=self.solo_cargado_var,
            bootstyle="success-round-toggle"
        )
        solo_cargado_check.pack(side=LEFT, padx=(0, 15))
        
        # Solo Pagado
        solo_pagado_check = tb.Checkbutton(
            row2_frame,
            text="Solo Pagado",
            variable=self.solo_pagado_var,
            bootstyle="info-round-toggle"
        )
        solo_pagado_check.pack(side=LEFT, padx=(0, 15))
        
        # Espaciador
        spacer = tb.Frame(row2_frame)
        spacer.pack(side=LEFT, fill=X, expand=True)
        
        # Botones de acción
        tb.Button(
            row2_frame,
            text="Buscar",
            bootstyle="primary",
            command=self._apply_filters
        ).pack(side=RIGHT, padx=(10, 0))
        
        tb.Button(
            row2_frame,
            text="Limpiar Filtros",
            bootstyle="secondary-outline",
            command=self._clear_filters
        ).pack(side=RIGHT, padx=(10, 0))
        
        tb.Button(
            row2_frame,
            text="Actualizar",
            bootstyle="info-outline",
            command=self._load_facturas
        ).pack(side=RIGHT, padx=(10, 0))
        
        # Tercera fila - Búsqueda de texto
        row3_frame = tb.Frame(filters_main)
        row3_frame.pack(fill=X)
        
        # Campo de búsqueda general
        tb.Label(row3_frame, text="Buscar:", font=("Segoe UI", 10)).pack(side=LEFT, padx=(0, 5))
        search_entry = tb.Entry(
            row3_frame,
            textvariable=self.search_var,
            font=("Segoe UI", 11),
            width=40
        )
        search_entry.pack(side=LEFT, padx=(0, 10))
        
        # Información de resultados
        self.results_label = tb.Label(
            row3_frame,
            text="",
            font=("Segoe UI", 10),
            bootstyle="inverse-secondary"
        )
        self.results_label.pack(side=RIGHT)
    
    def _create_table(self, parent):
        """Crea la tabla de facturas."""
        # Frame contenedor con scrollbars
        table_container = tb.Frame(parent)
        table_container.pack(fill=BOTH, expand=True)
        
        # Definir columnas
        columns = ("folio_interno", "tipo", "fecha", "nombre_emisor", "conceptos", "total", "clase", "cargada", "pagada")
        column_widths = {
            "folio_interno": 80, 
            "tipo": 60, 
            "fecha": 100, 
            "nombre_emisor": 160, 
            "conceptos": 300, 
            "total": 100,
            "clase": 120,
            "cargada": 80,
            "pagada": 80
        }
        column_names = {
            "folio_interno": "ID",
            "tipo": "Tipo",
            "fecha": "Fecha",
            "nombre_emisor": "Emisor",
            "conceptos": "Conceptos",
            "total": "Total",
            "clase": "Clase",
            "cargada": "Cargada",
            "pagada": "Pagada"
        }
        
        # Crear Treeview
        self.treeview = ttk.Treeview(
            table_container,
            columns=columns,
            show='headings',
            height=7
        )
        
        # Configurar columnas
        for col in columns:
            self.treeview.heading(col, text=column_names[col])
            self.treeview.column(col, width=column_widths.get(col, 100), minwidth=60)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(table_container, orient=VERTICAL, command=self.treeview.yview)
        h_scrollbar = ttk.Scrollbar(table_container, orient=HORIZONTAL, command=self.treeview.xview)
        
        self.treeview.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Posicionar elementos
        self.treeview.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        # Configurar grid
        table_container.grid_rowconfigure(0, weight=1)
        table_container.grid_columnconfigure(0, weight=1)
        
        # Eventos
        self.treeview.bind('<Double-1>', self._on_double_click)
        self.treeview.bind('<ButtonRelease-1>', self._on_select)
    
    def _create_bottom_controls(self, parent):
        """Crea los controles inferiores."""
        # Frame izquierdo con botones de acción
        left_frame = tb.Frame(parent)
        left_frame.pack(side=LEFT)
        
        # Botones de acción
        view_button = tb.Button(
            left_frame,
            text="Ver Detalles",
            bootstyle="info",
            command=self._view_details,
            state="disabled"
        )
        view_button.pack(side=LEFT, padx=(0, 10))
        self.view_button = view_button
        
        export_button = tb.Button(
            left_frame,
            text="Exportar",
            bootstyle="success-outline",
            command=self._export_selected,
            state="disabled"
        )
        export_button.pack(side=LEFT, padx=(0, 10))
        self.export_button = export_button
        
        delete_button = tb.Button(
            left_frame,
            text="Eliminar",
            bootstyle="danger-outline",
            command=self._delete_selected,
            state="disabled"
        )
        delete_button.pack(side=LEFT)
        self.delete_button = delete_button
        
        # Frame derecho con información de estado
        right_frame = tb.Frame(parent)
        right_frame.pack(side=RIGHT)
        
        self.status_label = tb.Label(
            right_frame,
            text="Especifique filtros para buscar facturas",
            font=("Segoe UI", 10),
            bootstyle="inverse-secondary"
        )
        self.status_label.pack()
    
    def _load_facturas(self):
        """Carga todas las facturas desde la base de datos."""
        try:
            print("Cargando facturas desde la base de datos...")
            
            if not self.bd_control or Factura is None:
                print("Base de datos no disponible, usando datos de ejemplo")
                self.facturas_data = self._get_sample_data()
                self.filtered_data = []  # Empezar con lista vacía
                self._update_table()
                self._update_status("Base de datos no disponible. Use los filtros para buscar.")
                return
            else:
                # Consultar todas las facturas con información del proveedor y conceptos
                facturas_query = (Factura
                                .select()
                                .join(Proveedor, on=(Factura.proveedor == Proveedor.id))
                                .order_by(Factura.fecha.desc()))
                
                self.facturas_data = []
                for factura in facturas_query:
                    # Manejar la fecha de forma segura
                    fecha_str = factura.fecha
                    if hasattr(factura.fecha, 'strftime'):
                        # Es un objeto date/datetime
                        fecha_str = factura.fecha.strftime('%Y-%m-%d')
                    elif isinstance(factura.fecha, str):
                        # Ya es string, usarlo tal como está
                        fecha_str = factura.fecha
                    else:
                        # Fallback
                        fecha_str = str(factura.fecha)
                    
                    # Obtener conceptos de la factura
                    conceptos_list = []
                    try:
                        conceptos = list(factura.conceptos)
                        for concepto in conceptos:
                            conceptos_list.append(concepto.descripcion)
                    except Exception as e:
                        print(f"Error al obtener conceptos para factura {factura.folio_interno}: {e}")
                        conceptos_list = ["Sin conceptos"]
                    
                    # Unir conceptos con "/" y limitar longitud
                    conceptos_str = " / ".join(conceptos_list) if conceptos_list else "Sin conceptos"
                    if len(conceptos_str) > 100:  # Limitar a 100 caracteres
                        conceptos_str = conceptos_str[:97] + "..."
                    
                    # Convertir booleanos a texto legible
                    cargada_str = "Sí" if factura.cargada else "No"
                    pagada_str = "Sí" if factura.pagada else "No"
                    
                    self.facturas_data.append({
                        'folio_interno': factura.folio_interno,
                        'serie': factura.serie,
                        'folio': factura.folio,
                        'serie_folio': f"{factura.serie}-{factura.folio}",
                        'tipo': factura.tipo,
                        'clase': factura.clase or "",  # Agregar campo clase con valor por defecto
                        'fecha': fecha_str,
                        'nombre_emisor': factura.nombre_emisor,
                        'nombre_receptor': factura.nombre_receptor,
                        'conceptos': conceptos_str,
                        'total': f"${factura.total:,.2f}",
                        'cargada': cargada_str,
                        'pagada': pagada_str,
                        'rfc_emisor': factura.rfc_emisor,
                        'rfc_receptor': factura.rfc_receptor,
                        'subtotal': factura.subtotal,
                        'iva_trasladado': factura.iva_trasladado,
                        'cargada_bool': factura.cargada,  # Mantener el valor booleano original
                        'pagada_bool': factura.pagada     # Mantener el valor booleano original
                    })
            
            self.filtered_data = []  # Empezar con lista vacía
            self._update_table()
            self._update_status(f"Se cargaron {len(self.facturas_data)} facturas. Use los filtros para buscar.")
            
        except Exception as e:
            print(f"Error al cargar facturas: {e}")
            import traceback
            traceback.print_exc()
            self._update_status("Error al cargar facturas")
            # Usar datos de ejemplo en caso de error
            self.facturas_data = self._get_sample_data()
            self.filtered_data = []  # Empezar con lista vacía incluso con datos de ejemplo
            self._update_table()
    
    def _load_proveedores(self):
        """Carga la lista de proveedores para el filtro."""
        try:
            if self.bd_control and Proveedor is not None:
                proveedores = list(Proveedor.select().order_by(Proveedor.nombre))
                
                # Convertir a formato para SearchEntry
                self.proveedores_data = []
                for p in proveedores:
                    proveedor_data = {
                        'id': p.id,
                        'nombre': p.nombre,
                        'rfc': p.rfc,
                        'telefono': p.telefono or '',
                        'email': p.email or '',
                        'nombre_contacto': p.nombre_contacto or ''
                    }
                    self.proveedores_data.append(proveedor_data)
                
                # Actualizar el widget de búsqueda si existe
                if self.proveedor_search_widget:
                    self.proveedor_search_widget.set_items(self.proveedores_data)
                
                # Mantener compatibilidad con el combobox si existe
                if hasattr(self, 'proveedor_combo'):
                    proveedores_nombres = [""] + [p.nombre for p in proveedores]
                    self.proveedor_combo['values'] = proveedores_nombres
            else:
                # Datos de ejemplo si no hay BD
                self.proveedores_data = [
                    {'id': 1, 'nombre': 'ABC Proveedores', 'rfc': 'ABC123456789', 'telefono': '555-1234', 'email': 'contacto@abc.com', 'nombre_contacto': 'Juan Pérez'},
                    {'id': 2, 'nombre': 'XYZ Servicios', 'rfc': 'XYZ987654321', 'telefono': '555-5678', 'email': 'info@xyz.com', 'nombre_contacto': 'María González'},
                    {'id': 3, 'nombre': 'Proveedores Varios', 'rfc': 'VAR456789123', 'telefono': '555-9012', 'email': 'ventas@varios.com', 'nombre_contacto': 'Carlos López'}
                ]
                
                if self.proveedor_search_widget:
                    self.proveedor_search_widget.set_items(self.proveedores_data)
                
                if hasattr(self, 'proveedor_combo'):
                    self.proveedor_combo['values'] = ["", "ABC Proveedores", "XYZ Servicios", "Proveedores Varios"]
                    
        except Exception as e:
            print(f"Error cargando proveedores: {e}")
            self.proveedores_data = []
            if hasattr(self, 'proveedor_combo'):
                self.proveedor_combo['values'] = [""]
    
    def _apply_filters(self):
        """Aplica todos los filtros seleccionados."""
        try:
            # Aplicar filtros sobre los datos originales
            filtered_data = []
            
            fecha_inicial = self.fecha_inicial_entry.entry.get().strip() if hasattr(self, 'fecha_inicial_entry') else ""
            fecha_final = self.fecha_final_entry.entry.get().strip() if hasattr(self, 'fecha_final_entry') else ""
            
            # Obtener tipo seleccionado desde SearchEntry o ComboBox
            tipo_filtro = ""
            if hasattr(self, 'tipo_search') and self.tipo_search:
                selected_tipo = self.tipo_search.get_selected_item()
                if selected_tipo:
                    tipo_filtro = selected_tipo.get('value', '')
            elif hasattr(self, 'tipo_var'):
                tipo_filtro_combo = self.tipo_var.get().strip()
                if tipo_filtro_combo and " - " in tipo_filtro_combo:
                    tipo_filtro = tipo_filtro_combo.split(" - ")[0]
                elif tipo_filtro_combo:
                    tipo_filtro = tipo_filtro_combo
            
            # Obtener proveedor seleccionado
            proveedor_filtro = ""
            if self.proveedor_search_widget:
                selected_proveedor = self.proveedor_search_widget.get_selected_item()
                if selected_proveedor:
                    proveedor_filtro = selected_proveedor.get('nombre', '')
            elif hasattr(self, 'proveedor_combo') and hasattr(self, 'proveedor_var'):
                proveedor_filtro = self.proveedor_var.get().strip()
                
            solo_cargado = self.solo_cargado_var.get()
            solo_pagado = self.solo_pagado_var.get()
            texto_busqueda = self.search_var.get().strip().lower()
            
            # Verificar si hay al menos un filtro activo
            has_filters = any([
                fecha_inicial, fecha_final, tipo_filtro, proveedor_filtro, 
                solo_cargado, solo_pagado, texto_busqueda
            ])
            
            if not has_filters:
                print("No hay filtros activos - no se mostrarán resultados")
                self.filtered_data = []
                self._update_table()
                self._update_status("Especifique al menos un filtro para buscar facturas")
                return
            
            print(f"DEBUG - Aplicando filtros:")
            print(f"  Fecha inicial: '{fecha_inicial}'")
            print(f"  Fecha final: '{fecha_final}'") 
            print(f"  Tipo: '{tipo_filtro}'")
            print(f"  Proveedor: '{proveedor_filtro}'")
            print(f"  Solo cargado: {solo_cargado}")
            print(f"  Solo pagado: {solo_pagado}")
            print(f"  Texto búsqueda: '{texto_busqueda}'")
            print(f"  Total facturas: {len(self.facturas_data)}")
            
            for i, factura in enumerate(self.facturas_data):
                include_factura = True
                exclusion_reason = ""
                
                # Filtro por fecha inicial - SOLO si se especifica fecha inicial
                if fecha_inicial and include_factura:
                    fecha_factura = factura.get('fecha', '')
                    if fecha_factura < fecha_inicial:
                        include_factura = False
                        exclusion_reason = f"fecha factura ({fecha_factura}) < fecha inicial ({fecha_inicial})"
                
                # Filtro por fecha final - SOLO si se especifica fecha final
                if fecha_final and include_factura:
                    fecha_factura = factura.get('fecha', '')
                    if fecha_factura > fecha_final:
                        include_factura = False
                        exclusion_reason = f"fecha factura ({fecha_factura}) > fecha final ({fecha_final})"
                
                # Filtro por tipo - SOLO si se especifica tipo
                if tipo_filtro and include_factura:
                    # Extraer el código del tipo si está en formato "CODE - DESCRIPTION"
                    tipo_codigo = tipo_filtro.split(' - ')[0] if ' - ' in tipo_filtro else tipo_filtro
                    
                    if factura.get('tipo', '') != tipo_codigo:
                        include_factura = False
                        exclusion_reason = f"tipo {factura.get('tipo', '')} != {tipo_codigo}"
                
                # Filtro por proveedor - SOLO si se especifica proveedor
                if proveedor_filtro and include_factura:
                    emisor = factura.get('nombre_emisor', '').lower()
                    if proveedor_filtro.lower() not in emisor:
                        include_factura = False
                        exclusion_reason = f"proveedor '{proveedor_filtro}' no encontrado en emisor '{emisor}'"
                
                # Filtro Solo Cargado - SOLO si el checkbox está marcado
                if solo_cargado and include_factura:
                    if not factura.get('cargada_bool', False):
                        include_factura = False
                        exclusion_reason = f"solo_cargado=True pero factura.cargada={factura.get('cargada_bool', False)}"
                
                # Filtro Solo Pagado - SOLO si el checkbox está marcado
                if solo_pagado and include_factura:
                    if not factura.get('pagada_bool', False):
                        include_factura = False
                        exclusion_reason = f"solo_pagado=True pero factura.pagada={factura.get('pagada_bool', False)}"
                
                # Filtro de búsqueda de texto - SOLO si hay texto de búsqueda
                if texto_busqueda and include_factura:
                    searchable_text = ' '.join([
                        str(factura.get("folio_interno", "")),
                        str(factura.get("serie_folio", "")),
                        str(factura.get("tipo", "")),
                        str(factura.get("nombre_emisor", "")),
                        str(factura.get("conceptos", "")),
                        str(factura.get("rfc_emisor", "")),
                        str(factura.get("rfc_receptor", ""))
                    ]).lower()
                    
                    if texto_busqueda not in searchable_text:
                        include_factura = False
                        exclusion_reason = f"texto '{texto_busqueda}' no encontrado"
                
                # Resultado final
                if include_factura:
                    filtered_data.append(factura)
                    print(f"  ✅ Factura {i+1} ({factura.get('serie_folio', '')}): INCLUIDA")
                else:
                    print(f"  ❌ Factura {i+1} ({factura.get('serie_folio', '')}): EXCLUIDA - {exclusion_reason}")
            
            self.filtered_data = filtered_data
            self._update_table()
            
            if len(filtered_data) == 0:
                self._update_status("No se encontraron facturas que coincidan con los filtros")
            else:
                self._update_status(f"Se encontraron {len(filtered_data)} facturas")
            
            print(f"✅ Filtros aplicados - {len(filtered_data)} resultados de {len(self.facturas_data)} totales")
            
        except Exception as e:
            print(f"Error aplicando filtros: {e}")
            import traceback
            traceback.print_exc()
    
    def _clear_filters(self):
        """Limpia todos los filtros."""
        if hasattr(self, 'fecha_inicial_entry'):
            self.fecha_inicial_entry.entry.delete(0, 'end')
        if hasattr(self, 'fecha_final_entry'):
            self.fecha_final_entry.entry.delete(0, 'end')
        
        # Limpiar tipo
        if hasattr(self, 'tipo_search') and self.tipo_search:
            self.tipo_search.clear_selection()
        elif hasattr(self, 'tipo_var'):
            self.tipo_var.set("")
        
        # Limpiar proveedor
        if self.proveedor_search_widget:
            self.proveedor_search_widget.clear_selection()
        elif hasattr(self, 'proveedor_combo') and hasattr(self, 'proveedor_var'):
            self.proveedor_var.set("")
        
        self.solo_cargado_var.set(False)
        self.solo_pagado_var.set(False)
        self.search_var.set("")
        
        # Mantener lista vacía después de limpiar
        self.filtered_data = []
        self._update_table()
        self._update_status("Filtros limpiados. Especifique filtros para buscar facturas.")
        print("Filtros limpiados - lista vacía")
    
    def _get_sample_data(self) -> List[Dict[str, Any]]:
        """Obtiene datos de ejemplo cuando la BD no está disponible."""
        return [
            {
                "folio_interno": 1,
                "serie": 1,
                "folio": 1001,
                "serie_folio": "1-1001",
                "tipo": "I",
                "clase": "Servicios",
                "fecha": "2024-01-15",
                "nombre_emisor": "Proveedor ABC S.A. de C.V.",
                "nombre_receptor": "Mi Empresa S.A.",
                "conceptos": "Servicio de consultoría / Capacitación técnica",
                "total": "$1,250.00",
                "cargada": "Sí",
                "pagada": "No",
                "rfc_emisor": "ABC123456789",
                "rfc_receptor": "EMP987654321",
                "cargada_bool": True,
                "pagada_bool": False
            },
            {
                "folio_interno": 2,
                "serie": 1,
                "folio": 1002,
                "serie_folio": "1-1002",
                "tipo": "E",
                "clase": "Materiales",
                "fecha": "2024-01-16",
                "nombre_emisor": "Servicios XYZ Corp.",
                "nombre_receptor": "Mi Empresa S.A.",
                "conceptos": "Materiales de oficina / Suministros de computación",
                "total": "$2,340.50",
                "cargada": "No",
                "pagada": "Sí",
                "rfc_emisor": "XYZ123456789",
                "rfc_receptor": "EMP987654321",
                "cargada_bool": False,
                "pagada_bool": True
            }
        ]
    
    def _search_facturas(self):
        """Realiza la búsqueda de facturas."""
        self._apply_filters()
    
    def _clear_search(self):
        """Limpia la búsqueda - ahora redirige a _clear_filters.""" 
        self._clear_filters()
    
    def _update_table(self):
        """Actualiza la tabla con los datos filtrados."""
        # Limpiar tabla
        for item in self.treeview.get_children():
            self.treeview.delete(item)
        
        # Insertar datos filtrados
        for factura in self.filtered_data:
            self.treeview.insert('', END, values=(
                factura.get("folio_interno", ""),
                factura.get("tipo", ""),
                factura.get("fecha", ""),
                factura.get("nombre_emisor", ""),
                factura.get("conceptos", ""),
                factura.get("total", ""),
                factura.get("clase", ""),
                factura.get("cargada", ""),
                factura.get("pagada", "")
            ))
        
        # Actualizar contador de resultados
        self.results_label.config(text=f"{len(self.filtered_data)} resultados")
    
    def _on_select(self, event):
        """Maneja la selección de elementos en la tabla."""
        selection = self.treeview.selection()
        
        # Habilitar/deshabilitar botones según la selección
        if selection:
            self.view_button.config(state="normal")
            self.export_button.config(state="normal")
            self.delete_button.config(state="normal")
        else:
            self.view_button.config(state="disabled")
            self.export_button.config(state="disabled")
            self.delete_button.config(state="disabled")
    
    def _on_double_click(self, event):
        """Maneja el doble click en la tabla."""
        self._view_details()
    
    def _view_details(self):
        """Muestra los detalles de la factura seleccionada."""
        selection = self.treeview.selection()
        if not selection:
            return
        
        item = self.treeview.item(selection[0])
        values = item['values']
        
        # Buscar la factura completa
        folio_interno = values[0]
        factura_completa = None
        
        for factura in self.filtered_data:
            if str(factura.get("folio_interno")) == str(folio_interno):
                factura_completa = factura
                break
        
        if factura_completa:
            # Crear ventana de detalles
            self._show_details_window(factura_completa)
        
        print(f"Ver detalles de factura ID: {folio_interno}")
    
    def _show_details_window(self, factura):
        """Muestra una ventana con los detalles de la factura."""
        # Crear ventana secundaria
        details_window = tb.Toplevel(self)
        details_window.title(f"Detalles - Factura {factura.get('serie_folio', 'N/A')}")
        details_window.geometry("500x400")
        details_window.transient(self)
        details_window.grab_set()
        
        # Frame principal
        main_frame = tb.Frame(details_window, padding=20)
        main_frame.pack(fill=BOTH, expand=True)
        
        # Título
        title_label = tb.Label(
            main_frame,
            text=f"Factura {factura.get('serie_folio', 'N/A')}",
            font=("Segoe UI", 16, "bold"),
            bootstyle="inverse-primary"
        )
        title_label.pack(pady=(0, 20))
        
        # Frame de detalles
        details_frame = tb.Frame(main_frame)
        details_frame.pack(fill=BOTH, expand=True)
        
        # Información básica
        details_info = [
            ("ID Interno:", factura.get('folio_interno', 'N/A')),
            ("Serie-Folio:", factura.get('serie_folio', 'N/A')),
            ("Fecha:", factura.get('fecha', 'N/A')),
            ("Emisor:", factura.get('nombre_emisor', 'N/A')),
            ("RFC Emisor:", factura.get('rfc_emisor', 'N/A')),
            ("Receptor:", factura.get('nombre_receptor', 'N/A')),
            ("RFC Receptor:", factura.get('rfc_receptor', 'N/A')),
            ("Proveedor:", factura.get('proveedor', 'N/A')),
            ("Subtotal:", factura.get('subtotal', 'N/A')),
            ("IVA:", factura.get('iva_trasladado', 'N/A')),
            ("Total:", factura.get('total', 'N/A')),
            ("Tipo:", factura.get('tipo', 'N/A')),
            ("Cargada:", factura.get('cargada', 'N/A')),
            ("Pagada:", factura.get('pagada', 'N/A'))
        ]
        
        for i, (label, value) in enumerate(details_info):
            row_frame = tb.Frame(details_frame)
            row_frame.pack(fill=X, pady=2)
            
            label_widget = tb.Label(
                row_frame,
                text=label,
                font=("Segoe UI", 10, "bold"),
                width=15,
                anchor="w"
            )
            label_widget.pack(side=LEFT)
            
            value_widget = tb.Label(
                row_frame,
                text=str(value),
                font=("Segoe UI", 10),
                anchor="w"
            )
            value_widget.pack(side=LEFT, fill=X, expand=True)
        
        # Botón cerrar
        close_button = tb.Button(
            main_frame,
            text="Cerrar",
            bootstyle="secondary",
            command=details_window.destroy
        )
        close_button.pack(pady=(20, 0))
    
    def _export_selected(self):
        """Exporta la factura seleccionada."""
        selection = self.treeview.selection()
        if not selection:
            return
        
        item = self.treeview.item(selection[0])
        values = item['values']
        
        factura_id = values[0]  # El ID está en la primera columna
        
        # Buscar la factura completa para obtener serie-folio
        factura_completa = None
        for factura in self.filtered_data:
            if str(factura.get("folio_interno")) == str(factura_id):
                factura_completa = factura
                break
        
        serie_folio = factura_completa.get('serie_folio', 'N/A') if factura_completa else 'N/A'
        
        print(f"Exportar factura ID: {factura_id}")
        tb.dialogs.Messagebox.show_info(
            title="Exportar",
            message=f"Funcionalidad de exportación para factura {serie_folio}\n(Por implementar)",
            parent=self
        )
    
    def _delete_selected(self):
        """Elimina la factura seleccionada."""
        selection = self.treeview.selection()
        if not selection:
            tb.dialogs.Messagebox.show_warning(
                title="Sin selección",
                message="Por favor seleccione una factura para eliminar.",
                parent=self
            )
            return

        item = self.treeview.item(selection[0])
        values = item['values']
        
        if not values or len(values) < 2:
            tb.dialogs.Messagebox.show_error(
                title="Error",
                message="No se pudo obtener la información de la factura seleccionada.",
                parent=self
            )
            return
        
        factura_id = values[0]  # El ID está en la primera columna
        
        # Buscar la factura completa para obtener serie-folio
        factura_completa = None
        for factura in self.filtered_data:
            if str(factura.get("folio_interno")) == str(factura_id):
                factura_completa = factura
                break
        
        serie_folio = factura_completa.get('serie_folio', 'N/A') if factura_completa else 'N/A'

        # Confirmar eliminación
        result = tb.dialogs.Messagebox.yesno(
            title="Confirmar eliminación",
            message=f"¿Está seguro de que desea eliminar la factura {serie_folio}?\n\n"
                   f"Esta acción eliminará:\n"
                   f"• La factura y todos sus datos\n"
                   f"• Los conceptos asociados\n"
                   f"• Los repartos relacionados (si existen)\n"
                   f"• Los vales relacionados (si existen)\n\n"
                   f"Esta acción NO se puede deshacer.",
            parent=self
        )

        if result == "Yes":
            try:
                # Verificar que tenemos acceso a la base de datos
                if not self.bd_control:
                    tb.dialogs.Messagebox.show_error(
                        title="Error de base de datos",
                        message="No hay conexión a la base de datos.",
                        parent=self
                    )
                    return
                
                # Eliminar la factura
                success = self.bd_control.eliminar_factura(factura_id)
                
                if success:
                    # Mostrar mensaje de éxito
                    tb.dialogs.Messagebox.show_info(
                        title="Eliminación exitosa",
                        message=f"La factura {serie_folio} ha sido eliminada correctamente.",
                        parent=self
                    )
                    
                    # Actualizar la lista de facturas
                    self._load_facturas()
                    
                    # Reaplicar filtros para actualizar la vista
                    if hasattr(self, 'fecha_inicial_entry') and self.fecha_inicial_entry.entry.get().strip():
                        self._apply_filters()
                    else:
                        # Si no hay filtros, mantener la lista vacía
                        self.filtered_data = []
                        self._update_table()
                        self._update_status("Factura eliminada. Especifique filtros para buscar facturas.")
                    
                    # Deshabilitar botón eliminar ya que no hay selección
                    self.delete_button.config(state="disabled")
                    if hasattr(self, 'export_button'):
                        self.export_button.config(state="disabled")
                        
                else:
                    tb.dialogs.Messagebox.show_error(
                        title="Error al eliminar",
                        message=f"No se pudo eliminar la factura {serie_folio}.\n"
                               f"Verifique los logs para más detalles.",
                        parent=self
                    )
                    
            except Exception as e:
                print(f"Error eliminando factura: {e}")
                import traceback
                traceback.print_exc()
                
                tb.dialogs.Messagebox.show_error(
                    title="Error inesperado",
                    message=f"Ocurrió un error inesperado al eliminar la factura:\n{str(e)}",
                    parent=self
                )
    
    def _update_status(self, message: str):
        """Actualiza el mensaje de estado."""
        if self.status_label:
            self.status_label.config(text=message)


def main():
    """Función principal para ejecutar la aplicación independientemente."""
    try:
        root = tb.Window(themename="cosmo")
        root.title("Búsqueda de Facturas")
        root.geometry("1200x700")
        
        app = BuscarApp(root)
        app.pack(fill="both", expand=True)
        
        root.mainloop()
        
    except Exception as e:
        print(f"Error ejecutando aplicación: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
