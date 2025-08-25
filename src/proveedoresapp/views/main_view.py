"""
ProveedoreView - Vista principal de la aplicación de proveedores
================================================================

Componente principal de la interfaz que orquesta y coordina todos los
elementos visuales de la aplicación. Actúa como contenedor maestro
integrando búsqueda, listado, formularios y controles de acción.

Arquitectura de componentes:
┌─────────────────────────────────────────┐
│        ProveedoreView (tb.Frame)         │
│  ┌─────────────────────────────────────┐ │
│  │        SearchFrame                   │ │ <- Búsqueda y filtros
│  └─────────────────────────────────────┘ │
│  ┌─────────────────────────────────────┐ │
│  │        TreeFrame                     │ │ <- Tabla de datos
│  └─────────────────────────────────────┘ │
│  ┌─────────────────────────────────────┐ │
│  │        ButtonsList                   │ │ <- Botones de acción
│  └─────────────────────────────────────┘ │
│  ┌─────────────────────────────────────┐ │
│  │        DataForm                      │ │ <- Formulario CRUD
│  └─────────────────────────────────────┘ │
└─────────────────────────────────────────┘

Patrón implementado:
- Facade Pattern: Simplifica la interacción con múltiples subsistemas (frames)
- Composite Pattern: Integra múltiples componentes en una interfaz unificada
- MVC Pattern: Actúa como la Vista principal en la arquitectura MVC

Responsabilidades principales:
- Composición y layout de la interfaz completa
- Abstracción de operaciones complejas (CRUD) en métodos simples
- Gestión del estado de la interfaz (formularios, selecciones)
- Coordinación entre componentes especializados
"""

import sys
import os
from pathlib import Path
import ttkbootstrap as tb

# Importación de componentes especializados
from proveedoresapp.views.frame_search import SearchFrame      # Panel de búsqueda
from proveedoresapp.views.frame_list import TreeFrame         # Tabla de datos  
from proveedoresapp.views.frame_buttons_list import ButtonsList # Botones de acción
from proveedoresapp.views.frame_dataform import DataForm      # Formulario de datos


class ProveedoreView(tb.Frame):
    """
    Vista principal que integra todos los componentes de la interfaz de proveedores.
    
    Hereda de tb.Frame para actuar como contenedor principal de la aplicación.
    Implementa el patrón Facade proporcionando una interfaz simplificada
    para operaciones complejas que involucran múltiples componentes.
    
    Componentes integrados:
    - SearchFrame: Búsqueda en tiempo real y filtros por estado
    - TreeFrame: Tabla con datos y ordenamiento por columnas
    - ButtonsList: Botones para operaciones CRUD principales
    - DataForm: Formulario para crear/editar proveedores
    
    Métodos de alto nivel:
    - Gestión de datos: get_form_data(), fill_form(), clear_form()
    - Operaciones de lista: fill_list(), get_selection(), add_item()
    - Control de estado: set_editable(), get_search_text()
    
    Integración MVC:
    - Proporciona interface limpia para el controlador
    - Abstrae complejidad de múltiples componentes
    - Mantiene estado consistente entre componentes
    """
    
    def __init__(self, master):
        """
        Inicializa la vista principal y todos sus componentes.
        
        Args:
            master: Widget padre (típicamente root window de la aplicación)
            
        Crea la jerarquía completa de componentes y establece las
        referencias necesarias para que el controlador pueda operar
        sobre la interfaz de manera simple y directa.
        
        Configuración del layout:
        - Frame principal expandible (fill='both', expand=True)
        - Componentes organizados verticalmente
        - Referencias directas a elementos importantes
        - Diccionario de entries para acceso simplificado
        """
        super().__init__(master)
        
        # === CONFIGURACIÓN DEL CONTENEDOR PRINCIPAL ===
        # Frame principal que ocupa toda la ventana disponible
        # Permite redimensionamiento automático y responsive design
        self.pack(fill='both', expand=True)
        
        # === INICIALIZACIÓN DE COMPONENTES PRINCIPALES ===
        # Orden de creación define el orden visual (top-to-bottom)
        
        # 1. Panel de búsqueda y filtros (parte superior)
        # Permite búsqueda en tiempo real y filtrado por proveedores incompletos
        self.search_frame = SearchFrame(self)
        
        # 2. Tabla de datos principales (componente central)
        # Muestra la lista de proveedores con capacidades de ordenamiento
        self.tree_frame = TreeFrame(self)
        
        # 3. Panel de botones de acción (debajo de la tabla)
        # Proporciona acceso directo a operaciones CRUD
        self.buttons_frame = ButtonsList(self)
        
        # 4. Formulario de datos (parte inferior)
        # Se muestra contextualmente para crear/editar proveedores
        self.data_form = DataForm(self)

        # === REFERENCIAS A BOTONES ESPECÍFICOS ===
        # Facilita la vinculación de eventos desde el controlador
        # Patrón: self.button_[acción] para consistencia
        
        # Botón de búsqueda (del frame de búsqueda)
        self.button_search = self.search_frame.button_search

        # Botones de operaciones principales (del frame de botones)
        self.button_combine = self.buttons_frame.button_combine    # Combinar proveedores
        self.button_add = self.buttons_frame.button_add           # Agregar nuevo
        self.button_delete = self.buttons_frame.button_delete     # Eliminar seleccionado
        self.button_edit = self.buttons_frame.button_edit         # Editar seleccionado

        # Botones del formulario (del frame de formulario)  
        self.button_save = self.data_form.button_guardar          # Guardar cambios
        self.button_cancel = self.data_form.button_cancelar       # Cancelar operación

        # === DICCIONARIO DE CAMPOS DEL FORMULARIO ===
        # Facilita el acceso programático a todos los campos de entrada
        # Permite operaciones masivas: llenar, limpiar, validar, etc.
        # Mapeo: nombre_campo -> referencia_al_widget
        self.entries = {
            "codigo": self.data_form.entry_codigo,                # Código único del proveedor
            "nombre": self.data_form.entry_nombre,                # Nombre comercial
            "email": self.data_form.entry_email,                  # Correo electrónico
            "nombre_contacto": self.data_form.entry_nombre_contacto, # Persona de contacto
            "rfc": self.data_form.entry_rfc,                      # RFC fiscal
            "nombre_quiter": self.data_form.entry_nombre_quiter,  # Nombre para quitar
            "telefono": self.data_form.entry_telefono             # Número telefónico
        }

    # === MÉTODOS DE OBTENCIÓN DE DATOS DE BÚSQUEDA ===
    
    def get_search_text(self):
        """
        Obtiene el texto actual del campo de búsqueda.
        
        Returns:
            str: Texto ingresado por el usuario para búsqueda.
                 Puede ser vacío si no hay texto o si está mostrando placeholder.
        
        Utiliza el método especializado get_search_text() del SearchBar
        que maneja correctamente la distinción entre texto real y placeholder.
        """
        return self.search_frame.search_bar.get_search_text()

    def get_incompletos(self):
        """
        Obtiene el estado del filtro de proveedores incompletos.
        
        Returns:
            bool: True si el filtro está activado (mostrar solo incompletos),
                  False si está desactivado (mostrar todos los proveedores).
        
        Este filtro permite al usuario ver únicamente los proveedores
        que tienen campos faltantes o información incompleta.
        """
        return self.search_frame.incomplete_var.get()
    
    # === MÉTODOS DE GESTIÓN DE LA LISTA/TABLA ===
    
    def clear_list(self):
        """
        Limpia completamente la tabla de proveedores.
        
        Elimina todas las filas mostradas en el TreeView, dejándolo
        vacío para nueva población de datos. Útil antes de actualizar
        la lista con nuevos resultados de búsqueda o filtros.
        """
        self.tree_frame.treeview.delete(*self.tree_frame.treeview.get_children())

    def fill_list(self, data):
        """
        Pobla la tabla con una lista de proveedores.
        
        Args:
            data: Lista de tuplas/listas, donde cada elemento representa
                  un proveedor con todos sus campos en orden de columnas.
        
        Proceso:
        1. Limpia la tabla actual
        2. Inserta cada proveedor como nueva fila
        3. Los datos se muestran inmediatamente en la interfaz
        
        Formato esperado de data:
        [
            (id, codigo, nombre, email, contacto, rfc, telefono),
            (id, codigo, nombre, email, contacto, rfc, telefono),
            ...
        ]
        """
        self.clear_list()
        for item in data:
            self.tree_frame.treeview.insert("", "end", values=item)

    def get_selection(self):
        """
        Obtiene los datos del proveedor actualmente seleccionado en la tabla.
        
        Returns:
            tuple | None: Tupla con todos los valores del proveedor seleccionado,
                         o None si no hay selección activa.
        
        Útil para obtener todos los datos del proveedor para operaciones
        como editar, eliminar o mostrar detalles. La tupla contiene los
        valores en el mismo orden que las columnas de la tabla.
        """
        selected_item = self.tree_frame.treeview.selection()
        if selected_item:
            return self.tree_frame.treeview.item(selected_item, "values")
        return None
    
    def get_selected_id(self):
        """
        Obtiene específicamente el ID del proveedor seleccionado.
        
        Returns:
            int | None: ID numérico del proveedor seleccionado,
                       o None si no hay selección.
        
        Optimización para casos donde solo se necesita el identificador
        único del proveedor (ej: operaciones de base de datos).
        Asume que el ID está siempre en la primera columna (índice 0).
        """
        selected_item = self.tree_frame.treeview.selection()
        if selected_item:
            item_id = int(self.tree_frame.treeview.item(selected_item, "values")[0])
            return item_id
        return None

    def add_item(self, item):
        """
        Agrega un nuevo proveedor a la tabla sin recargar toda la lista.
        
        Args:
            item: Tupla/lista con los datos del nuevo proveedor
                  en orden de columnas.
        
        Inserción optimizada que mantiene el estado actual de la tabla
        (selecciones, scroll, etc.) y solo agrega el nuevo elemento
        al final de la lista.
        """
        self.tree_frame.treeview.insert("", "end", values=item)

    def remove_selected(self):
        """
        Elimina de la tabla el proveedor actualmente seleccionado.
        
        Solo elimina de la vista (TreeView), no de la base de datos.
        La eliminación de BD debe manejarse por separado en el modelo.
        
        Útil para reflejar inmediatamente eliminaciones sin recargar
        toda la lista desde la base de datos.
        """
        selected_item = self.tree_frame.treeview.selection()
        if selected_item:
            self.tree_frame.treeview.delete(selected_item)

    def modify_selected(self, new_values):
        """
        Actualiza los datos del proveedor seleccionado en la tabla.
        
        Args:
            new_values: Tupla/lista con los nuevos valores para todas
                       las columnas del proveedor.
        
        Actualización en lugar sin afectar la posición o selección
        del elemento. Útil después de editar un proveedor para
        reflejar los cambios inmediatamente en la tabla.
        """
        selected_item = self.tree_frame.treeview.selection()
        if selected_item:
            self.tree_frame.treeview.item(selected_item, values=new_values)

    # === MÉTODOS DE GESTIÓN DEL FORMULARIO ===
    
    def get_form_data(self):
        """
        Recopila todos los datos ingresados en el formulario.
        
        Returns:
            dict: Diccionario con todos los campos del formulario.
                  Formato: {"campo": "valor", ...}
        
        Maneja inteligentemente diferentes tipos de widgets:
        - SearchBar: usa get_search_text() para evitar placeholder
        - Entry normal: usa get() directamente
        
        Útil para validación, guardado y operaciones CRUD que
        requieren todos los datos del formulario como estructura.
        """
        return {key: entry.get_search_text() if hasattr(entry, 'get_search_text') else entry.get() 
                for key, entry in self.entries.items()}
    
    def fill_form(self, data):
        """
        Llena el formulario con datos de un proveedor existente.
        
        Args:
            data: Diccionario con los datos del proveedor.
                  Las claves deben coincidir con los nombres de campos.
        
        Utiliza el método set_text() específico de SearchBar para
        manejar correctamente la transición placeholder -> datos reales.
        
        Casos de uso:
        - Cargar datos para edición
        - Mostrar detalles de proveedor seleccionado
        - Prellenar formulario con valores por defecto
        """
        for key, value in data.items():
            if key in self.entries:
                # Usar el método set_text del SearchBar para manejar correctamente placeholder vs datos reales
                self.entries[key].set_text(value)

    def clear_form(self):
        """
        Limpia completamente el formulario de datos.
        
        Restaura todos los campos a su estado inicial (vacío/placeholder).
        Utiliza clear_search() específico de SearchBar para manejar
        correctamente la restauración del placeholder.
        
        Casos de uso:
        - Cancelar operación de edición
        - Preparar formulario para nuevo proveedor
        - Reset después de operación completada
        """
        for entry in self.entries.values():
            entry.clear_search()

    def set_editable(self, editable):
        """
        Controla si los campos del formulario pueden ser editados.
        
        Args:
            editable (bool): True para habilitar edición,
                           False para solo lectura.
        
        Útil para:
        - Modo lectura: mostrar datos sin permitir cambios
        - Modo edición: habilitar modificaciones
        - Estados intermedios durante procesamiento
        
        Aplica el cambio a todos los campos simultáneamente
        manteniendo consistencia en toda la interfaz.
        """
        for entry in self.entries.values():
            entry.set_editable(editable) 