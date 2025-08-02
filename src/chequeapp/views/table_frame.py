"""
Vista para el frame de la tabla de resultados - Aplicación de Cheques
Adaptado de buscar_app_refactored
"""
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from typing import List, Dict, Any, Callable, Optional
import logging


class TableFrame:
    """Frame que contiene la tabla de resultados para la aplicación de cheques"""
    
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
        
        # Configurar columnas de la tabla
        self.columns = [
            "folio_interno", "tipo", "no_vale", "fecha", "serie_folio",
            "nombre_emisor", "conceptos", "total", "clase", "cargada", "pagada"
        ]
        
        self.column_names = {
            "folio_interno": "Folio Interno",
            "tipo": "Tipo",
            "no_vale": "No Vale",
            "fecha": "Fecha",
            "serie_folio": "Serie-Folio",
            "nombre_emisor": "Emisor",
            "conceptos": "Conceptos",
            "total": "Total",
            "clase": "Clase",
            "cargada": "Cargada",
            "pagada": "Pagada"
        }
        
        self.column_widths = {
            "folio_interno": 100,
            "tipo": 60,
            "no_vale": 80,
            "fecha": 100,
            "serie_folio": 120,
            "nombre_emisor": 200,
            "conceptos": 300,
            "total": 100,
            "clase": 80,
            "cargada": 80,
            "pagada": 80
        }
        
        # Crear Treeview
        all_columns = list(self.columns) + ["original_index"]
        
        self.tree = ttk.Treeview(
            table_container,
            columns=all_columns,
            show="headings",
            height=10,
            selectmode='extended'
        )
        
        # Configurar columnas con ordenamiento
        for col in self.columns:
            self.tree.heading(col, text=self.column_names[col], command=lambda c=col: self._sort_by_column(c))
            self.tree.column(col, width=self.column_widths.get(col, 100), minwidth=60)
        
        # Configurar columna oculta para índice original
        self.tree.heading("original_index", text="")
        self.tree.column("original_index", width=0, minwidth=0, stretch=False)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(table_container, orient="vertical", command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(table_container, orient="horizontal", command=self.tree.xview)
        
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grid layout para tabla y scrollbars
        self.tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        # Configurar expansión
        table_container.grid_rowconfigure(0, weight=1)
        table_container.grid_columnconfigure(0, weight=1)
        
        # Configurar eventos
        self.tree.bind("<<TreeviewSelect>>", self._on_selection_changed)
        self.tree.bind("<Double-1>", self._on_double_click)
        
        # Configurar tags para estilos
        self.tree.tag_configure("even", background="")
        self.tree.tag_configure("odd", background="")
        self.tree.tag_configure("cargada", background="")
        self.tree.tag_configure("pagada", background="")
        self.tree.tag_configure("cargada_pagada", background="")
    
    def load_data(self, data: List[Dict[str, Any]]):
        """
        Carga datos en la tabla
        
        Args:
            data: Lista de diccionarios con los datos
        """
        try:
            # Limpiar tabla
            self.clear_table()
            
            # Guardar datos
            self._current_data = data.copy() if data else []
            
            # Cargar datos en la tabla
            for i, row in enumerate(data):
                values = []
                
                for col in self.columns:
                    value = row.get(col, "")
                    
                    # Formatear valores especiales
                    if col == "total" and value:
                        try:
                            # Formatear como moneda si es numérico
                            float_val = float(str(value).replace(",", "").replace("$", ""))
                            value = f"${float_val:,.2f}"
                        except (ValueError, TypeError):
                            value = str(value)
                    elif col in ["cargada", "pagada"]:
                        # Convertir booleanos a texto
                        bool_val = row.get(f"{col}_bool", False)
                        value = "Sí" if bool_val else "No"
                    else:
                        value = str(value) if value is not None else ""
                    
                    values.append(value)
                
                # Agregar índice original al final
                values.append(str(i))
                
                # Determinar tag para estilos
                tag = "even" if i % 2 == 0 else "odd"
                
                # Tags especiales para estados
                cargada = row.get("cargada_bool", False)
                pagada = row.get("pagada_bool", False)
                
                if cargada and pagada:
                    tag = "cargada_pagada"
                elif cargada:
                    tag = "cargada"
                elif pagada:
                    tag = "pagada"
                
                # Insertar fila
                item_id = self.tree.insert("", "end", values=values, tags=(tag,))
            
            self.logger.info(f"Tabla cargada con {len(data)} registros")
            
        except Exception as e:
            self.logger.error(f"Error cargando datos en tabla: {e}")
    
    def clear_table(self):
        """Limpia todos los datos de la tabla"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        self._current_data = []
    
    def _sort_by_column(self, column: str):
        """
        Ordena la tabla por la columna especificada
        
        Args:
            column: Nombre de la columna por la que ordenar
        """
        if not self._current_data:
            return
        
        # Si se hace clic en la misma columna, invertir el orden
        if self._sort_column == column:
            self._sort_reverse = not self._sort_reverse
        else:
            self._sort_column = column
            self._sort_reverse = False
        
        # Actualizar el texto del header para mostrar el orden
        for col in self.columns:
            header_text = self.column_names[col]
            if col == column:
                if self._sort_reverse:
                    header_text += " ▼"
                else:
                    header_text += " ▲"
            self.tree.heading(col, text=header_text)
        
        # Ordenar los datos
        try:
            def sort_key(item):
                value = item.get(column, "")
                
                # Manejo especial para diferentes tipos de datos
                if column in ["folio_interno", "no_vale"]:
                    # Números: intentar convertir a int, si falla usar string
                    try:
                        return int(str(value))
                    except (ValueError, TypeError):
                        return str(value).lower()
                elif column == "total":
                    # Montos: intentar convertir a float
                    try:
                        return float(str(value).replace(",", "").replace("$", ""))
                    except (ValueError, TypeError):
                        return 0.0
                elif column == "fecha":
                    # Fechas: mantener como string para ordenamiento lexicográfico
                    return str(value)
                elif column in ["cargada", "pagada"]:
                    # Booleanos: True antes que False
                    bool_val = item.get(f"{column}_bool", False)
                    return not bool_val  # Invertir para que True aparezca primero
                else:
                    # Texto: ordenamiento alfabético
                    return str(value).lower()
            
            sorted_data = sorted(self._current_data, key=sort_key, reverse=self._sort_reverse)
            
            # Recargar la tabla con los datos ordenados
            self.clear_table()
            self.load_data(sorted_data)
            
        except Exception as e:
            self.logger.error(f"Error ordenando por columna {column}: {e}")
    
    def get_selected_data(self) -> Optional[Dict[str, Any]]:
        """
        Obtiene los datos de la fila seleccionada
        
        Returns:
            Dict con los datos de la fila seleccionada o None
        """
        selection = self.tree.selection()
        if not selection:
            return None
        
        item = selection[0]
        
        # Obtener índice original
        try:
            original_index = int(self.tree.set(item, "original_index"))
            if 0 <= original_index < len(self._current_data):
                return self._current_data[original_index]
        except (ValueError, IndexError):
            pass
        
        return None
    
    def get_selected_multiple(self) -> List[Dict[str, Any]]:
        """
        Obtiene los datos de todas las filas seleccionadas
        
        Returns:
            Lista de diccionarios con los datos seleccionados
        """
        selection = self.tree.selection()
        selected_data = []
        
        for item in selection:
            try:
                original_index = int(self.tree.set(item, "original_index"))
                if 0 <= original_index < len(self._current_data):
                    selected_data.append(self._current_data[original_index])
            except (ValueError, IndexError):
                continue
        
        return selected_data
    
    def _on_selection_changed(self, event):
        """Maneja el evento de cambio de selección"""
        if self.on_selection_callback:
            selected_data = self.get_selected_data()
            self.on_selection_callback(selected_data)
    
    def _on_double_click(self, event):
        """Maneja el evento de doble click"""
        if self.on_double_click_callback:
            selected_data = self.get_selected_data()
            if selected_data:
                self.on_double_click_callback(selected_data)
