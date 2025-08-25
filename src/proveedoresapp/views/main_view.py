import sys
import os
from pathlib import Path
import ttkbootstrap as tb

from proveedoresapp.views.frame_search import SearchFrame
from proveedoresapp.views.frame_list import TreeFrame
from proveedoresapp.views.frame_buttons_list import ButtonsList
from proveedoresapp.views.frame_dataform import DataForm


class ProveedoreView(tb.Frame):
    def __init__(self, master):
        super().__init__(master)
        
        # Crear un contenedor principal que ocupe toda la ventana
        self.pack(fill='both', expand=True)
        # Crear los marcos
        self.search_frame = SearchFrame(self)
        self.tree_frame = TreeFrame(self)
        self.buttons_frame = ButtonsList(self)
        self.data_form = DataForm(self)

        # Botones del marco de búsqueda
        self.button_search = self.search_frame.button_search

        # Botones del marco de lista
        self.button_combine = self.buttons_frame.button_combine
        self.button_add = self.buttons_frame.button_add
        self.button_delete = self.buttons_frame.button_delete
        self.button_edit = self.buttons_frame.button_edit

        # Botones del marco de formulario de datos
        self.button_save = self.data_form.button_guardar
        self.button_cancel = self.data_form.button_cancelar

        # Diccionario para acceder a los entrys del formulario
        self.entries = {
            "codigo": self.data_form.entry_codigo,
            "nombre": self.data_form.entry_nombre,
            "email": self.data_form.entry_email,
            "nombre_contacto": self.data_form.entry_nombre_contacto,
            "rfc": self.data_form.entry_rfc,
            "nombre_quiter": self.data_form.entry_nombre_quiter,
            "telefono": self.data_form.entry_telefono
        }

    # Métodos para obtener datos de la vista
    def get_search_text(self):
        return self.search_frame.search_bar.get_search_text()

    def get_incompletos(self):
        return self.search_frame.incomplete_var.get()
    
    # Metodos para rellenar la lista
    def clear_list(self):
        self.tree_frame.treeview.delete(*self.tree_frame.treeview.get_children())

    def fill_list(self, data):
        self.clear_list()
        for item in data:
            self.tree_frame.treeview.insert("", "end", values=item)

    def get_selection(self):
        selected_item = self.tree_frame.treeview.selection()
        if selected_item:
            return self.tree_frame.treeview.item(selected_item, "values")
        return None
    
    def get_selected_id(self):
        selected_item = self.tree_frame.treeview.selection()
        if selected_item:
            item_id = int(self.tree_frame.treeview.item(selected_item, "values")[0])
            return item_id
        return None

    def add_item(self, item):
        self.tree_frame.treeview.insert("", "end", values=item)

    def remove_selected(self):
        selected_item = self.tree_frame.treeview.selection()
        if selected_item:
            self.tree_frame.treeview.delete(selected_item)

    def modify_selected(self, new_values):
        selected_item = self.tree_frame.treeview.selection()
        if selected_item:
            self.tree_frame.treeview.item(selected_item, values=new_values)

    # Métodos para obtener datos del formulario
    def get_form_data(self):
        return {key: entry.get_search_text() if hasattr(entry, 'get_search_text') else entry.get() 
                for key, entry in self.entries.items()}
    
    def fill_form(self, data):
        for key, value in data.items():
            if key in self.entries:
                # Usar el método set_text del SearchBar para manejar correctamente placeholder vs datos reales
                self.entries[key].set_text(value)

    def clear_form(self):
        for entry in self.entries.values():
            entry.clear_search()

    def set_editable(self, editable):
        for entry in self.entries.values():
            entry.set_editable(editable) 