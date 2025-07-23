"""
Componentes de vista reutilizables.
"""
import tkinter as tk
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from typing import Dict, List, Callable, Optional
from decimal import Decimal

import sys
import os
# Agregar el directorio solicitudapp al path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from solicitudapp.config.app_config import AppConfig
from solicitudapp.services.validation import ValidationService

# Importar componentes de búsqueda
try:
    from solicitudapp.search_components import SearchEntry
    SEARCH_COMPONENTS_AVAILABLE = True
except ImportError:
    SEARCH_COMPONENTS_AVAILABLE = False
    SearchEntry = None


class BaseFrame(tb.Labelframe):
    """Frame base con funcionalidades comunes."""
    
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.validation_service = ValidationService()
    
    def clear_entries(self):
        """Limpia todos los Entry y Text widgets en este frame."""
        self._clear_widget_recursive(self)
    
    def _clear_widget_recursive(self, widget):
        """Limpia widgets recursivamente."""
        if isinstance(widget, tb.Entry):
            widget.delete(0, 'end')
        elif isinstance(widget, tb.Text):
            widget.delete("1.0", "end")
        elif isinstance(widget, tb.Combobox):
            widget.set("")
        elif hasattr(widget, 'clear_selection'):  # SearchEntry
            widget.clear_selection()
        
        for child in widget.winfo_children():
            self._clear_widget_recursive(child)


class ProveedorFrame(BaseFrame):
    """Frame para datos del proveedor con búsqueda avanzada."""
    
    def __init__(self, master=None, db_manager=None):
        super().__init__(master)
        self.db_manager = db_manager
        self.entries: Dict[str, tb.Entry] = {}
        self.proveedor_search = None  # SearchEntry component
        self._build_ui()
    
    def _build_ui(self):
        # Configurar el frame
        self.configure(text="Datos de proveedor", width=350)
        self.pack_propagate(False)
        
        # Si está disponible el componente de búsqueda, agregarlo primero
        if SEARCH_COMPONENTS_AVAILABLE and self.db_manager:
            self._create_search_component()
        
        # Campos del proveedor
        campos = ["Nombre", "RFC", "Teléfono", "Correo", "Contacto"]
        start_row = 1 if SEARCH_COMPONENTS_AVAILABLE and self.db_manager else 0
        
        for i, campo in enumerate(campos):
            tb.Label(self, text=f"{campo}:").grid(
                row=start_row + i, column=0, sticky=E, padx=5, pady=4
            )
            entry = tb.Entry(self, width=56, bootstyle="dark")
            entry.grid(row=start_row + i, column=1, padx=5, pady=4)
            self.entries[campo] = entry
    
    def _create_search_component(self):
        """Crea el componente de búsqueda de proveedores."""
        try:
            # Obtener proveedores de la base de datos
            proveedores_data = self._get_proveedores_data()
            
            if proveedores_data:
                # Label para búsqueda
                tb.Label(self, text="Buscar:").grid(
                    row=0, column=0, sticky=E, padx=5, pady=4
                )
                
                # Componente de búsqueda
                self.proveedor_search = SearchEntry(
                    parent=self,
                    items=proveedores_data,
                    search_fields=['nombre', 'rfc'],
                    display_columns=[
                        {'name': 'nombre', 'text': 'Nombre', 'width': 250},
                        {'name': 'rfc', 'text': 'RFC', 'width': 130},
                        {'name': 'telefono', 'text': 'Teléfono', 'width': 100},
                        {'name': 'email', 'text': 'Email', 'width': 200}
                    ],
                    entity_type="Proveedor",
                    placeholder_text="Buscar proveedor...",
                    width=40,
                    on_selection_change=self._on_proveedor_selected
                )
                self.proveedor_search.grid(row=0, column=1, padx=5, pady=4, sticky="ew")
                
        except Exception as e:
            print(f"Error creando componente de búsqueda: {e}")
    
    def _get_proveedores_data(self) -> List[Dict[str, str]]:
        """Obtiene la lista de proveedores desde la base de datos."""
        try:
            if not self.db_manager:
                return []
            
            # Importar Proveedor aquí para evitar dependencias circulares
            from bd.models import Proveedor
            
            proveedores = Proveedor.select()
            proveedores_data = []
            
            for proveedor in proveedores:
                proveedores_data.append({
                    'id': proveedor.id,
                    'nombre': proveedor.nombre or '',
                    'rfc': proveedor.rfc or '',
                    'telefono': proveedor.telefono or '',
                    'email': proveedor.email or '',
                    'nombre_contacto': getattr(proveedor, 'nombre_contacto', '') or ''
                })
            
            return proveedores_data
            
        except Exception as e:
            print(f"Error obteniendo proveedores: {e}")
            return []
    
    def _on_proveedor_selected(self, proveedor_data: Dict[str, str]):
        """Callback cuando se selecciona un proveedor."""
        try:
            # Rellenar automáticamente los campos con los datos del proveedor
            data = {
                "Nombre": proveedor_data.get('nombre', ''),
                "RFC": proveedor_data.get('rfc', ''),
                "Teléfono": proveedor_data.get('telefono', ''),
                "Correo": proveedor_data.get('email', ''),
                "Contacto": proveedor_data.get('nombre_contacto', '')
            }
            self.set_data(data)
            
        except Exception as e:
            print(f"Error al seleccionar proveedor: {e}")
    
    def get_data(self) -> Dict[str, str]:
        """Obtiene los datos del proveedor."""
        return {campo: entry.get().strip() for campo, entry in self.entries.items()}
    
    def set_data(self, data: Dict[str, str]):
        """Establece los datos del proveedor."""
        for campo, valor in data.items():
            if campo in self.entries:
                self.entries[campo].delete(0, 'end')
                self.entries[campo].insert(0, valor)
    
    def validate(self) -> tuple[bool, List[str]]:
        """Valida los datos del proveedor."""
        data = self.get_data()
        errores = []
        
        # Validar campos obligatorios
        if not data["Nombre"]:
            errores.append("El nombre del proveedor es obligatorio")
        if not data["RFC"]:
            errores.append("El RFC del proveedor es obligatorio")
        
        # Validar RFC
        if data["RFC"]:
            valido, mensaje = self.validation_service.validar_rfc(data["RFC"])
            if not valido:
                errores.append(mensaje)
        
        return len(errores) == 0, errores
        
        # Validar email
        if data["Correo"]:
            valido, mensaje = self.validation_service.validar_email(data["Correo"])
            if not valido:
                errores.append(mensaje)
        
        # Validar teléfono
        if data["Teléfono"]:
            valido, mensaje = self.validation_service.validar_telefono(data["Teléfono"])
            if not valido:
                errores.append(mensaje)
        
        return len(errores) == 0, errores


class SolicitudFrame(BaseFrame):
    """Frame para datos de la solicitud con búsqueda avanzada."""
    
    def __init__(self, master=None):
        super().__init__(master)
        self.entries: Dict[str, tb.Widget] = {}
        self.tipo_search = None  # SearchEntry component for tipo de vale
        self._build_ui()
    
    def _build_ui(self):
        self.configure(text="Datos de la solicitud", width=320)
        self.pack_propagate(False)
        
        campos = ["Fecha", "Clase", "Tipo", "Depa", "Folio"]
        
        for i, campo in enumerate(campos):
            tb.Label(self, text=f"{campo}:").grid(
                row=i, column=0, sticky=E, padx=5, pady=4
            )
            
            if campo == "Tipo":
                if SEARCH_COMPONENTS_AVAILABLE:
                    # Usar componente de búsqueda para tipos de vale
                    tipos_data = self._get_tipos_vale_data()
                    self.tipo_search = SearchEntry(
                        parent=self,
                        items=tipos_data,
                        search_fields=['clave', 'descripcion'],
                        display_columns=[
                            {'name': 'clave', 'text': 'Clave', 'width': 80},
                            {'name': 'descripcion', 'text': 'Descripción', 'width': 200}
                        ],
                        entity_type="Tipo de Vale",
                        placeholder_text="Seleccionar tipo...",
                        width=20
                    )
                    widget = self.tipo_search
                else:
                    # Fallback a Combobox tradicional
                    tipo_vales_list = [f"{k} - {v}" for k, v in AppConfig.TIPO_VALE.items()]
                    widget = tb.Combobox(
                        self, 
                        values=tipo_vales_list, 
                        width=22, 
                        bootstyle="dark"
                    )
                    widget.set(tipo_vales_list[0] if tipo_vales_list else "")
                    widget.bind("<FocusOut>", self._validar_tipo_vale)
                    widget.bind("<Return>", self._validar_tipo_vale)
            elif campo == "Depa":
                widget = tb.Combobox(
                    self, 
                    values=AppConfig.DEPARTAMENTOS, 
                    width=22, 
                    bootstyle="dark",
                    state="readonly"
                )
                widget.set(AppConfig.DEFAULT_VALUES["departamento"])
            elif campo == "Fecha":
                widget = tb.DateEntry(
                    self,
                    width=19,
                    bootstyle="dark"
                )
            else:
                widget = tb.Entry(self, width=24, bootstyle="dark")
            
            widget.grid(row=i, column=1, padx=5, pady=4)
            self.entries[campo] = widget
    
    def _get_tipos_vale_data(self) -> List[Dict[str, str]]:
        """Obtiene la lista de tipos de vale desde la configuración."""
        tipos_data = []
        for clave, descripcion in AppConfig.TIPO_VALE.items():
            tipos_data.append({
                'clave': clave,
                'descripcion': descripcion,
                'display': f"{clave} - {descripcion}"
            })
        return tipos_data
    
    def get_data(self) -> Dict[str, str]:
        """Obtiene los datos de la solicitud."""
        data = {}
        for campo, widget in self.entries.items():
            if campo == "Tipo" and self.tipo_search:
                # Para SearchEntry, obtener el valor seleccionado
                selected_item = self.tipo_search.get_selected_item()
                if selected_item:
                    data[campo] = selected_item.get('display', '')
                else:
                    data[campo] = ''
            elif campo == "Fecha":
                data[campo] = widget.entry.get()
            else:
                data[campo] = widget.get()
        return data
    
    def set_data(self, data: Dict[str, str]):
        """Establece los datos de la solicitud."""
        for campo, valor in data.items():
            if campo in self.entries:
                widget = self.entries[campo]
                if campo == "Tipo" and self.tipo_search:
                    # Para SearchEntry, buscar el item correspondiente
                    for item in self.tipo_search.items:
                        if item.get('display') == valor or item.get('clave') in valor:
                            self.tipo_search.set_selection(item)
                            break
                elif campo == "Fecha":
                    widget.entry.delete(0, 'end')
                    widget.entry.insert(0, valor)
                elif isinstance(widget, tb.Combobox):
                    widget.set(valor)
                else:
                    widget.delete(0, 'end')
                    widget.insert(0, valor)
    
    def clear_entries(self):
        """Limpia todos los campos del frame de solicitud."""
        for campo, widget in self.entries.items():
            if campo == "Tipo" and self.tipo_search:
                self.tipo_search.clear_selection()
            elif campo == "Fecha":
                widget.entry.delete(0, 'end')
            elif hasattr(widget, 'delete'):
                widget.delete(0, 'end')
            elif hasattr(widget, 'set'):
                widget.set("")
    
    def _validar_tipo_vale(self, event=None):
        """
        Valida el texto del Combobox Tipo.
        Si es una clave válida en AppConfig.TIPO_VALE, lo formatea como 'key - value'.
        Si no, borra el contenido.
        """
        cb_tipo = self.entries["Tipo"]
        texto = cb_tipo.get().strip().upper()
        # Extraer solo la clave si el usuario seleccionó "KEY - VALUE"
        clave = texto.split(" - ")[0]
        if clave in AppConfig.TIPO_VALE:
            valor = AppConfig.TIPO_VALE[clave]
            cb_tipo.set(f"{clave} - {valor}")
        else:
            cb_tipo.set("")


class ConceptoPopup:
    """Popup para agregar/editar conceptos."""
    
    def __init__(self, parent, title: str, button_text: str, 
                 callback: Callable, valores_iniciales: Optional[List[str]] = None):
        self.parent = parent
        self.callback = callback
        self.popup = None
        self.entries = {}
        self._create_popup(title, button_text, valores_iniciales)
    
    def _create_popup(self, title: str, button_text: str, 
                     valores_iniciales: Optional[List[str]]):
        self.popup = tk.Toplevel(self.parent)
        self.popup.title(title)
        self.popup.geometry("720x120")
        self.popup.grab_set()
        self.popup.resizable(False, False)
        
        # Centrar el popup
        self.popup.transient(self.parent)
        
        labels = ["Cantidad", "Descripción", "Precio", "Total"]
        
        # Crear etiquetas y campos
        for i, label in enumerate(labels):
            tk.Label(self.popup, text=label).grid(
                row=0, column=i, padx=10, pady=8, sticky="w"
            )
            
            width = AppConfig.POPUP_ENTRY_WIDTHS[label]
            entry = tk.Entry(self.popup, width=width)
            entry.grid(row=1, column=i, padx=10, pady=8)
            
            if valores_iniciales and i < len(valores_iniciales):
                entry.insert(0, valores_iniciales[i])
            
            self.entries[label] = entry
        
        # Botón de acción
        tk.Button(
            self.popup, 
            text=button_text, 
            command=self._on_ok
        ).grid(row=2, column=0, columnspan=len(labels), pady=12)
        
        # Focus en el primer campo
        self.entries["Cantidad"].focus()
        
        # Bind Enter key
        self.popup.bind('<Return>', lambda e: self._on_ok())
        self.popup.bind('<Escape>', lambda e: self.popup.destroy())
    
    def _on_ok(self):
        """Maneja la confirmación del popup."""
        from tkinter import messagebox
        
        values = [self.entries[label].get().strip() for label in self.entries.keys()]
        
        # Validar campos obligatorios
        if not all(values):
            messagebox.showerror("Error", AppConfig.ERROR_MESSAGES["campos_obligatorios"])
            return
        
        # Validar números
        validation_service = ValidationService()
        try:
            # Validar cantidad, precio y total
            for i, campo in enumerate(["Cantidad", "Precio", "Total"]):
                if i == 1:  # Saltar descripción
                    continue
                idx = 0 if i == 0 else i  # Ajustar índice para saltar descripción
                if idx == 2:  # Precio
                    idx = 2
                elif idx == 3:  # Total
                    idx = 3
                
                valido, mensaje = validation_service.validar_numero(
                    values[idx], campo
                )
                if not valido:
                    messagebox.showerror("Error", mensaje)
                    return
        except Exception:
            messagebox.showerror("Error", AppConfig.ERROR_MESSAGES["numeros_invalidos"])
            return
        
        # Si todo es válido, ejecutar callback y cerrar
        self.callback(values)
        self.popup.destroy()
