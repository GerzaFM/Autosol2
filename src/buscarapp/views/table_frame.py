"""
Vista para el frame de la tabla de resultados
"""
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from typing import List, Dict, Any, Callable, Optional
import logging


class TableFrame:
    """Frame que contiene la tabla de resultados"""
    
    def __init__(self, parent, on_selection_callback: Optional[Callable] = None,
                 on_double_click_callback: Optional[Callable] = None):
        self.parent = parent
        self.on_selection_callback = on_selection_callback
        self.on_double_click_callback = on_double_click_callback
        self.logger = logging.getLogger(__name__)
        
        # Crear frame principal
        self.main_frame = ttk.LabelFrame(
            parent,
            text="📋 Resultados",
            bootstyle="info"
        )
        self.main_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        self._create_widgets()
        self._current_data = []
    
    def _create_widgets(self):
        """Crea todos los widgets del frame de tabla"""
        
        # Frame para la tabla y scrollbars
        table_container = ttk.Frame(self.main_frame)
        table_container.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Configurar columnas de la tabla
        self.columns = [
            "folio_interno", "tipo", "no_vale", "fecha", "serie_folio",
            "nombre_emisor", "conceptos", "total", "cargada", "pagada"
        ]
        
        self.column_headers = {
            "folio_interno": "Folio Interno",
            "tipo": "Tipo",
            "no_vale": "No. Vale",
            "fecha": "Fecha",
            "serie_folio": "Serie-Folio",
            "nombre_emisor": "Proveedor",
            "conceptos": "Conceptos",
            "total": "Total",
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
            "cargada": 80,
            "pagada": 80
        }
        
        # Crear Treeview
        self.tree = ttk.Treeview(
            table_container,
            columns=self.columns,
            show="tree headings",
            bootstyle="info"
        )
        
        # Configurar columnas
        self.tree.heading("#0", text="", anchor="w")
        self.tree.column("#0", width=0, stretch=False)
        
        for col in self.columns:
            self.tree.heading(col, text=self.column_headers[col], anchor="w")
            self.tree.column(col, width=self.column_widths[col], anchor="w")
        
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
        
        # Frame para información de la tabla
        info_frame = ttk.Frame(self.main_frame)
        info_frame.pack(fill="x", padx=5, pady=(0, 5))
        
        # Label de información
        self.info_label = ttk.Label(
            info_frame,
            text="Listo para mostrar resultados",
            bootstyle="info"
        )
        self.info_label.pack(side="left")
        
        # Label de selección
        self.selection_label = ttk.Label(
            info_frame,
            text="",
            bootstyle="secondary"
        )
        self.selection_label.pack(side="right")
        
        # Configurar eventos
        self.tree.bind("<<TreeviewSelect>>", self._on_selection_changed)
        self.tree.bind("<Double-1>", self._on_double_click)
        
        # Configurar tags para colores alternados
        self.tree.tag_configure("even", background="#f8f9fa")
        self.tree.tag_configure("odd", background="#ffffff")
        self.tree.tag_configure("cargada", background="#d4edda")
        self.tree.tag_configure("pagada", background="#fff3cd")
        self.tree.tag_configure("cargada_pagada", background="#b8e6b8")
    
    def load_data(self, data: List[Dict[str, Any]]):
        """
        Carga datos en la tabla
        
        Args:
            data: Lista de diccionarios con los datos
        """
        try:
            # Limpiar tabla
            self.clear_table()
            
            if not data:
                self.info_label.config(text="No hay resultados para mostrar")
                return
            
            self._current_data = data.copy()
            
            # Insertar datos
            for i, row in enumerate(data):
                # Preparar valores para las columnas
                values = []
                for col in self.columns:
                    value = row.get(col, "")
                    
                    # Formatear valores especiales
                    if col == "total" and isinstance(value, (int, float)):
                        value = f"${value:,.2f}"
                    elif col in ["cargada", "pagada"]:
                        value = "✓" if row.get(f"{col}_bool", False) else ""
                    elif col == "serie_folio":
                        # Construir serie-folio
                        serie = row.get("serie", "")
                        folio = row.get("folio", "")
                        value = f"{serie} {folio}".strip()
                    
                    values.append(str(value))
                
                # Determinar tag para colores
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
                
                # Almacenar índice original en el item
                self.tree.set(item_id, "original_index", i)
            
            # Actualizar información
            self.info_label.config(text=f"Mostrando {len(data)} registros")
            
            self.logger.info(f"Tabla cargada con {len(data)} registros")
            
        except Exception as e:
            self.logger.error(f"Error cargando datos en tabla: {e}")
            self.info_label.config(text="Error cargando datos")
    
    def clear_table(self):
        """Limpia todos los datos de la tabla"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        self._current_data = []
        self.info_label.config(text="Tabla vacía")
        self.selection_label.config(text="")
    
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
        
        # Fallback: construir datos desde los valores de la tabla
        values = self.tree.item(item, "values")
        if len(values) >= len(self.columns):
            data = {}
            for i, col in enumerate(self.columns):
                data[col] = values[i]
            return data
        
        return None
    
    def get_selected_index(self) -> Optional[int]:
        """
        Obtiene el índice de la fila seleccionada
        
        Returns:
            Índice de la fila seleccionada o None
        """
        selection = self.tree.selection()
        if not selection:
            return None
        
        item = selection[0]
        try:
            return int(self.tree.set(item, "original_index"))
        except (ValueError, IndexError):
            return None
    
    def select_row(self, index: int):
        """
        Selecciona una fila por índice
        
        Args:
            index: Índice de la fila a seleccionar
        """
        try:
            items = self.tree.get_children()
            if 0 <= index < len(items):
                item = items[index]
                self.tree.selection_set(item)
                self.tree.focus(item)
                self.tree.see(item)
        except Exception as e:
            self.logger.error(f"Error seleccionando fila {index}: {e}")
    
    def _on_selection_changed(self, event):
        """Maneja el evento de cambio de selección"""
        selected_data = self.get_selected_data()
        
        if selected_data:
            folio = selected_data.get("folio_interno", "")
            proveedor = selected_data.get("nombre_emisor", "")[:30]
            if len(selected_data.get("nombre_emisor", "")) > 30:
                proveedor += "..."
            
            self.selection_label.config(
                text=f"Seleccionado: {folio} - {proveedor}"
            )
        else:
            self.selection_label.config(text="")
        
        # Llamar callback si existe
        if self.on_selection_callback:
            self.on_selection_callback(selected_data)
    
    def _on_double_click(self, event):
        """Maneja el evento de doble click"""
        selected_data = self.get_selected_data()
        if selected_data and self.on_double_click_callback:
            self.on_double_click_callback(selected_data)
    
    def update_row_status(self, folio_interno: str, cargada: Optional[bool] = None, 
                         pagada: Optional[bool] = None):
        """
        Actualiza el estado de una fila específica
        
        Args:
            folio_interno: Folio interno de la factura
            cargada: Nuevo estado de cargada (opcional)
            pagada: Nuevo estado de pagada (opcional)
        """
        try:
            # Buscar la fila en los datos actuales
            for i, row_data in enumerate(self._current_data):
                if row_data.get("folio_interno") == folio_interno:
                    # Actualizar datos
                    if cargada is not None:
                        row_data["cargada_bool"] = cargada
                        row_data["cargada"] = "✓" if cargada else ""
                    if pagada is not None:
                        row_data["pagada_bool"] = pagada
                        row_data["pagada"] = "✓" if pagada else ""
                    
                    # Actualizar vista
                    items = self.tree.get_children()
                    if i < len(items):
                        item = items[i]
                        
                        # Actualizar valores
                        values = list(self.tree.item(item, "values"))
                        if cargada is not None and len(values) > 8:
                            values[8] = "✓" if cargada else ""
                        if pagada is not None and len(values) > 9:
                            values[9] = "✓" if pagada else ""
                        
                        self.tree.item(item, values=values)
                        
                        # Actualizar tag para colores
                        new_cargada = row_data.get("cargada_bool", False)
                        new_pagada = row_data.get("pagada_bool", False)
                        
                        if new_cargada and new_pagada:
                            tag = "cargada_pagada"
                        elif new_cargada:
                            tag = "cargada"
                        elif new_pagada:
                            tag = "pagada"
                        else:
                            tag = "even" if i % 2 == 0 else "odd"
                        
                        self.tree.item(item, tags=(tag,))
                    
                    break
                    
        except Exception as e:
            self.logger.error(f"Error actualizando estado de fila {folio_interno}: {e}")
    
    def get_all_data(self) -> List[Dict[str, Any]]:
        """
        Obtiene todos los datos actuales de la tabla
        
        Returns:
            Lista con todos los datos
        """
        return self._current_data.copy()
    
    def get_frame(self):
        """Retorna el frame principal"""
        return self.main_frame
