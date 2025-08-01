"""
Componente reutilizable para búsqueda con cuadro de diálogo.
Permite buscar elementos de una lista con filtrado por palabras clave.
"""
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import ttk
from typing import List, Dict, Any, Callable, Optional


class SearchDialog(tb.Toplevel):
    """
    Cuadro de diálogo para buscar y seleccionar elementos de una lista.
    """
    
    def __init__(self, parent, title: str, items: List[Dict[str, Any]],
                 search_fields: List[str], display_columns: List[Dict[str, Any]],
                 on_select: Callable[[Dict[str, Any]], None]):
        """
        Inicializa el cuadro de diálogo de búsqueda.
        
        Args:
            parent: Widget padre
            title: Título del cuadro de diálogo
            items: Lista de elementos para buscar
            search_fields: Campos por los que buscar
            display_columns: Configuración de columnas para mostrar
            on_select: Callback cuando se selecciona un elemento
        """
        super().__init__(parent)
        
        # Configurar ventana
        self.title(title)
        self.geometry("700x500")
        self.transient(parent)
        self.resizable(True, True)
        self.grab_set()
        
        # Centrar en la pantalla
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (700 // 2)
        y = (self.winfo_screenheight() // 2) - (500 // 2)
        self.geometry(f"700x500+{x}+{y}")
        
        # Variables
        self.items = items
        self.filtered_items = []
        self.search_fields = search_fields
        self.display_columns = display_columns
        self.on_select_callback = on_select
        self.selected_item = None
        self.result = None
        
        self._create_layout()
        self._setup_bindings()
        
        # Mostrar todos los elementos inicialmente
        self._filter_items("")
        
        # Focus en el campo de búsqueda
        self.search_entry.focus_set()
    
    def _create_layout(self):
        """Crea el layout del cuadro de diálogo."""
        # Frame principal
        main_frame = tb.Frame(self)
        main_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # Frame de búsqueda
        search_frame = tb.Frame(main_frame)
        search_frame.pack(fill=X, pady=(0, 10))
        
        tb.Label(search_frame, text="Buscar:", font=("Segoe UI", 10)).pack(side=LEFT, padx=(0, 5))
        
        self.search_var = tb.StringVar()
        self.search_entry = tb.Entry(
            search_frame, 
            textvariable=self.search_var,
            font=("Segoe UI", 10)
        )
        self.search_entry.pack(side=LEFT, fill=X, expand=True, padx=(0, 10))
        
        # Botón limpiar
        clear_btn = tb.Button(
            search_frame,
            text="Limpiar",
            bootstyle="secondary-outline",
            command=self._clear_search
        )
        clear_btn.pack(side=RIGHT)
        
        # Frame del TreeView
        tree_frame = tb.Frame(main_frame)
        tree_frame.pack(fill=BOTH, expand=True, pady=(0, 10))
        
        # Crear TreeView con scrollbars
        self.treeview = ttk.Treeview(tree_frame, show="headings")
        
        # Configurar columnas
        columns = [col["name"] for col in self.display_columns]
        self.treeview["columns"] = columns
        
        for col in self.display_columns:
            self.treeview.heading(col["name"], text=col["text"])
            self.treeview.column(col["name"], width=col.get("width", 100))
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=VERTICAL, command=self.treeview.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=HORIZONTAL, command=self.treeview.xview)
        self.treeview.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Posicionar elementos
        self.treeview.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        # Configurar expansión
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # Frame de botones
        button_frame = tb.Frame(main_frame)
        button_frame.pack(fill=X)
        
        # Botones
        cancel_btn = tb.Button(
            button_frame,
            text="Cancelar",
            bootstyle="secondary",
            command=self._cancel
        )
        cancel_btn.pack(side=RIGHT, padx=(10, 0))
        
        select_btn = tb.Button(
            button_frame,
            text="Seleccionar",
            bootstyle="primary",
            command=self._select
        )
        select_btn.pack(side=RIGHT)
    
    def _setup_bindings(self):
        """Configura los eventos."""
        # Filtrar mientras se escribe
        self.search_var.trace_add("write", lambda *args: self._filter_items(self.search_var.get()))
        
        # Selección con doble click
        self.treeview.bind("<Double-1>", lambda e: self._select())
        
        # Tecla Enter para seleccionar
        self.bind("<Return>", lambda e: self._select())
        
        # Tecla Escape para cancelar
        self.bind("<Escape>", lambda e: self._cancel())
    
    def _filter_items(self, search_text: str):
        """Filtra los elementos según el texto de búsqueda."""
        search_text = search_text.lower().strip()
        
        if not search_text:
            # Mostrar todos los elementos
            self.filtered_items = self.items.copy()
        else:
            # Filtrar elementos
            self.filtered_items = []
            for item in self.items:
                # Buscar en todos los campos especificados
                found = False
                for field in self.search_fields:
                    field_value = str(item.get(field, '')).lower()
                    if search_text in field_value:
                        found = True
                        break
                
                if found:
                    self.filtered_items.append(item)
        
        self._update_tree()
    
    def _update_tree(self):
        """Actualiza el contenido del TreeView."""
        # Limpiar TreeView
        for item in self.treeview.get_children():
            self.treeview.delete(item)
        
        # Agregar elementos filtrados
        for item in self.filtered_items:
            values = []
            for col in self.display_columns:
                value = item.get(col["name"], "")
                values.append(str(value))
            
            self.treeview.insert("", END, values=values)
    
    def _clear_search(self):
        """Limpia el campo de búsqueda."""
        self.search_var.set("")
        self.search_entry.focus_set()
    
    def _select(self):
        """Selecciona el elemento actual."""
        selection = self.treeview.selection()
        if not selection:
            return
        
        # Obtener el índice del elemento seleccionado
        item_id = selection[0]
        item_index = self.treeview.index(item_id)
        
        if 0 <= item_index < len(self.filtered_items):
            self.selected_item = self.filtered_items[item_index]
            self.result = self.selected_item
            
            if self.on_select_callback:
                self.on_select_callback(self.selected_item)
            
            self.destroy()
    
    def _cancel(self):
        """Cancela la selección."""
        self.result = None
        self.destroy()


class SearchEntry(tb.Frame):
    """
    Widget que combina un Entry con un botón para abrir el cuadro de búsqueda.
    """
    
    def __init__(self, parent, items=None, search_fields=None, display_columns=None, 
                 entity_type="", placeholder_text="", width=None, on_selection_change=None, **kwargs):
        """
        Inicializa el widget de búsqueda.
        
        Args:
            parent: Widget padre
            items: Lista de elementos para buscar
            search_fields: Campos por los que buscar
            display_columns: Configuración de columnas
            entity_type: Tipo de entidad para el título del diálogo
            placeholder_text: Texto de placeholder
            width: Ancho del Entry
            on_selection_change: Callback cuando cambia la selección
        """
        super().__init__(parent, **kwargs)
        
        self.items = items or []
        self.search_fields = search_fields or []
        self.display_columns = display_columns or []
        self.entity_type = entity_type
        self.placeholder_text = placeholder_text or f"Seleccionar {entity_type}..."
        self.selected_item = None
        self.width = width
        self.on_selection_change = on_selection_change
        
        # Variable para el Entry
        self.entry_var = tb.StringVar()
        
        self._create_layout()
    
    def _create_layout(self):
        """Crea el layout del widget."""
        # Entry
        entry_config = {
            "textvariable": self.entry_var,
            "font": ("Segoe UI", 10),
            "state": "readonly"  # Solo lectura, se llena mediante búsqueda
        }
        if self.width:
            entry_config["width"] = self.width
            
        self.entry = tb.Entry(self, **entry_config)
        self.entry.pack(side=LEFT, fill=X, expand=True, padx=(0, 5))
        
        # Botón de búsqueda
        self.search_button = tb.Button(
            self,
            text="🔍",
            width=3,
            bootstyle="info-outline",
            command=self._open_search_dialog
        )
        self.search_button.pack(side=RIGHT)
        
        # Establecer placeholder si está vacío
        if self.placeholder_text:
            self._set_placeholder()
    
    def _set_placeholder(self):
        """Establece el texto de placeholder."""
        if not self.entry_var.get():
            # Cambiar temporalmente a normal para establecer placeholder
            self.entry.configure(state="normal")
            self.entry_var.set(self.placeholder_text)
            self.entry.configure(foreground="gray")
            self.entry.configure(state="readonly")
    
    def _open_search_dialog(self):
        """Abre el cuadro de diálogo de búsqueda."""
        if not self.items:
            return
            
        dialog = SearchDialog(
            parent=self,
            title=f"Buscar {self.entity_type}",
            items=self.items,
            search_fields=self.search_fields,
            display_columns=self.display_columns,
            on_select=self._on_selection
        )
        
        # Esperar a que se cierre el diálogo
        self.wait_window(dialog)
    
    def _on_selection(self, selected_item: Dict[str, Any]):
        """Maneja la selección de un elemento."""
        self.selected_item = selected_item
        
        # Actualizar el Entry con el elemento seleccionado
        if selected_item:
            # Usar el primer campo de búsqueda como texto a mostrar
            display_text = ""
            if self.search_fields:
                display_text = str(selected_item.get(self.search_fields[0], ""))
            
            self.entry.configure(state="normal", foreground="white")
            self.entry_var.set(display_text)
            self.entry.configure(state="readonly")
            
            # Llamar al callback si existe
            if self.on_selection_change:
                self.on_selection_change(selected_item)
    
    def get_selected_item(self) -> Optional[Dict[str, Any]]:
        """Obtiene el elemento seleccionado."""
        return self.selected_item
    
    def get_selected_value(self, field: str = None) -> Optional[str]:
        """Obtiene un valor específico del elemento seleccionado."""
        if not self.selected_item:
            return None
        
        if field:
            return self.selected_item.get(field)
        
        # Si no se especifica campo, usar el primer campo de búsqueda
        if self.search_fields:
            return self.selected_item.get(self.search_fields[0])
        
        return None
    
    def clear_selection(self):
        """Limpia la selección actual."""
        self.selected_item = None
        self.entry.configure(state="normal")
        self.entry_var.set("")
        self.entry.configure(state="readonly")
        self._set_placeholder()
    
    def set_items(self, items: List[Dict[str, Any]]):
        """Actualiza la lista de elementos disponibles para búsqueda."""
        self.items = items or []
    
    def set_selection(self, item: Dict[str, Any]):
        """Establece la selección programáticamente."""
        self.selected_item = item
        if item and self.search_fields:
            display_text = str(item.get(self.search_fields[0], ""))
            self.entry.configure(state="normal", foreground="white")
            self.entry_var.set(display_text)
            self.entry.configure(state="readonly")
