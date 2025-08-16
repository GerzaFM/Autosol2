"""
Vistas para la gestión de usuarios.
Contiene solo la interfaz de usuario.
"""
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import messagebox
from typing import Dict, List, Optional

class UsuariosView(tb.Frame):
    """
    Vista principal para la gestión de usuarios.
    Solo maneja la interfaz de usuario.
    """
    
    def __init__(self, parent, controller):
        """Inicializa la vista."""
        super().__init__(parent)
        self.controller = controller
        
        # Variables de estado de UI
        self.selected_user = None
        self.modo_edicion = False
        
        # Referencias a widgets
        self.tree = None
        self.form_entries = {}
        self.buttons = {}
        
        # Configurar callbacks del controller
        self._setup_controller_callbacks()
        
        # Crear interfaz
        self._create_interface()
    
    def _setup_controller_callbacks(self):
        """Configura los callbacks del controller."""
        self.controller.set_callbacks(
            on_usuarios_loaded=self._populate_tree,
            on_success_message=self._show_success,
            on_error_message=self._show_error
        )
    
    def _create_interface(self):
        """Crea la interfaz de usuario."""
        # Configurar grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Crear componentes
        self._create_header()
        self._create_main_content()
    
    def _create_header(self):
        """Crea el encabezado."""
        header_frame = tb.Frame(self, bootstyle="primary", padding=10)
        header_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        title_label = tb.Label(
            header_frame,
            text="👥 Administrador de Usuarios",
            font=("Segoe UI", 16, "bold"),
            bootstyle="inverse-primary"
        )
        title_label.pack(side=LEFT)
        
        # Botón de actualizar
        refresh_btn = tb.Button(
            header_frame,
            text="🔄 Actualizar",
            bootstyle="outline-light",
            command=self.refresh_usuarios
        )
        refresh_btn.pack(side=RIGHT, padx=5)
    
    def _create_main_content(self):
        """Crea el contenido principal."""
        main_frame = tb.Frame(self)
        main_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        main_frame.grid_columnconfigure(0, weight=2)
        main_frame.grid_columnconfigure(1, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)
        
        # Panel izquierdo - Lista de usuarios
        self._create_users_panel(main_frame)
        
        # Panel derecho - Formulario
        self._create_form_panel(main_frame)
    
    def _create_users_panel(self, parent):
        """Crea el panel de lista de usuarios."""
        panel = tb.Labelframe(parent, text="📋 Usuarios", padding=10)
        panel.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        panel.grid_rowconfigure(0, weight=1)
        panel.grid_columnconfigure(0, weight=1)
        
        # Crear Treeview
        columns = ("ID", "Usuario", "Email", "Rol", "Estado", "Creado")
        self.tree = tb.Treeview(panel, columns=columns, show="headings", height=15)
        
        # Configurar columnas
        self.tree.heading("ID", text="ID")
        self.tree.heading("Usuario", text="Usuario")
        self.tree.heading("Email", text="Email")
        self.tree.heading("Rol", text="Rol")
        self.tree.heading("Estado", text="Estado")
        self.tree.heading("Creado", text="Fecha Creación")
        
        # Ancho de columnas
        self.tree.column("ID", width=50, anchor=CENTER)
        self.tree.column("Usuario", width=100, anchor=W)
        self.tree.column("Email", width=200, anchor=W)
        self.tree.column("Rol", width=100, anchor=CENTER)
        self.tree.column("Estado", width=80, anchor=CENTER)
        self.tree.column("Creado", width=120, anchor=CENTER)
        
        # Scrollbar
        scrollbar = tb.Scrollbar(panel, orient=VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Grid
        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Bind eventos
        self.tree.bind("<<TreeviewSelect>>", self._on_user_select)
        self.tree.bind("<Double-1>", self._on_user_double_click)
    
    def _create_form_panel(self, parent):
        """Crea el panel del formulario."""
        panel = tb.Labelframe(parent, text="✏️ Formulario", padding=10)
        panel.grid(row=0, column=1, sticky="nsew")
        
        # Formulario
        self._create_form_fields(panel)
        
        # Botones
        self._create_form_buttons(panel)
    
    def _create_form_fields(self, parent):
        """Crea los campos del formulario."""
        form_frame = tb.Frame(parent)
        form_frame.pack(fill=BOTH, expand=True, pady=(0, 10))
        
        fields = [
            ("username", "👤 Usuario:", tb.Entry),
            ("email", "✉️ Email:", tb.Entry),
            ("password", "🔒 Contraseña:", lambda parent, **kwargs: tb.Entry(parent, show="*", **kwargs)),
            ("rol", "🎭 Rol:", lambda parent, **kwargs: tb.Combobox(parent, values=self.controller.get_roles(), state="readonly", **kwargs))
        ]
        
        for i, (field_name, label_text, widget_class) in enumerate(fields):
            # Label
            label = tb.Label(form_frame, text=label_text, font=("Segoe UI", 10))
            label.grid(row=i, column=0, sticky="w", pady=5, padx=(0, 10))
            
            # Widget
            widget = widget_class(form_frame, width=25, bootstyle="dark")
            widget.grid(row=i, column=1, sticky="ew", pady=5)
            
            self.form_entries[field_name] = widget
        
        # Checkbox activo
        self.activo_var = tb.BooleanVar(value=True)
        activo_check = tb.Checkbutton(
            form_frame,
            text="✅ Usuario activo",
            variable=self.activo_var,
            bootstyle="success"
        )
        activo_check.grid(row=len(fields), column=0, columnspan=2, sticky="w", pady=10)
        
        # Configurar grid
        form_frame.grid_columnconfigure(1, weight=1)
    
    def _create_form_buttons(self, parent):
        """Crea los botones del formulario."""
        buttons_frame = tb.Frame(parent)
        buttons_frame.pack(fill=X, pady=5)
        
        # Botones principales
        self.buttons["nuevo"] = tb.Button(
            buttons_frame,
            text="➕ Nuevo",
            bootstyle="success",
            command=self.nuevo_usuario
        )
        
        self.buttons["guardar"] = tb.Button(
            buttons_frame,
            text="💾 Guardar",
            bootstyle="primary", 
            command=self.guardar_usuario,
            state=DISABLED
        )
        
        self.buttons["editar"] = tb.Button(
            buttons_frame,
            text="✏️ Editar",
            bootstyle="warning",
            command=self.editar_usuario,
            state=DISABLED
        )
        
        self.buttons["eliminar"] = tb.Button(
            buttons_frame,
            text="🗑️ Eliminar",
            bootstyle="danger",
            command=self.eliminar_usuario,
            state=DISABLED
        )
        
        self.buttons["cancelar"] = tb.Button(
            buttons_frame,
            text="❌ Cancelar",
            bootstyle="secondary",
            command=self.cancelar_edicion,
            state=DISABLED
        )
        
        # Layout botones
        for i, button in enumerate(self.buttons.values()):
            button.pack(fill=X, pady=2)
    
    def _populate_tree(self, usuarios: List[Dict]):
        """Poblar el tree con los usuarios."""
        # Limpiar tree
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Insertar usuarios
        for usuario in usuarios:
            estado = "✅ Activo" if usuario.get("activo", True) else "❌ Inactivo"
            self.tree.insert("", "end", values=(
                usuario["id"],
                usuario["username"],
                usuario["email"],
                usuario["rol"],
                estado,
                usuario["fecha_creacion"]
            ))
    
    def _on_user_select(self, event):
        """Maneja la selección de usuario."""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            values = item["values"]
            
            self.selected_user = {
                "id": values[0],
                "username": values[1],
                "email": values[2],
                "rol": values[3],
                "activo": "Activo" in values[4],
                "fecha_creacion": values[5]
            }
            
            self._update_button_states()
        else:
            self.selected_user = None
            self._update_button_states()
    
    def _on_user_double_click(self, event):
        """Maneja doble clic en usuario."""
        if self.selected_user:
            self.editar_usuario()
    
    def _update_button_states(self):
        """Actualiza el estado de los botones."""
        if self.modo_edicion:
            # Modo edición
            self.buttons["nuevo"]["state"] = DISABLED
            self.buttons["guardar"]["state"] = NORMAL
            self.buttons["editar"]["state"] = DISABLED
            self.buttons["eliminar"]["state"] = DISABLED
            self.buttons["cancelar"]["state"] = NORMAL
        elif self.selected_user:
            # Usuario seleccionado
            self.buttons["nuevo"]["state"] = NORMAL
            self.buttons["guardar"]["state"] = DISABLED
            self.buttons["editar"]["state"] = NORMAL
            self.buttons["eliminar"]["state"] = NORMAL
            self.buttons["cancelar"]["state"] = DISABLED
        else:
            # Sin selección
            self.buttons["nuevo"]["state"] = NORMAL
            self.buttons["guardar"]["state"] = DISABLED
            self.buttons["editar"]["state"] = DISABLED
            self.buttons["eliminar"]["state"] = DISABLED
            self.buttons["cancelar"]["state"] = DISABLED
    
    def _clear_form(self):
        """Limpia el formulario."""
        for entry in self.form_entries.values():
            if hasattr(entry, 'delete'):
                entry.delete(0, 'end')
            elif hasattr(entry, 'set'):
                entry.set("")
        self.activo_var.set(True)
    
    def _fill_form(self, user_data: Dict):
        """Llena el formulario con datos del usuario."""
        self.form_entries["username"].delete(0, 'end')
        self.form_entries["username"].insert(0, user_data["username"])
        
        self.form_entries["email"].delete(0, 'end')
        self.form_entries["email"].insert(0, user_data["email"])
        
        self.form_entries["password"].delete(0, 'end')
        
        self.form_entries["rol"].set(user_data["rol"])
        
        self.activo_var.set(user_data["activo"])
    
    def _get_form_data(self) -> Dict:
        """Obtiene los datos del formulario."""
        return {
            "username": self.form_entries["username"].get().strip(),
            "email": self.form_entries["email"].get().strip(),
            "password": self.form_entries["password"].get().strip(),
            "rol": self.form_entries["rol"].get(),
            "activo": self.activo_var.get()
        }
    
    # Métodos públicos (comandos de botones)
    def refresh_usuarios(self):
        """Actualiza la lista de usuarios."""
        self.controller.load_usuarios()
    
    def nuevo_usuario(self):
        """Inicia creación de nuevo usuario."""
        self._clear_form()
        self.selected_user = None
        self.modo_edicion = True
        self._update_button_states()
        self.form_entries["username"].focus()
    
    def editar_usuario(self):
        """Inicia edición de usuario seleccionado."""
        if not self.selected_user:
            self._show_error("Seleccione un usuario para editar")
            return
        
        self._fill_form(self.selected_user)
        self.modo_edicion = True
        self._update_button_states()
        self.form_entries["username"].focus()
    
    def guardar_usuario(self):
        """Guarda usuario (crear o actualizar)."""
        form_data = self._get_form_data()
        
        if self.selected_user:
            # Actualizar usuario existente
            self.controller.update_usuario(self.selected_user["id"], form_data)
        else:
            # Crear nuevo usuario
            self.controller.create_usuario(form_data)
        
        # Resetear modo edición
        self.modo_edicion = False
        self._clear_form()
        self.selected_user = None
        self._update_button_states()
    
    def eliminar_usuario(self):
        """Elimina usuario seleccionado."""
        if not self.selected_user:
            self._show_error("Seleccione un usuario para eliminar")
            return
        
        # Confirmar eliminación
        result = messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Está seguro de eliminar el usuario '{self.selected_user['username']}'?\n\nEsta acción no se puede deshacer.",
            icon="warning"
        )
        
        if result:
            self.controller.delete_usuario(
                self.selected_user["id"], 
                self.selected_user["username"]
            )
            self.selected_user = None
            self._update_button_states()
    
    def cancelar_edicion(self):
        """Cancela la edición actual."""
        self.modo_edicion = False
        self._clear_form()
        self.selected_user = None
        self._update_button_states()
    
    def _show_success(self, message: str):
        """Muestra mensaje de éxito."""
        messagebox.showinfo("Éxito", message, icon="info")
    
    def _show_error(self, message: str):
        """Muestra mensaje de error."""
        messagebox.showerror("Error", message, icon="error")
    
    def inicializar(self):
        """Inicializa la vista cargando los datos."""
        self.controller.load_usuarios()
