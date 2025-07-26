"""
Aplicación de búsqueda de facturas - Maneja la lógica principal de búsqueda y listado de facturas.
"""
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import ttk
from typing import Optional, List, Dict, Any
import logging
import traceback
import os
from datetime import datetime
from tkinter import filedialog

# Importar modelos de base de datos
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from bd.models import Factura, Proveedor, Layout, Concepto, Vale, OrdenCompra, Banco, Reparto, db
    from bd.bd_control import DBManager as BdControl
    from solicitudapp.config.app_config import AppConfig
    from solicitudapp.form_control import FormPDF
    
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
        self.using_sample_data = False  # Bandera para distinguir datos de ejemplo
        
        # Referencias a widgets
        self.search_var = tb.StringVar()
        self.proveedor_search_widget = None
        self.solo_pagado_var = tb.BooleanVar()
        self.solo_cargado_var = tb.BooleanVar()
        self.treeview: Optional[ttk.Treeview] = None
        
        # Referencias a labels de paneles de información
        self.proveedor_codigo_label = None
        self.proveedor_nombre_label = None
        self.proveedor_rfc_label = None
        self.proveedor_email_label = None
        self.vale_no_label = None
        self.vale_tipo_label = None
        self.vale_folio_label = None
        self.orden_importe_label = None
        self.orden_iva_label = None
        self.orden_letras_label = None
        self.orden_cuenta_label = None
        self.orden_banco_label = None
        
        self._initialize_db()
        self._create_layout()
        # Cargar datos automáticamente al iniciar
        self._load_facturas()  # Cargar facturas al inicio
        self._load_proveedores()  # Cargar proveedores para el filtro
    
    def _format_folio(self, serie, folio):
        """Formatea el folio con serie y número, usando espacio como separador."""
        if serie and serie.strip():
            return f"{serie} {folio}"
        else:
            return str(folio)
    
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
        
        # Frame debajo del tree
        below_tree_frame = tb.Frame(main_frame)
        below_tree_frame.pack(fill=X, pady=(0, 10))
        
        self._create_below_tree_controls(below_tree_frame)
        
        # Frame de información de factura seleccionada
        info_frame = tb.Frame(main_frame)
        info_frame.pack(fill=X, pady=(0, 10))
        
        self._create_info_panels(info_frame)
    
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
        
        # No Vale
        tb.Label(row1_frame, text="No Vale:", font=("Segoe UI", 10)).pack(side=LEFT, padx=(0, 5))
        self.no_vale_var = tb.StringVar()
        no_vale_entry = tb.Entry(
            row1_frame,
            textvariable=self.no_vale_var,
            font=("Segoe UI", 11),
            width=15
        )
        no_vale_entry.pack(side=LEFT, padx=(0, 15))
        
        # Segunda fila - Fecha Final, Checkboxes y controles
        row2_frame = tb.Frame(filters_main)
        row2_frame.pack(fill=X, pady=(0, 10))
        
        # Fecha Final
        tb.Label(row2_frame, text="Fecha Final:  ", font=("Segoe UI", 10)).pack(side=LEFT, padx=(0, 5))
        fecha_final_entry = tb.DateEntry(
            row2_frame,
            dateformat='%Y-%m-%d',
            width=12
        )
        fecha_final_entry.pack(side=LEFT, padx=(0, 15))
        self.fecha_final_entry = fecha_final_entry  # Guardar referencia
        
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
        columns = ("folio_interno", "tipo", "no_vale", "fecha", "folio_xml", "nombre_emisor", "conceptos", "total", "clase", "cargada", "pagada")
        column_widths = {
            "folio_interno": 80, 
            "tipo": 60,
            "no_vale": 80,
            "fecha": 100,
            "folio_xml": 100,
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
            "no_vale": "No Vale",
            "fecha": "Fecha",
            "folio_xml": "Folio",
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
    
    def _create_below_tree_controls(self, parent):
        """Crea los controles que van debajo del treeview."""
        # Frame contenedor con padding
        controls_frame = tb.Frame(parent, padding=10)
        controls_frame.pack(fill=X)
        
        # Frame izquierdo para controles adicionales
        left_controls = tb.Frame(controls_frame)
        left_controls.pack(side=LEFT)
        
        # Frame derecho para botones de acción
        right_controls = tb.Frame(controls_frame)
        right_controls.pack(side=RIGHT)
        
        # Botones de acción en el orden solicitado (todos con el mismo ancho)
        button_width = 12  # Ancho uniforme para todos los botones
        
        cargado_button = tb.Button(
            right_controls,
            text="Cargado",
            bootstyle="primary",
            command=self._toggle_cargado,
            state="disabled",
            width=button_width
        )
        cargado_button.pack(side=RIGHT, padx=(10, 0))
        self.cargado_button = cargado_button
        
        detalles_button = tb.Button(
            right_controls,
            text="Detalles",
            bootstyle="primary",
            command=self._view_details,
            state="disabled",
            width=button_width
        )
        detalles_button.pack(side=RIGHT, padx=(10, 0))
        self.view_button = detalles_button  # Mantener la referencia original
        
        modificar_button = tb.Button(
            right_controls,
            text="Modificar",
            bootstyle="primary",
            command=self._modify_selected,
            state="disabled",
            width=button_width
        )
        modificar_button.pack(side=RIGHT, padx=(10, 0))
        self.modificar_button = modificar_button
        
        export_button = tb.Button(
            right_controls,
            text="Exportar",
            bootstyle="primary",
            command=self._export_selected,
            state="disabled",
            width=button_width
        )
        export_button.pack(side=RIGHT, padx=(10, 0))
        self.export_button = export_button
        
        # Botón Autocarga
        autocarga_button = tb.Button(
            right_controls,
            text="Autocarga",
            bootstyle="primary",
            command=self._autocarga_selected,
            state="disabled",
            width=button_width
        )
        autocarga_button.pack(side=RIGHT, padx=(10, 0))
        self.autocarga_button = autocarga_button
        
        # Botón Reimprimir
        reimprimir_button = tb.Button(
            right_controls,
            text="Reimprimir",
            bootstyle="primary",
            command=self._reimprimir_selected,
            state="disabled",
            width=button_width
        )
        reimprimir_button.pack(side=RIGHT, padx=(10, 0))
        self.reimprimir_button = reimprimir_button
    
    def _load_facturas(self):
        """Carga todas las facturas desde la base de datos."""
        try:
            print("Cargando facturas desde la base de datos...")
            
            if not self.bd_control or Factura is None:
                print("Base de datos no disponible")
                self.facturas_data = []
                self.filtered_data = []
                self.using_sample_data = False
                self._update_table()
                # Deshabilitar botones de acción cuando no hay datos
                self._disable_action_buttons()
                return
            else:
                # Verificar primero si hay facturas en la base de datos
                facturas_count = Factura.select().count()
                if facturas_count == 0:
                    print("No hay facturas en la base de datos")
                    self.facturas_data = []
                    self.using_sample_data = False  # No son datos de ejemplo, es BD real vacía
                    self.filtered_data = self.facturas_data.copy()
                    self._update_table()
                    return
                
                # Consultar todas las facturas con información del proveedor
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
                    
                    # Obtener el número de vale si existe
                    no_vale_str = ""
                    try:
                        if hasattr(factura, 'vale') and factura.vale:
                            no_vale_str = factura.vale.noVale
                        else:
                            # Si no hay vale asociado, intentar obtenerlo directamente
                            vale_asociado = Vale.select().where(Vale.factura_id == factura.folio_interno).first()
                            if vale_asociado:
                                no_vale_str = vale_asociado.noVale
                    except Exception as e:
                        print(f"Error al obtener vale para factura {factura.folio_interno}: {e}")
                        no_vale_str = ""
                    
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
                        'serie_folio': self._format_folio(factura.serie, factura.folio),
                        'tipo': factura.tipo,
                        'no_vale': no_vale_str,  # Usar el noVale del vale asociado
                        'clase': factura.clase or "",  # Agregar campo clase con valor por defecto
                        'fecha': fecha_str,
                        'folio_xml': self._format_folio(factura.serie, factura.folio),  # Folio del XML
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
            
            self.using_sample_data = False  # Marcar que estamos usando datos reales
            # No mostrar datos automáticamente, esperar a que el usuario haga búsqueda
            self.filtered_data = []  # Iniciar con tabla vacía
            self._update_table()
            
        except Exception as e:
            print(f"Error al cargar facturas: {e}")
            import traceback
            traceback.print_exc()
            # En caso de error, no mostrar datos
            self.facturas_data = []
            self.filtered_data = []
            self.using_sample_data = False
            self._update_table()
            # Deshabilitar botones de acción cuando no hay datos
            self._disable_action_buttons()
    
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
            
            # Obtener número de vale
            no_vale_filtro = self.no_vale_var.get().strip() if hasattr(self, 'no_vale_var') else ""
                
            solo_cargado = self.solo_cargado_var.get()
            solo_pagado = self.solo_pagado_var.get()
            texto_busqueda = self.search_var.get().strip().lower()
            
            # Verificar si hay al menos un filtro activo
            has_filters = any([
                fecha_inicial, fecha_final, tipo_filtro, proveedor_filtro, no_vale_filtro,
                solo_cargado, solo_pagado, texto_busqueda
            ])
            
            if not has_filters:
                print("No hay filtros activos - mostrando todas las facturas")
                # Mostrar todas las facturas
                self.filtered_data = self.facturas_data.copy()
                self._update_table()
                return
            
            print(f"DEBUG - Aplicando filtros:")
            print(f"  Fecha inicial: '{fecha_inicial}'")
            print(f"  Fecha final: '{fecha_final}'") 
            print(f"  Tipo: '{tipo_filtro}'")
            print(f"  Proveedor: '{proveedor_filtro}'")
            print(f"  No Vale: '{no_vale_filtro}'")
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
                
                # Filtro por número de vale - SOLO si se especifica número
                if no_vale_filtro and include_factura:
                    no_vale_factura = str(factura.get('no_vale', ''))
                    folio_interno = str(factura.get('folio_interno', ''))
                    serie_folio = str(factura.get('serie_folio', ''))
                    folio = str(factura.get('folio', ''))
                    
                    # Buscar en no_vale, folio interno, serie-folio, o folio individual
                    if (no_vale_filtro not in no_vale_factura and 
                        no_vale_filtro not in folio_interno and 
                        no_vale_filtro not in serie_folio and 
                        no_vale_filtro not in folio):
                        include_factura = False
                        exclusion_reason = f"número de vale '{no_vale_filtro}' no encontrado en no_vale ({no_vale_factura}), folio_interno ({folio_interno}), serie_folio ({serie_folio}), o folio ({folio})"
                
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
        
        # Limpiar No Vale
        if hasattr(self, 'no_vale_var'):
            self.no_vale_var.set("")
        
        self.solo_cargado_var.set(False)
        self.solo_pagado_var.set(False)
        self.search_var.set("")
        
        # Limpiar tabla después de quitar filtros
        self.filtered_data = []
        self._update_table()
        print("Filtros limpiados - tabla vacía")
    
    def _search_facturas(self):
        """Realiza la búsqueda de facturas."""
        self._apply_filters()
    
    def _clear_search(self):
        """Limpia la búsqueda - ahora redirige a _clear_filters.""" 
        self._clear_filters()
    
    def _select_all(self):
        """Selecciona todos los elementos en la tabla."""
        for item in self.treeview.get_children():
            self.treeview.selection_add(item)
        self._update_selection_info()
    
    def _deselect_all(self):
        """Deselecciona todos los elementos en la tabla."""
        self.treeview.selection_set([])
        self._update_selection_info()
        # Deshabilitar botones cuando no hay selección
        if hasattr(self, 'cargado_button'):
            self.cargado_button.config(state="disabled")
        if hasattr(self, 'view_button'):
            self.view_button.config(state="disabled")
        if hasattr(self, 'modificar_button'):
            self.modificar_button.config(state="disabled")
        if hasattr(self, 'export_button'):
            self.export_button.config(state="disabled")
        if hasattr(self, 'autocarga_button'):
            self.autocarga_button.config(state="disabled")
        if hasattr(self, 'reimprimir_button'):
            self.reimprimir_button.config(state="disabled")
    
    def _update_selection_info(self):
        """Actualiza la información de elementos seleccionados."""
        selected_count = len(self.treeview.selection())
        total_count = len(self.filtered_data)
        
        if selected_count > 0:
            print(f"Seleccionados: {selected_count} de {total_count} elementos")
        
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
                factura.get("no_vale", ""),
                factura.get("fecha", ""),
                factura.get("folio_xml", ""),
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
        
        # Habilitar/deshabilitar botones según la selección y tipo de datos
        if selection and self.bd_control and not self.using_sample_data:
            # Solo habilitar si hay conexión a BD real Y no estamos usando datos de ejemplo
            self._enable_action_buttons_on_selection()
            
            # Actualizar paneles de información con la factura seleccionada
            item = self.treeview.item(selection[0])
            values = item['values']
            if values:
                folio_interno = values[0]
                self._update_info_panels(folio_interno)
        else:
            # Deshabilitar si no hay selección, no hay BD real, o estamos usando datos de ejemplo
            self.view_button.config(state="disabled")
            self.export_button.config(state="disabled")
            if hasattr(self, 'cargado_button'):
                self.cargado_button.config(state="disabled")
            if hasattr(self, 'modificar_button'):
                self.modificar_button.config(state="disabled")
            if hasattr(self, 'autocarga_button'):
                self.autocarga_button.config(state="disabled")
            # Limpiar paneles de información
            self._clear_info_panels()
    
    def _on_double_click(self, event):
        """Maneja el doble click en la tabla."""
        self._view_details()
    
    def _enable_action_buttons_on_selection(self):
        """Habilita los botones de acción cuando hay una selección válida."""
        if hasattr(self, 'cargado_button'):
            self.cargado_button.config(state="normal")
        if hasattr(self, 'view_button'):
            self.view_button.config(state="normal")
        if hasattr(self, 'modificar_button'):
            self.modificar_button.config(state="normal")
        if hasattr(self, 'export_button'):
            self.export_button.config(state="normal")
        if hasattr(self, 'autocarga_button'):
            self.autocarga_button.config(state="normal")
        if hasattr(self, 'reimprimir_button'):
            self.reimprimir_button.config(state="normal")
    
    def _disable_action_buttons(self):
        """Deshabilita todos los botones de acción."""
        if hasattr(self, 'cargado_button'):
            self.cargado_button.config(state="disabled")
        if hasattr(self, 'view_button'):
            self.view_button.config(state="disabled")
        if hasattr(self, 'modificar_button'):
            self.modificar_button.config(state="disabled")
        if hasattr(self, 'export_button'):
            self.export_button.config(state="disabled")
        if hasattr(self, 'autocarga_button'):
            self.autocarga_button.config(state="disabled")
        if hasattr(self, 'reimprimir_button'):
            self.reimprimir_button.config(state="disabled")
    
    def _toggle_cargado(self):
        """Alterna el estado de cargado de la factura seleccionada."""
        selection = self.treeview.selection()
        if not selection:
            tb.dialogs.Messagebox.show_warning(
                title="Sin selección",
                message="Por favor seleccione una factura para cambiar su estado de cargado.",
                parent=self
            )
            return
        
        # Verificar si hay conexión a BD real
        if not self.bd_control or self.using_sample_data:
            tb.dialogs.Messagebox.show_info(
                title="Cambiar Estado Cargado",
                message="El cambio de estado de cargado solo está disponible con datos reales de la base de datos.",
                parent=self
            )
            return

        item = self.treeview.item(selection[0])
        values = item['values']
        folio_interno = values[0]
        
        try:
            # Obtener la factura de la base de datos
            factura = Factura.get_or_none(Factura.folio_interno == folio_interno)
            if not factura:
                tb.dialogs.Messagebox.show_error(
                    title="Error",
                    message="No se encontró la factura en la base de datos.",
                    parent=self
                )
                return
            
            # Verificar el estado actual
            current_status = factura.cargada
            nuevo_status = None
            
            if not current_status:  # Si está en "No" (False), cambiar a "Sí" (True)
                nuevo_status = True
                message = f"¿Desea marcar la factura {self._format_folio(factura.serie, factura.folio)} como CARGADA?"
                title = "Marcar como Cargada"
            else:  # Si está en "Sí" (True), preguntar si cambiar a "No" (False)
                message = f"La factura {self._format_folio(factura.serie, factura.folio)} está actualmente CARGADA.\n\n¿Desea cambiarla a NO CARGADA?"
                title = "Cambiar a No Cargada"
                nuevo_status = False
            
            # Confirmar el cambio
            result = tb.dialogs.Messagebox.yesno(
                title=title,
                message=message,
                parent=self
            )
            
            if result == "Yes":
                # Actualizar la base de datos
                factura.cargada = nuevo_status
                factura.save()
                
                # Actualizar los datos en memoria
                for factura_data in self.facturas_data:
                    if str(factura_data.get("folio_interno")) == str(folio_interno):
                        factura_data['cargada'] = "Sí" if nuevo_status else "No"
                        factura_data['cargada_bool'] = nuevo_status
                        break
                
                # Actualizar los datos filtrados si la factura está visible
                for factura_data in self.filtered_data:
                    if str(factura_data.get("folio_interno")) == str(folio_interno):
                        factura_data['cargada'] = "Sí" if nuevo_status else "No"
                        factura_data['cargada_bool'] = nuevo_status
                        break
                
                # Actualizar la tabla
                self._update_table()
                
                # Restaurar la selección
                for child in self.treeview.get_children():
                    item_values = self.treeview.item(child)['values']
                    if str(item_values[0]) == str(folio_interno):
                        self.treeview.selection_set(child)
                        self.treeview.focus(child)
                        break
                
        except Exception as e:
            print(f"Error al cambiar estado de cargado: {e}")
            import traceback
            traceback.print_exc()
            tb.dialogs.Messagebox.show_error(
                title="Error",
                message=f"Ocurrió un error al cambiar el estado de cargado:\n{str(e)}",
                parent=self
            )
    
    def _modify_selected(self):
        """Modifica la factura seleccionada."""
        selection = self.treeview.selection()
        if not selection:
            tb.dialogs.Messagebox.show_warning(
                title="Sin selección",
                message="Por favor seleccione una factura para modificar.",
                parent=self
            )
            return
        
        # Verificar si hay conexión a BD real
        if not self.bd_control or self.using_sample_data:
            tb.dialogs.Messagebox.show_info(
                title="Modificar Factura",
                message="La modificación solo está disponible con datos reales de la base de datos.",
                parent=self
            )
            return

        item = self.treeview.item(selection[0])
        values = item['values']
        folio_interno = values[0]
        
        # Placeholder: Funcionalidad por implementar
        tb.dialogs.Messagebox.show_info(
            title="Modificar Factura",
            message=f"Funcionalidad para modificar factura {folio_interno}\n(Por implementar)",
            parent=self
        )
    
    def _autocarga_selected(self):
        """Realiza autocarga de la factura seleccionada."""
        selection = self.treeview.selection()
        if not selection:
            tb.dialogs.Messagebox.show_warning(
                title="Sin selección",
                message="Por favor seleccione una factura para autocarga.",
                parent=self
            )
            return
        
        # Verificar si hay conexión a BD real
        if not self.bd_control or self.using_sample_data:
            tb.dialogs.Messagebox.show_info(
                title="Autocarga",
                message="La autocarga solo está disponible con datos reales de la base de datos.",
                parent=self
            )
            return

        item = self.treeview.item(selection[0])
        values = item['values']
        folio_interno = values[0]
        
        # Placeholder: Funcionalidad por implementar
        tb.dialogs.Messagebox.show_info(
            title="Autocarga",
            message=f"Funcionalidad de autocarga para factura {folio_interno}\n(Por implementar)",
            parent=self
        )
    
    def _reimprimir_selected(self):
        """Reimprimir la solicitud usando los datos de la base de datos."""
        selection = self.treeview.selection()
        if not selection:
            tb.dialogs.Messagebox.show_warning(
                title="Sin selección",
                message="Por favor seleccione una factura para reimprimir.",
                parent=self
            )
            return
        
        # Verificar si hay conexión a BD real
        if not self.bd_control or self.using_sample_data:
            tb.dialogs.Messagebox.show_info(
                title="Reimprimir Solicitud",
                message="La reimpresión solo está disponible con datos reales de la base de datos.",
                parent=self
            )
            return

        item = self.treeview.item(selection[0])
        values = item['values']
        folio_interno = values[0]
        
        try:
            # Obtener la factura de la base de datos
            factura = Factura.get_or_none(Factura.folio_interno == folio_interno)
            if not factura:
                tb.dialogs.Messagebox.show_error(
                    title="Error",
                    message="No se encontró la factura en la base de datos.",
                    parent=self
                )
                return
            
            # Obtener el proveedor
            proveedor = factura.proveedor
            
            # Obtener conceptos
            conceptos = list(factura.conceptos)
            conceptos_text = []
            for concepto in conceptos:
                conceptos_text.append(f"{concepto.cantidad} - {concepto.descripcion} - ${concepto.precio_unitario:,.2f}")
            
            # Obtener vale asociado si existe
            vale = None
            try:
                vale = Vale.get(Vale.factura_id == factura.folio_interno)
            except:
                pass
            
            # Obtener reparto asociado si existe
            reparto = None
            try:
                reparto = Reparto.get(Reparto.factura == factura)
            except:
                pass
            
            # Preparar los datos para el formulario PDF usando el mismo formato que solicitud_app_professional
            # Convertir el tipo de factura a formato "clave - valor"
            tipo_vale_formatted = ""
            if factura.tipo:
                # Importar AppConfig para obtener la descripción del tipo
                try:
                    from solicitudapp.config.app_config import AppConfig
                    if hasattr(AppConfig, 'TIPO_VALE') and factura.tipo in AppConfig.TIPO_VALE:
                        tipo_vale_formatted = f"{factura.tipo} - {AppConfig.TIPO_VALE[factura.tipo]}"
                    else:
                        tipo_vale_formatted = factura.tipo
                except:
                    tipo_vale_formatted = factura.tipo
            
            # Construir comentario con serie y folio de la factura (igual que solicitud_app_professional)
            serie_str = factura.serie or ""
            folio_str = factura.folio or ""
            
            # Construir el comentario evitando espacios dobles
            if serie_str and folio_str:
                comentario_factura = f"Factura: {serie_str} {folio_str}"
            elif serie_str:
                comentario_factura = f"Factura: {serie_str}"
            elif folio_str:
                comentario_factura = f"Factura: {folio_str}"
            else:
                comentario_factura = "Factura:"
            
            datos_formulario = {
                "TIPO DE VALE": tipo_vale_formatted,
                "C A N T I D A D": "\n".join([str(concepto.cantidad) for concepto in conceptos]),
                "C O M E N T A R I O S": comentario_factura,
                "Nombre de Empresa": proveedor.nombre if proveedor else "",
                "RFC": proveedor.rfc if proveedor else "",
                "Teléfono": proveedor.telefono if proveedor else "",
                "Correo": proveedor.email if proveedor else "",
                "Nombre Contacto": proveedor.nombre_contacto if proveedor else "",
                "Menudeo": str(reparto.comercial) if reparto and reparto.comercial else "",
                "Seminuevos": str(reparto.seminuevos) if reparto and reparto.seminuevos else "",
                "Flotas": str(reparto.fleet) if reparto and reparto.fleet else "",
                "Administración": str(reparto.administracion) if reparto and reparto.administracion else "",
                "Refacciones": str(reparto.refacciones) if reparto and reparto.refacciones else "",
                "Servicio": str(reparto.servicio) if reparto and reparto.servicio else "",
                "HYP": str(reparto.hyp) if reparto and reparto.hyp else "",
                "DESCRIPCIÓN": "\n".join([concepto.descripcion for concepto in conceptos]),
                "PRECIO UNITARIO": "\n".join([f"${concepto.precio_unitario:,.2f}" for concepto in conceptos]),
                "TOTAL": "\n".join([f"${concepto.total:,.2f}" for concepto in conceptos]),
                "FECHA GERENTE DE ÁREA": "",
                "FECHA GERENTE ADMINISTRATIVO": "",
                "FECHA DE AUTORIZACIÓN GG O DIRECTOR DE MARCA": "",
                "SUBTOTAL": f"${factura.subtotal:,.2f}" if factura.subtotal else "",
                "IVA": f"${factura.iva_trasladado:,.2f}" if factura.iva_trasladado else "",
                "TOTAL, SUMATORIA": f"${factura.total:,.2f}" if factura.total else "",
                "FECHA CREACIÓN SOLICITUD": factura.fecha.strftime('%d/%m/%Y') if hasattr(factura.fecha, 'strftime') else str(factura.fecha),
                "FOLIO": str(factura.folio_interno),
                "RETENCIÓN": f"${(factura.ret_iva or 0) + (factura.ret_isr or 0):,.2f}" if factura.ret_iva or factura.ret_isr else "",
                "Departamento": ""  # Este campo no está en el modelo Factura, se deja vacío
            }
            
            # Solicitar ubicación de guardado
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename_default = f"Solicitud_{factura.folio_interno}_{timestamp}.pdf"
            
            archivo_salida = filedialog.asksaveasfilename(
                title="Guardar solicitud reimpresa",
                defaultextension=".pdf",
                filetypes=[("Archivos PDF", "*.pdf")],
                initialfile=filename_default,
                parent=self
            )
            
            if archivo_salida:
                # Generar el PDF usando form_control
                form_pdf = FormPDF()
                form_pdf.rellenar(datos_formulario, archivo_salida)
                
                tb.dialogs.Messagebox.show_info(
                    title="Reimpresión Exitosa",
                    message=f"La solicitud se ha reimpreso correctamente en:\n{archivo_salida}",
                    parent=self
                )
            
        except Exception as e:
            print(f"Error al reimprimir solicitud: {e}")
            traceback.print_exc()
            tb.dialogs.Messagebox.show_error(
                title="Error",
                message=f"Ocurrió un error al reimprimir la solicitud:\n{str(e)}",
                parent=self
            )

    def _generate_cheque(self):
        """Genera información para cheque de la factura seleccionada."""
        selection = self.treeview.selection()
        if not selection:
            tb.dialogs.Messagebox.show_warning(
                title="Sin selección",
                message="Por favor seleccione una factura para generar cheque.",
                parent=self
            )
            return
        
        # Verificar si hay conexión a BD real
        if not self.bd_control or self.using_sample_data:
            tb.dialogs.Messagebox.show_info(
                title="Generar Cheque",
                message="La generación de cheques solo está disponible con datos reales de la base de datos.",
                parent=self
            )
            return

        item = self.treeview.item(selection[0])
        values = item['values']
        folio_interno = values[0]
        
        # Actualizar paneles de información
        self._update_info_panels(folio_interno)
        
        # Mensaje informativo
        tb.dialogs.Messagebox.show_info(
            title="Información de Cheque",
            message=f"Se ha actualizado la información para la factura {folio_interno}.\nRevise los paneles de información debajo.",
            parent=self
        )
    
    def _view_details(self):
        """Muestra los detalles de la factura seleccionada."""
        selection = self.treeview.selection()
        if not selection:
            return
        
        # Verificar si hay conexión a BD real y no estamos usando datos de ejemplo
        if not self.bd_control or self.using_sample_data:
            tb.dialogs.Messagebox.show_info(
                title="Vista de Detalles",
                message="La vista de detalles solo está disponible con datos reales de la base de datos.\n\nActualmente se están mostrando datos de ejemplo.",
                parent=self
            )
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
        
        # Verificar si hay conexión a BD real y no estamos usando datos de ejemplo
        if not self.bd_control or self.using_sample_data:
            tb.dialogs.Messagebox.show_info(
                title="Exportación",
                message="La exportación solo está disponible con datos reales de la base de datos.\n\nActualmente se están mostrando datos de ejemplo.",
                parent=self
            )
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
        
        # Verificar si hay conexión a BD real y no estamos usando datos de ejemplo
        if not self.bd_control or self.using_sample_data:
            tb.dialogs.Messagebox.show_info(
                title="Eliminación",
                message="La eliminación solo está disponible con datos reales de la base de datos.\n\nActualmente se están mostrando datos de ejemplo.",
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
    
    def _create_info_panels(self, parent):
        """Crea los paneles de información para cheques."""
        # Frame contenedor principal
        main_info_frame = tb.Frame(parent, padding=10)
        main_info_frame.pack(fill=X)
        
        # Crear tres LabelFrames horizontales
        
        # 1. Panel de Proveedor
        proveedor_frame = tb.LabelFrame(
            main_info_frame,
            text="Datos Proveedor",
            padding=10
        )
        proveedor_frame.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 5))
        
        # Campos del proveedor
        self.proveedor_codigo_label = tb.Label(
            proveedor_frame,
            text="Código: -",
            font=("Segoe UI", 10),
            anchor="w"
        )
        self.proveedor_codigo_label.pack(fill=X, pady=2)
        
        self.proveedor_nombre_label = tb.Label(
            proveedor_frame,
            text="Nombre: -",
            font=("Segoe UI", 10),
            anchor="w"
        )
        self.proveedor_nombre_label.pack(fill=X, pady=2)
        
        self.proveedor_rfc_label = tb.Label(
            proveedor_frame,
            text="RFC: -",
            font=("Segoe UI", 10),
            anchor="w"
        )
        self.proveedor_rfc_label.pack(fill=X, pady=2)
        
        self.proveedor_email_label = tb.Label(
            proveedor_frame,
            text="Email: -",
            font=("Segoe UI", 10),
            anchor="w"
        )
        self.proveedor_email_label.pack(fill=X, pady=2)
        
        # 2. Panel de Vale
        vale_frame = tb.LabelFrame(
            main_info_frame,
            text="Vale",
            padding=10
        )
        vale_frame.pack(side=LEFT, fill=BOTH, expand=True, padx=5)
        
        # Campos del vale
        self.vale_no_label = tb.Label(
            vale_frame,
            text="No Vale: -",
            font=("Segoe UI", 10),
            anchor="w"
        )
        self.vale_no_label.pack(fill=X, pady=2)
        
        self.vale_tipo_label = tb.Label(
            vale_frame,
            text="Tipo: -",
            font=("Segoe UI", 10),
            anchor="w"
        )
        self.vale_tipo_label.pack(fill=X, pady=2)
        
        self.vale_folio_label = tb.Label(
            vale_frame,
            text="Folio Factura: -",
            font=("Segoe UI", 10),
            anchor="w"
        )
        self.vale_folio_label.pack(fill=X, pady=2)
        
        # 3. Panel de Orden de Compra
        orden_frame = tb.LabelFrame(
            main_info_frame,
            text="Orden de Compra",
            padding=10
        )
        orden_frame.pack(side=LEFT, fill=BOTH, expand=True, padx=(5, 0))
        
        # Campos de la orden
        self.orden_importe_label = tb.Label(
            orden_frame,
            text="Importe: -",
            font=("Segoe UI", 10),
            anchor="w"
        )
        self.orden_importe_label.pack(fill=X, pady=2)
        
        self.orden_iva_label = tb.Label(
            orden_frame,
            text="IVA: -",
            font=("Segoe UI", 10),
            anchor="w"
        )
        self.orden_iva_label.pack(fill=X, pady=2)
        
        self.orden_letras_label = tb.Label(
            orden_frame,
            text="Importe en Letras: -",
            font=("Segoe UI", 10),
            anchor="w"
        )
        self.orden_letras_label.pack(fill=X, pady=2)
        
        self.orden_cuenta_label = tb.Label(
            orden_frame,
            text="Cuenta Mayor: -",
            font=("Segoe UI", 10),
            anchor="w"
        )
        self.orden_cuenta_label.pack(fill=X, pady=2)
        
        self.orden_banco_label = tb.Label(
            orden_frame,
            text="Banco Código: -",
            font=("Segoe UI", 10),
            anchor="w"
        )
        self.orden_banco_label.pack(fill=X, pady=2)
    
    def _update_info_panels(self, folio_interno):
        """Actualiza los paneles de información con datos de la factura."""
        try:
            if not self.bd_control:
                return
            
            # Obtener la factura
            factura = Factura.get_or_none(Factura.folio_interno == folio_interno)
            if not factura:
                self._clear_info_panels()
                return
            
            # 1. Actualizar datos del proveedor
            if factura.proveedor:
                proveedor = factura.proveedor
                self.proveedor_nombre_label.config(text=f"Nombre: {proveedor.nombre}")
                codigo_quiter = proveedor.codigo_quiter if proveedor.codigo_quiter else "N/A"
                self.proveedor_codigo_label.config(text=f"Código Quiter: {codigo_quiter}")
            else:
                self.proveedor_nombre_label.config(text="Nombre: Sin proveedor")
                self.proveedor_codigo_label.config(text="Código Quiter: -")
            
            # 2. Actualizar datos del vale
            vale = Vale.get_or_none(Vale.factura_id == factura.folio_interno)
            if vale:
                self.vale_no_label.config(text=f"No Vale: {vale.noVale}")
                self.vale_tipo_label.config(text=f"Tipo: {vale.tipo}")
                self.vale_folio_label.config(text=f"Folio Factura: {self._format_folio(factura.serie, factura.folio)}")
            else:
                self.vale_no_label.config(text="No Vale: Sin vale")
                self.vale_tipo_label.config(text="Tipo: -")
                self.vale_folio_label.config(text=f"Folio Factura: {self._format_folio(factura.serie, factura.folio)}")
            
            # 3. Actualizar datos de orden de compra
            orden = OrdenCompra.get_or_none(OrdenCompra.factura == factura.folio_interno)
            if orden:
                self.orden_importe_label.config(text=f"Importe: ${orden.importe:,.2f}")
                iva_text = f"${orden.iva:,.2f}" if orden.iva else "N/A"
                self.orden_iva_label.config(text=f"IVA: {iva_text}")
                self.orden_letras_label.config(text=f"Importe en Letras: {orden.importe_en_letras}")
                cuenta_mayor = orden.cuenta_mayor if orden.cuenta_mayor else "N/A"
                self.orden_cuenta_label.config(text=f"Cuenta Mayor: {cuenta_mayor}")
                
                # Buscar banco por cuenta
                banco = Banco.get_or_none(Banco.cuenta == str(orden.cuenta))
                if banco:
                    self.orden_banco_label.config(text=f"Banco Código: {banco.codigo}")
                else:
                    self.orden_banco_label.config(text="Banco Código: N/A")
            else:
                self.orden_importe_label.config(text="Importe: Sin orden")
                self.orden_iva_label.config(text="IVA: -")
                self.orden_letras_label.config(text="Importe en Letras: -")
                self.orden_cuenta_label.config(text="Cuenta Mayor: -")
                self.orden_banco_label.config(text="Banco Código: -")
                
        except Exception as e:
            print(f"Error actualizando paneles de información: {e}")
            import traceback
            traceback.print_exc()
            self._clear_info_panels()
    
    def _clear_info_panels(self):
        """Limpia los paneles de información."""
        if hasattr(self, 'proveedor_nombre_label'):
            self.proveedor_nombre_label.config(text="Nombre: -")
            self.proveedor_codigo_label.config(text="Código Quiter: -")
            
            self.vale_no_label.config(text="No Vale: -")
            self.vale_tipo_label.config(text="Tipo: -")
            self.vale_folio_label.config(text="Folio Factura: -")
            
            self.orden_importe_label.config(text="Importe: -")
            self.orden_iva_label.config(text="IVA: -")
            self.orden_letras_label.config(text="Importe en Letras: -")
            self.orden_cuenta_label.config(text="Cuenta Mayor: -")
            self.orden_banco_label.config(text="Banco Código: -")

    # ...existing code...
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
