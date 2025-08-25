from proveedoresapp.views.main_view import ProveedoreView
from proveedoresapp.models.model import ProveedorModel
import tkinter.messagebox as msgbox


class Controller:
    def __init__(self, model: ProveedorModel, view: ProveedoreView):
        self.model = model
        self.view = view

        self.proveedores = []

        # Cambiar botón search por refresh
        self.view.search_frame.button_search.config(command=self.refresh_proveedores)
        
        # Agregar búsqueda en tiempo real cuando el usuario escribe
        self.view.search_frame.search_bar.bind('<KeyRelease>', self._on_search_keyrelease)
        
        # Agregar funcionalidad al toggle de incompletos
        self.view.search_frame.incomplete_var.trace('w', self._on_incomplete_toggle)

        self.view.button_add.config(command=self.add_proveedor)
        self.view.button_delete.config(command=self.delete_proveedor)
        self.view.button_edit.config(command=self.edit_proveedor)
        self.view.button_combine.config(command=self.combine_proveedor)

        self.view.button_cancel.config(command=self.cancel_proveedor)
        self.view.button_save.config(command=self.save_proveedor)

        # Vincular evento de selección en la lista
        self.view.tree_frame.treeview.bind('<<TreeviewSelect>>', self.on_proveedor_select)

        self.view.set_editable(False)

        self.load_proveedores()
        self.fill_list(self.proveedores)

    def on_proveedor_select(self, event):
        """Maneja la selección de un proveedor en la lista."""
        # Ya no llenamos automáticamente el formulario al seleccionar
        # Solo se llenará cuando se presione el botón "Editar"
        pass

    def load_proveedores(self):
        self.proveedores = self.model.obtener_todos()

    def fill_list(self, proveedores):
        table_data = [list(proveedor.values()) for proveedor in proveedores]
        self.view.fill_list(table_data)

    def _on_search_keyrelease(self, event):
        """Búsqueda en tiempo real mientras el usuario escribe."""
        self.apply_filters()

    def _on_incomplete_toggle(self, *args):
        """Maneja el cambio del toggle de incompletos."""
        self.apply_filters()

    def apply_filters(self):
        """Aplica todos los filtros activos (búsqueda + incompletos)."""
        # Obtener el texto de búsqueda del searchbar
        query = self.view.search_frame.search_bar.get_search_text().strip().lower()
        # Obtener el estado del toggle incompletos
        show_incomplete = self.view.search_frame.incomplete_var.get()
        
        # Comenzar con todos los proveedores
        proveedores_filtrados = self.proveedores.copy()
        
        # Aplicar filtro de incompletos si está activado
        if show_incomplete:
            proveedores_filtrados = [
                proveedor for proveedor in proveedores_filtrados
                if self._is_proveedor_incomplete(proveedor)
            ]
        
        # Aplicar filtro de búsqueda si hay texto
        if query:
            proveedores_con_busqueda = []
            for proveedor in proveedores_filtrados:
                # Buscar en múltiples campos del proveedor
                campos_busqueda = [
                    str(proveedor.get('nombre', '')).lower(),
                    str(proveedor.get('codigo_quiter', '')).lower(),
                    str(proveedor.get('rfc', '')).lower(),
                    str(proveedor.get('nombre_en_quiter', '')).lower(),
                    str(proveedor.get('email', '')).lower(),
                ]
                
                # Si el query aparece en alguno de los campos, incluir el proveedor
                if any(query in campo for campo in campos_busqueda):
                    proveedores_con_busqueda.append(proveedor)
            
            proveedores_filtrados = proveedores_con_busqueda
        
        # Actualizar la lista con los resultados filtrados
        self.fill_list(proveedores_filtrados)

    def _is_proveedor_incomplete(self, proveedor):
        """Determina si un proveedor está incompleto (sin nombre o nombre_en_quiter)."""
        nombre = proveedor.get('nombre', '').strip()
        nombre_en_quiter = proveedor.get('nombre_en_quiter', '').strip()
        
        # Es incompleto si no tiene nombre O no tiene nombre_en_quiter
        return not nombre or not nombre_en_quiter

    def refresh_proveedores(self):
        """Recarga los proveedores desde la base de datos."""
        # Limpiar el searchbar
        self.view.search_frame.search_bar.clear_search()
        # Recargar datos desde la base de datos
        self.load_proveedores()
        # Aplicar filtros actuales (respeta el toggle incompletos)
        self.apply_filters()

    def search_proveedor(self):
        """Realiza búsqueda usando el nuevo sistema de filtros."""
        self.apply_filters()
    
    def add_proveedor(self):
        """Habilita el formulario para agregar un nuevo proveedor."""
        # Limpiar el formulario
        self.view.clear_form()
        # Habilitar edición
        self.view.set_editable(True)
        # Foco en el primer campo (código)
        if 'codigo' in self.view.entries:
            self.view.entries['codigo'].focus_set()

    def delete_proveedor(self):
        """Elimina el proveedor seleccionado."""
        selected_id = self.view.get_selected_id()
        if not selected_id:
            msgbox.showwarning("Advertencia", "Selecciona un proveedor para eliminar")
            return
        
        # Confirmar eliminación
        selection = self.view.get_selection()
        proveedor_nombre = selection[2] if len(selection) > 2 else "Sin nombre"  # Asumiendo que el nombre está en la posición 2
        
        if msgbox.askyesno("Confirmar eliminación", 
                          f"¿Estás seguro de eliminar el proveedor:\n{proveedor_nombre}?"):
            
            # Intentar eliminar
            exito, mensaje = self.model.eliminar_proveedor(selected_id)
            
            if exito:
                msgbox.showinfo("Éxito", mensaje)
                # Recargar la lista
                self.load_proveedores()
                self.apply_filters()
                # Limpiar formulario
                self.view.clear_form()
            else:
                msgbox.showerror("Error", f"No se pudo eliminar el proveedor:\n{mensaje}")

    def edit_proveedor(self):
        """Habilita la edición del proveedor seleccionado."""
        selected_id = self.view.get_selected_id()
        if not selected_id:
            msgbox.showwarning("Advertencia", "Selecciona un proveedor para editar")
            return
        
        # Habilitar edición PRIMERO
        self.view.set_editable(True)
        
        # Obtener datos completos del proveedor
        proveedor_data = self.model.obtener_por_id(selected_id)
        if not proveedor_data:
            msgbox.showerror("Error", "No se pudo obtener la información del proveedor")
            return
        
        # Llenar el formulario con los datos del proveedor
        form_data = {
            'codigo': str(proveedor_data.get('codigo_quiter', '')),
            'nombre': proveedor_data.get('nombre', ''),
            'email': proveedor_data.get('email', ''),
            'nombre_contacto': proveedor_data.get('nombre_contacto', ''),
            'rfc': proveedor_data.get('rfc', ''),
            'nombre_quiter': proveedor_data.get('nombre_en_quiter', ''),
            'telefono': proveedor_data.get('telefono', ''),
            'cuenta_mayor': str(proveedor_data.get('cuenta_mayor', ''))
        }
        
        self.view.fill_form(form_data)

    def save_proveedor(self):
        """Guarda el proveedor (nuevo o editado)."""
        # Obtener datos del formulario
        form_data = self.view.get_form_data()
        
        # Validar datos básicos
        if not form_data.get('codigo', '').strip():
            msgbox.showwarning("Advertencia", "El código es requerido")
            return
        
        # Preparar datos para el modelo (ajustar nombres de campos)
        datos_proveedor = {
            'codigo_quiter': form_data.get('codigo', '').strip(),
            'nombre': form_data.get('nombre', '').strip(),
            'nombre_en_quiter': form_data.get('nombre_quiter', '').strip(),
            'rfc': form_data.get('rfc', '').strip(),
            'telefono': form_data.get('telefono', '').strip(),
            'email': form_data.get('email', '').strip(),
            'nombre_contacto': form_data.get('nombre_contacto', '').strip(),
            'cuenta_mayor': form_data.get('cuenta_mayor', '').strip() or None
        }
        
        # Determinar si es nuevo o edición
        selected_id = self.view.get_selected_id()
        
        if selected_id:
            # Edición de proveedor existente
            exito, mensaje = self.model.actualizar_proveedor(selected_id, datos_proveedor)
        else:
            # Nuevo proveedor
            exito, mensaje, nuevo_id = self.model.crear_proveedor(datos_proveedor)
        
        if exito:
            msgbox.showinfo("Éxito", mensaje)
            # Recargar la lista
            self.load_proveedores()
            self.apply_filters()
            # Limpiar formulario y deshabilitar edición
            self.view.clear_form()
            self.view.set_editable(False)
        else:
            msgbox.showerror("Error", f"No se pudo guardar el proveedor:\n{mensaje}")

    def cancel_proveedor(self):
        """Cancela la edición/creación y vuelve al modo de visualización."""
        self.view.clear_form()
        self.view.set_editable(False)
        # Ya no llenamos automáticamente el formulario al cancelar

    def combine_proveedor(self):
        self.view.set_editable(False)
        pass