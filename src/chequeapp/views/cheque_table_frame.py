"""
Frame de tabla específico para cheques
"""
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from typing import List, Dict, Any, Callable, Optional
import logging


class ChequeTableFrame:
    """Frame que contiene la tabla de resultados para cheques"""
    
    def __init__(self, parent, on_selection_callback: Optional[Callable] = None,
                 on_double_click_callback: Optional[Callable] = None):
        self.parent = parent
        self.on_selection_callback = on_selection_callback
        self.on_double_click_callback = on_double_click_callback
        self.logger = logging.getLogger(__name__)
        
        # Crear frame principal
        self.main_frame = ttk.Frame(parent)
        
        self._create_widgets()
        self._current_data = []
        
        # Variables para ordenamiento
        self._sort_column = None
        self._sort_reverse = False
    
    def _create_widgets(self):
        """Crea todos los widgets del frame de tabla"""
        
        # Frame para la tabla y scrollbars
        table_container = ttk.Frame(self.main_frame)
        table_container.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Configurar columnas de la tabla específicas para cheques
        self.columns = [
            "numero_cheque", "fecha_cheque", "beneficiario", "monto", 
            "banco", "estado", "fecha_cobro", "concepto"
        ]
        
        self.column_names = {
            "numero_cheque": "No. Cheque",
            "fecha_cheque": "Fecha Cheque",
            "beneficiario": "Beneficiario",
            "monto": "Monto",
            "banco": "Banco",
            "estado": "Estado",
            "fecha_cobro": "Fecha Cobro",
            "concepto": "Concepto"
        }
        
        self.column_widths = {
            "numero_cheque": 100,
            "fecha_cheque": 120,
            "beneficiario": 250,
            "monto": 120,
            "banco": 150,
            "estado": 100,
            "fecha_cobro": 120,
            "concepto": 200
        }
        
        # Crear Treeview
        all_columns = list(self.columns) + ["original_index", "id"]
        
        self.tree = ttk.Treeview(
            table_container,
            columns=all_columns,
            show="headings",
            height=12,
            selectmode='extended'
        )
        
        # Configurar columnas visibles
        for col in self.columns:
            self.tree.heading(col, text=self.column_names[col], 
                            command=lambda c=col: self._sort_by_column(c))
            self.tree.column(col, width=self.column_widths.get(col, 100), minwidth=60)
        
        # Configurar columnas ocultas
        for hidden_col in ["original_index", "id"]:
            self.tree.heading(hidden_col, text="")
            self.tree.column(hidden_col, width=0, minwidth=0, stretch=False)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(table_container, orient="vertical", command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(table_container, orient="horizontal", command=self.tree.xview)
        
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grid layout para tabla y scrollbars
        self.tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        # Configurar peso de filas y columnas
        table_container.grid_rowconfigure(0, weight=1)
        table_container.grid_columnconfigure(0, weight=1)
        
        # Bindear eventos
        self.tree.bind("<<TreeviewSelect>>", self._on_selection_changed)
        self.tree.bind("<Double-1>", self._on_double_click)
        
        # Configurar colores alternados
        self.tree.tag_configure('oddrow', background='#f0f0f0')
        self.tree.tag_configure('evenrow', background='white')
        
        # Configurar colores por estado
        self.tree.tag_configure('PENDIENTE', foreground='#007acc')
        self.tree.tag_configure('COBRADO', foreground='#28a745')
        self.tree.tag_configure('CANCELADO', foreground='#dc3545')
        
        # Label de información
        self.info_label = ttk.Label(
            self.main_frame,
            text="Total: 0 cheques",
            font=("Segoe UI", 9)
        )
        self.info_label.pack(side="bottom", anchor="w", padx=5, pady=(5, 0))
    
    def load_data(self, data: List[Dict[str, Any]]):
        """Carga datos en la tabla"""
        try:
            # Limpiar tabla actual
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            self._current_data = data
            
            # Agregar nuevos datos
            for index, row in enumerate(data):
                # Preparar valores para mostrar
                values = []
                for col in self.columns:
                    value = row.get(col, '')
                    
                    # Formatear valores específicos
                    if col == 'monto' and value:
                        try:
                            # Formatear como moneda
                            value = f"${float(value):,.2f}"
                        except (ValueError, TypeError):
                            pass
                    elif col in ['fecha_cheque', 'fecha_cobro'] and value:
                        # Formatear fechas
                        if value and value != '':
                            try:
                                # Si es string de fecha, mantener formato
                                if isinstance(value, str) and len(value) == 10:
                                    pass  # Ya está en formato YYYY-MM-DD
                                else:
                                    value = str(value)[:10] if str(value) else ''
                            except:
                                pass
                    
                    values.append(str(value) if value is not None else '')
                
                # Agregar columnas ocultas
                values.append(str(index))  # original_index
                values.append(str(row.get('id', '')))  # id
                
                # Determinar tags para colores
                tags = []
                
                # Color alternado por fila
                if index % 2 == 0:
                    tags.append('evenrow')
                else:
                    tags.append('oddrow')
                
                # Color por estado
                estado = row.get('estado', '')
                if estado in ['PENDIENTE', 'COBRADO', 'CANCELADO']:
                    tags.append(estado)
                
                # Insertar fila
                item_id = self.tree.insert('', 'end', values=values, tags=tags)
            
            # Actualizar label de información
            self.info_label.config(text=f"Total: {len(data)} cheques")
            
            self.logger.debug(f"Cargados {len(data)} cheques en la tabla")
            
        except Exception as e:
            self.logger.error(f"Error cargando datos en tabla: {e}")
    
    def _sort_by_column(self, col):
        """Ordena la tabla por una columna"""
        try:
            # Determinar dirección de ordenamiento
            if self._sort_column == col:
                self._sort_reverse = not self._sort_reverse
            else:
                self._sort_column = col
                self._sort_reverse = False
            
            # Obtener datos actuales con índices
            data_with_index = []
            for item in self.tree.get_children():
                values = self.tree.item(item, 'values')
                data_with_index.append((values, item))
            
            # Encontrar índice de la columna
            col_index = self.columns.index(col)
            
            # Función de ordenamiento
            def sort_key(item):
                value = item[0][col_index]
                
                # Manejar diferentes tipos de datos
                if col == 'monto':
                    # Remover formato de moneda y convertir a float
                    try:
                        clean_value = value.replace('$', '').replace(',', '')
                        return float(clean_value)
                    except:
                        return 0.0
                elif col in ['fecha_cheque', 'fecha_cobro']:
                    # Ordenar por fecha
                    try:
                        if not value or value == '':
                            return '9999-12-31'  # Fechas vacías al final
                        return value
                    except:
                        return '9999-12-31'
                else:
                    # Ordenamiento alfabético
                    return str(value).lower()
            
            # Ordenar
            data_with_index.sort(key=sort_key, reverse=self._sort_reverse)
            
            # Reorganizar elementos en el treeview
            for index, (values, item) in enumerate(data_with_index):
                self.tree.move(item, '', index)
            
            self.logger.debug(f"Tabla ordenada por {col}, reverso: {self._sort_reverse}")
            
        except Exception as e:
            self.logger.error(f"Error ordenando tabla: {e}")
    
    def _on_selection_changed(self, event):
        """Maneja el evento de cambio de selección"""
        try:
            selection = self.tree.selection()
            if selection and self.on_selection_callback:
                # Obtener datos de la primera fila seleccionada
                item = selection[0]
                values = self.tree.item(item, 'values')
                
                # Reconstruir diccionario de datos
                selected_data = {}
                for i, col in enumerate(self.columns):
                    selected_data[col] = values[i] if i < len(values) else ''
                
                # Agregar datos ocultos
                if len(values) > len(self.columns):
                    selected_data['original_index'] = values[len(self.columns)]
                    selected_data['id'] = values[len(self.columns) + 1]
                
                self.on_selection_callback(selected_data)
                
        except Exception as e:
            self.logger.error(f"Error en selección: {e}")
    
    def _on_double_click(self, event):
        """Maneja el evento de doble click"""
        try:
            selection = self.tree.selection()
            if selection and self.on_double_click_callback:
                # Obtener datos de la fila
                item = selection[0]
                values = self.tree.item(item, 'values')
                
                # Reconstruir diccionario de datos
                selected_data = {}
                for i, col in enumerate(self.columns):
                    selected_data[col] = values[i] if i < len(values) else ''
                
                # Agregar datos ocultos
                if len(values) > len(self.columns):
                    selected_data['original_index'] = values[len(self.columns)]
                    selected_data['id'] = values[len(self.columns) + 1]
                
                self.on_double_click_callback(selected_data)
                
        except Exception as e:
            self.logger.error(f"Error en doble click: {e}")
    
    def get_selected_data(self) -> Optional[Dict[str, Any]]:
        """Obtiene los datos de la fila seleccionada"""
        try:
            selection = self.tree.selection()
            if not selection:
                return None
            
            # Obtener datos de la primera fila seleccionada
            item = selection[0]
            values = self.tree.item(item, 'values')
            
            # Reconstruir diccionario de datos
            selected_data = {}
            for i, col in enumerate(self.columns):
                selected_data[col] = values[i] if i < len(values) else ''
            
            # Agregar datos ocultos
            if len(values) > len(self.columns):
                selected_data['original_index'] = values[len(self.columns)]
                selected_data['id'] = values[len(self.columns) + 1]
            
            return selected_data
            
        except Exception as e:
            self.logger.error(f"Error obteniendo datos seleccionados: {e}")
            return None
