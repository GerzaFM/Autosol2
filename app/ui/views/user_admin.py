"""
Administrador de usuarios - Vista para gestionar usuarios del sistema.
"""
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from typing import Optional, Dict, List
import logging
import hashlib
from datetime import datetime
import re

from app.utils.logger import get_logger

# Importar modelos de la base de datos
try:
    from src.bd.models import Usuario, db
    from peewee import DoesNotExist, IntegrityError
except ImportError:
    # Fallback si no se puede importar
    Usuario = None
    db = None

class AdministradorUsuarios(tb.Frame):
    """
    Vista para administrar usuarios del sistema.
    Permite crear, editar, eliminar y gestionar usuarios.
    """
    
    def __init__(self, parent, db_manager, **kwargs):
        """
        Inicializa el administrador de usuarios.
        
        Args:
            parent: Widget padre
            db_manager: Gestor de base de datos
        """
        super().__init__(parent, **kwargs)
        
        self.logger = get_logger(__name__)
        self.db_manager = db_manager
        
        # Variables de estado
        self.usuarios_data: List[Dict] = []
        self.selected_user = None
        self.modo_edicion = False
        
        # Verificar disponibilidad de la base de datos
        self.db_disponible = Usuario is not None and db is not None
        if not self.db_disponible:
            self.logger.warning("Modelos de base de datos no disponibles, usando modo demo")
        
        # Roles disponibles (basados en el sistema)
        self.roles_disponibles = ["Administrador", "Usuario", "Supervisor", "Contador", "Gerente"]
        
        # Estados disponibles (personalizados para el sistema)
        self.estados_disponibles = ["Activo", "Inactivo", "Suspendido"]
        
        self._create_widgets()
        self._setup_layout()
        self._bind_events()
        
        self.logger.info("Administrador de usuarios inicializado")
    
    def _create_widgets(self):
        """Crea todos los widgets de la vista."""
        # Frame principal con padding
        self.main_frame = tb.Frame(self, padding=20)
        
        # Header con título y controles
        self.header_frame = tb.Frame(self.main_frame)
        
        # Título principal
        self.title_label = tb.Label(
            self.header_frame,
            text="👥 Administrador de Usuarios",
            font=("Segoe UI", 24, "bold"),
            bootstyle="inverse-primary"
        )
        
        # Subtítulo
        self.subtitle_label = tb.Label(
            self.header_frame,
            text="Gestión completa de usuarios del sistema",
            font=("Segoe UI", 12),
            bootstyle="inverse-secondary"
        )
        
        # Frame para controles superiores
        self.controls_frame = tb.Frame(self.header_frame)
        
        # Botones de acción
        self.btn_nuevo = tb.Button(
            self.controls_frame,
            text="➕ Nuevo Usuario",
            bootstyle="success",
            command=self._nuevo_usuario
        )
        
        self.btn_editar = tb.Button(
            self.controls_frame,
            text="✏️ Editar",
            bootstyle="warning",
            command=self._editar_usuario,
            state="disabled"
        )
        
        self.btn_eliminar = tb.Button(
            self.controls_frame,
            text="🗑️ Eliminar",
            bootstyle="danger",
            command=self._eliminar_usuario,
            state="disabled"
        )
        
        self.btn_cambiar_estado = tb.Button(
            self.controls_frame,
            text="🔄 Cambiar Estado",
            bootstyle="info",
            command=self._cambiar_estado_usuario,
            state="disabled"
        )
        
        self.btn_refrescar = tb.Button(
            self.controls_frame,
            text="🔄 Refrescar",
            bootstyle="secondary",
            command=self._refrescar_usuarios
        )
        
        # Frame central para contenido
        self.content_frame = tb.Frame(self.main_frame)
        
        # Frame izquierdo - Lista de usuarios
        self.left_frame = tb.LabelFrame(
            self.content_frame,
            text="👥 Lista de Usuarios",
            padding=10
        )
        
        # Treeview para mostrar usuarios
        self.tree_columns = ("Código", "Username", "Nombre", "Email", "Empresa", "Permisos", "Estado")
        self.tree = tb.Treeview(
            self.left_frame,
            columns=self.tree_columns,
            show="tree headings",
            height=15
        )
        
        # Configurar columnas del Treeview
        self.tree.heading("#0", text="", anchor=W)
        self.tree.column("#0", width=0, stretch=False)
        
        for col in self.tree_columns:
            self.tree.heading(col, text=col, anchor=W)
            if col == "Código":
                self.tree.column(col, width=60, stretch=False)
            elif col == "Username":
                self.tree.column(col, width=120, stretch=False)
            elif col == "Nombre":
                self.tree.column(col, width=180, stretch=True)
            elif col == "Email":
                self.tree.column(col, width=160, stretch=True)
            elif col == "Empresa":
                self.tree.column(col, width=80, stretch=False)
            elif col == "Permisos":
                self.tree.column(col, width=100, stretch=False)
            else:  # Estado
                self.tree.column(col, width=80, stretch=False)
        
        # Scrollbar para el Treeview
        self.tree_scrollbar = tb.Scrollbar(
            self.left_frame,
            orient=VERTICAL,
            command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=self.tree_scrollbar.set)
        
        # Frame para el formulario (simplificado, sin scroll)
        self.form_frame = tb.LabelFrame(
            self.main_frame,
            text="👤 Datos del Usuario",
            padding=15
        )
        
        # Crear Labels para el formulario
        self.lbl_username = tb.Label(self.form_frame, text="Username:")
        self.lbl_nombre = tb.Label(self.form_frame, text="Nombre Completo:")
        self.lbl_email = tb.Label(self.form_frame, text="Email:")
        self.lbl_password = tb.Label(self.form_frame, text="Contraseña:")
        self.lbl_empresa = tb.Label(self.form_frame, text="Código Empresa:")
        self.lbl_centro = tb.Label(self.form_frame, text="Centro:")
        self.lbl_sucursal = tb.Label(self.form_frame, text="Sucursal:")
        self.lbl_marca = tb.Label(self.form_frame, text="Marca:")
        self.lbl_permisos = tb.Label(self.form_frame, text="Permisos:")
        self.lbl_estado = tb.Label(self.form_frame, text="Estado:")
        
        # Crear Entry widgets para el formulario
        self.entry_username = tb.Entry(self.form_frame, width=20)
        self.entry_nombre = tb.Entry(self.form_frame, width=25)
        self.entry_email = tb.Entry(self.form_frame, width=25)
        self.entry_password = tb.Entry(self.form_frame, width=15, show="*")
        self.entry_empresa = tb.Entry(self.form_frame, width=15)
        self.entry_centro = tb.Entry(self.form_frame, width=15)
        self.entry_sucursal = tb.Entry(self.form_frame, width=15)
        self.entry_marca = tb.Entry(self.form_frame, width=15)
        
        # Crear Combobox widgets
        self.combo_permisos = tb.Combobox(
            self.form_frame,
            values=self.roles_disponibles,
            state="readonly",
            width=18
        )
        self.combo_estado = tb.Combobox(
            self.form_frame,
            values=self.estados_disponibles,
            state="readonly",
            width=18
        )
        
        # Botón para mostrar/ocultar contraseña
        self.btn_mostrar_pass = tb.Button(
            self.form_frame,
            text="👁️",
            width=3,
            command=self._toggle_password_visibility
        )
        
        # Frame para botones del formulario
        self.btn_guardar = tb.Button(
            self.form_frame,
            text="💾 Guardar Usuario",
            bootstyle="success",
            command=self._guardar_usuario
        )
        
        self.btn_cancelar = tb.Button(
            self.form_frame,
            text="❌ Cancelar",
            bootstyle="secondary",
            command=self._cancelar_edicion
        )
        
        # Frame inferior para información
        self.info_frame = tb.Frame(self.main_frame)
        
        self.info_label = tb.Label(
            self.info_frame,
            text="Selecciona un usuario de la lista para ver/editar sus detalles",
            font=("Segoe UI", 10),
            bootstyle="inverse-secondary"
        )
    
    def _setup_layout(self):
        """Configura la disposición de los widgets."""
        # Frame principal
        self.main_frame.pack(fill=BOTH, expand=True)
        
        # Header
        self.header_frame.pack(fill=X, pady=(0, 20))
        
        # Título y subtítulo
        self.title_label.pack(anchor=W)
        self.subtitle_label.pack(anchor=W, pady=(5, 15))
        
        # Controles
        self.controls_frame.pack(fill=X)
        self.btn_nuevo.pack(side=LEFT, padx=(0, 10))
        self.btn_editar.pack(side=LEFT, padx=(0, 10))
        self.btn_eliminar.pack(side=LEFT, padx=(0, 10))
        self.btn_cambiar_estado.pack(side=LEFT, padx=(0, 10))
        self.btn_refrescar.pack(side=LEFT)
        
        # Contenido central
        self.content_frame.pack(fill=BOTH, expand=True, pady=20)
        
        # Frame de usuarios (parte superior)
        self.left_frame.pack(fill=BOTH, expand=True, pady=(0, 10))
        
        # Treeview y scrollbar
        self.tree.pack(side=LEFT, fill=BOTH, expand=True)
        self.tree_scrollbar.pack(side=RIGHT, fill=Y)
        
        # Frame del formulario (parte inferior)
        self.form_frame.pack(fill=X, pady=(10, 0))
        
        # Organizar campos del formulario en columnas para ahorrar espacio
        # Primera fila: Username, Nombre, Email
        primera_fila = tb.Frame(self.form_frame)
        primera_fila.pack(fill=X, pady=(0, 10))
        
        # Columna 1: Username
        col1_frame = tb.Frame(primera_fila)
        col1_frame.pack(side=LEFT, fill=X, expand=True, padx=(0, 10))
        self.lbl_username.pack(in_=col1_frame, anchor=W)
        self.entry_username.pack(in_=col1_frame, fill=X)
        
        # Columna 2: Nombre
        col2_frame = tb.Frame(primera_fila)
        col2_frame.pack(side=LEFT, fill=X, expand=True, padx=(0, 10))
        self.lbl_nombre.pack(in_=col2_frame, anchor=W)
        self.entry_nombre.pack(in_=col2_frame, fill=X)
        
        # Columna 3: Email
        col3_frame = tb.Frame(primera_fila)
        col3_frame.pack(side=LEFT, fill=X, expand=True)
        self.lbl_email.pack(in_=col3_frame, anchor=W)
        self.entry_email.pack(in_=col3_frame, fill=X)
        
        # Segunda fila: Contraseña, Empresa, Centro, Sucursal
        segunda_fila = tb.Frame(self.form_frame)
        segunda_fila.pack(fill=X, pady=(0, 10))
        
        # Columna 1: Contraseña
        col4_frame = tb.Frame(segunda_fila)
        col4_frame.pack(side=LEFT, fill=X, expand=True, padx=(0, 10))
        self.lbl_password.pack(in_=col4_frame, anchor=W)
        password_entry_frame = tb.Frame(col4_frame)
        password_entry_frame.pack(fill=X)
        self.entry_password.pack(in_=password_entry_frame, side=LEFT, fill=X, expand=True, padx=(0, 5))
        self.btn_mostrar_pass.pack(in_=password_entry_frame, side=RIGHT)
        
        # Columna 2: Empresa
        col5_frame = tb.Frame(segunda_fila)
        col5_frame.pack(side=LEFT, fill=X, expand=True, padx=(0, 10))
        self.lbl_empresa.pack(in_=col5_frame, anchor=W)
        self.entry_empresa.pack(in_=col5_frame, fill=X)
        
        # Columna 3: Centro
        col6_frame = tb.Frame(segunda_fila)
        col6_frame.pack(side=LEFT, fill=X, expand=True, padx=(0, 10))
        self.lbl_centro.pack(in_=col6_frame, anchor=W)
        self.entry_centro.pack(in_=col6_frame, fill=X)
        
        # Columna 4: Sucursal
        col7_frame = tb.Frame(segunda_fila)
        col7_frame.pack(side=LEFT, fill=X, expand=True)
        self.lbl_sucursal.pack(in_=col7_frame, anchor=W)
        self.entry_sucursal.pack(in_=col7_frame, fill=X)
        
        # Tercera fila: Marca, Permisos, Estado, Botones
        tercera_fila = tb.Frame(self.form_frame)
        tercera_fila.pack(fill=X, pady=(0, 10))
        
        # Columna 1: Marca
        col8_frame = tb.Frame(tercera_fila)
        col8_frame.pack(side=LEFT, fill=X, expand=True, padx=(0, 10))
        self.lbl_marca.pack(in_=col8_frame, anchor=W)
        self.entry_marca.pack(in_=col8_frame, fill=X)
        
        # Columna 2: Permisos
        col9_frame = tb.Frame(tercera_fila)
        col9_frame.pack(side=LEFT, fill=X, expand=True, padx=(0, 10))
        self.lbl_permisos.pack(in_=col9_frame, anchor=W)
        self.combo_permisos.pack(in_=col9_frame, fill=X)
        
        # Columna 3: Estado
        col10_frame = tb.Frame(tercera_fila)
        col10_frame.pack(side=LEFT, fill=X, expand=True, padx=(0, 10))
        self.lbl_estado.pack(in_=col10_frame, anchor=W)
        self.combo_estado.pack(in_=col10_frame, fill=X)
        
        # Columna 4: Botones
        col11_frame = tb.Frame(tercera_fila)
        col11_frame.pack(side=LEFT, fill=X, expand=True)
        
        # Espacio para alinear botones con los otros campos
        tb.Label(col11_frame, text="").pack(anchor=W)
        
        # Frame para botones del formulario
        buttons_frame = tb.Frame(col11_frame)
        buttons_frame.pack(fill=X)
        
        self.btn_guardar.pack(in_=buttons_frame, side=LEFT, padx=(0, 5))
        self.btn_cancelar.pack(in_=buttons_frame, side=LEFT)
        
        # Info inferior
        self.info_frame.pack(fill=X, pady=(20, 0))
        self.info_label.pack()
    
    def _bind_events(self):
        """Vincula eventos a los widgets."""
        # Selección en el Treeview
        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)
        
        # Doble clic para editar
        self.tree.bind("<Double-1>", lambda e: self._editar_usuario())
        
        # Validación en tiempo real de email
        self.entry_email.bind("<KeyRelease>", self._validar_email)
        
        # Validación numérica para campos organizacionales
        self.entry_empresa.bind("<KeyRelease>", self._validar_numerico)
        self.entry_centro.bind("<KeyRelease>", self._validar_numerico)
        self.entry_sucursal.bind("<KeyRelease>", self._validar_numerico)
        self.entry_marca.bind("<KeyRelease>", self._validar_numerico)
    
    def _validar_numerico(self, event):
        """Valida que el campo contenga solo números."""
        entry = event.widget
        valor = entry.get()
        if valor and not valor.isdigit():
            entry.config(bootstyle="danger")
        else:
            entry.config(bootstyle="default")
    
    def _toggle_password_visibility(self):
        """Alterna la visibilidad de la contraseña."""
        if self.entry_password.cget("show") == "*":
            self.entry_password.config(show="")
            self.btn_mostrar_pass.config(text="🙈")
        else:
            self.entry_password.config(show="*")
            self.btn_mostrar_pass.config(text="👁️")
    
    def _validar_email(self, event):
        """Valida el formato del email en tiempo real."""
        email = self.entry_email.get()
        if email and not self._es_email_valido(email):
            self.entry_email.config(bootstyle="danger")
        else:
            self.entry_email.config(bootstyle="default")
    
    def _es_email_valido(self, email: str) -> bool:
        """Valida el formato de un email."""
        patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(patron, email) is not None
    
    def _generar_hash_password(self, password: str) -> str:
        """Genera un hash seguro de la contraseña."""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _nuevo_usuario(self):
        """Crea un nuevo usuario."""
        self.logger.info("Creando nuevo usuario")
        self.modo_edicion = False
        self.selected_user = None
        
        # Limpiar formulario
        self._limpiar_formulario()
        
        # Establecer valores por defecto
        self.combo_permisos.set("Usuario")
        self.combo_estado.set("Activo")
        self.entry_empresa.insert(0, "1")  # Valor por defecto
        self.entry_centro.insert(0, "1")
        self.entry_sucursal.insert(0, "1")
        self.entry_marca.insert(0, "1")
        
        self.entry_username.focus()
        self.info_label.config(text="Ingresa los datos del nuevo usuario")
    
    def _editar_usuario(self):
        """Edita el usuario seleccionado."""
        if not self.selected_user:
            return
        
        self.logger.info(f"Editando usuario: {self.selected_user}")
        self.modo_edicion = True
        
        if self.db_disponible:
            # Buscar usuario en la base de datos
            try:
                usuario = Usuario.get(Usuario.codigo == int(self.selected_user))
                
                # Cargar datos en el formulario
                self.entry_username.delete(0, END)
                self.entry_username.insert(0, usuario.username)
                
                self.entry_nombre.delete(0, END)
                self.entry_nombre.insert(0, usuario.nombre)
                
                self.entry_email.delete(0, END)
                self.entry_email.insert(0, usuario.email or "")
                
                # No cargar la contraseña por seguridad
                self.entry_password.delete(0, END)
                
                self.entry_empresa.delete(0, END)
                self.entry_empresa.insert(0, str(usuario.empresa))
                
                self.entry_centro.delete(0, END)
                self.entry_centro.insert(0, str(usuario.centro))
                
                self.entry_sucursal.delete(0, END)
                self.entry_sucursal.insert(0, str(usuario.sucursal))
                
                self.entry_marca.delete(0, END)
                self.entry_marca.insert(0, str(usuario.marca))
                
                self.combo_permisos.set(usuario.permisos or "Usuario")
                self.combo_estado.set("Activo")  # Por defecto, ya que no está en el modelo
                
                self.entry_username.focus()
                self.info_label.config(text=f"Editando usuario: {usuario.nombre}")
                
            except DoesNotExist:
                from tkinter import messagebox
                messagebox.showerror("Error", "Usuario no encontrado en la base de datos")
                return
        else:
            # Usar datos en memoria para modo demo
            usuario_data = None
            for usuario in self.usuarios_data:
                if usuario['codigo'] == int(self.selected_user):
                    usuario_data = usuario
                    break
            
            if not usuario_data:
                return
            
            # Cargar datos en el formulario
            self.entry_username.delete(0, END)
            self.entry_username.insert(0, usuario_data['username'])
            
            self.entry_nombre.delete(0, END)
            self.entry_nombre.insert(0, usuario_data['nombre'])
            
            self.entry_email.delete(0, END)
            self.entry_email.insert(0, usuario_data.get('email', ''))
            
            # No cargar la contraseña por seguridad
            self.entry_password.delete(0, END)
            
            self.entry_empresa.delete(0, END)
            self.entry_empresa.insert(0, str(usuario_data['empresa']))
            
            self.entry_centro.delete(0, END)
            self.entry_centro.insert(0, str(usuario_data['centro']))
            
            self.entry_sucursal.delete(0, END)
            self.entry_sucursal.insert(0, str(usuario_data['sucursal']))
            
            self.entry_marca.delete(0, END)
            self.entry_marca.insert(0, str(usuario_data['marca']))
            
            self.combo_permisos.set(usuario_data.get('permisos', 'Usuario'))
            self.combo_estado.set(usuario_data.get('estado', 'Activo'))
            
            self.entry_username.focus()
            self.info_label.config(text=f"Editando usuario: {usuario_data['nombre']}")
    
    def _eliminar_usuario(self):
        """Elimina el usuario seleccionado."""
        if not self.selected_user:
            return
        
        if self.db_disponible:
            try:
                usuario = Usuario.get(Usuario.codigo == int(self.selected_user))
                
                # Confirmación
                from tkinter import messagebox
                if messagebox.askyesno(
                    "Confirmar Eliminación", 
                    f"¿Está seguro de eliminar al usuario '{usuario.nombre}'?\n\nEsta acción no se puede deshacer."
                ):
                    usuario.delete_instance()
                    
                    # Actualizar vista
                    self._cargar_usuarios_desde_bd()
                    self._limpiar_formulario()
                    self.selected_user = None
                    self._actualizar_botones()
                    
                    self.info_label.config(text=f"Usuario '{usuario.nombre}' eliminado de la base de datos")
                    self.logger.info(f"Usuario eliminado de BD: {usuario.nombre}")
                    
            except DoesNotExist:
                from tkinter import messagebox
                messagebox.showerror("Error", "Usuario no encontrado en la base de datos")
            except Exception as e:
                from tkinter import messagebox
                messagebox.showerror("Error", f"Error al eliminar usuario: {str(e)}")
                self.logger.error(f"Error al eliminar usuario: {e}")
        else:
            # Modo demo - eliminar de memoria
            usuario_data = None
            for usuario in self.usuarios_data:
                if usuario['codigo'] == int(self.selected_user):
                    usuario_data = usuario
                    break
            
            if not usuario_data:
                return
            
            # Confirmación
            from tkinter import messagebox
            if messagebox.askyesno(
                "Confirmar Eliminación", 
                f"¿Está seguro de eliminar al usuario '{usuario_data['nombre']}'?\n\nEsta acción no se puede deshacer."
            ):
                # Eliminar de la lista
                self.usuarios_data = [u for u in self.usuarios_data if u['codigo'] != int(self.selected_user)]
                
                # Actualizar vista
                self._actualizar_vista_usuarios()
                self._limpiar_formulario()
                self.selected_user = None
                self._actualizar_botones()
                
                self.info_label.config(text=f"Usuario '{usuario_data['nombre']}' eliminado (modo demo)")
                self.logger.info(f"Usuario eliminado de memoria: {usuario_data['nombre']}")
    
    def _cambiar_estado_usuario(self):
        """Cambia el estado del usuario seleccionado (solo en modo demo)."""
        if not self.selected_user:
            return
        
        if self.db_disponible:
            from tkinter import messagebox
            messagebox.showinfo("Información", "Esta funcionalidad requiere agregar un campo 'estado' al modelo Usuario en la base de datos.")
            return
        
        # Buscar datos del usuario en memoria
        usuario_data = None
        for usuario in self.usuarios_data:
            if usuario['codigo'] == int(self.selected_user):
                usuario_data = usuario
                break
        
        if not usuario_data:
            return
        
        # Determinar nuevo estado
        estado_actual = usuario_data.get('estado', 'Activo')
        if estado_actual == "Activo":
            nuevo_estado = "Inactivo"
        elif estado_actual == "Inactivo":
            nuevo_estado = "Activo"
        else:  # Suspendido
            nuevo_estado = "Activo"
        
        # Confirmación
        from tkinter import messagebox
        if messagebox.askyesno(
            "Cambiar Estado", 
            f"¿Cambiar estado de '{usuario_data['nombre']}' de '{estado_actual}' a '{nuevo_estado}'?"
        ):
            usuario_data['estado'] = nuevo_estado
            self._actualizar_vista_usuarios()
            self.info_label.config(text=f"Estado cambiado a '{nuevo_estado}' para {usuario_data['nombre']}")
            self.logger.info(f"Estado cambiado para usuario {usuario_data['nombre']}: {estado_actual} -> {nuevo_estado}")
    
    def _refrescar_usuarios(self):
        """Refresca los datos de usuarios."""
        self.logger.info("Refrescando datos de usuarios")
        if self.db_disponible:
            self._cargar_usuarios_desde_bd()
            self.info_label.config(text="Lista de usuarios actualizada desde la base de datos")
        else:
            self._cargar_usuarios_ejemplo()
            self.info_label.config(text="Lista de usuarios actualizada (modo demo)")
    
    def _on_tree_select(self, event):
        """Maneja la selección en el Treeview."""
        selection = self.tree.selection()
        if selection:
            item_id = selection[0]
            values = self.tree.item(item_id, "values")
            if values:
                self.selected_user = values[0]  # Código del usuario
                self.info_label.config(text=f"Seleccionado: {values[2]} ({values[1]})")  # Nombre (Username)
        else:
            self.selected_user = None
            self.info_label.config(text="Ningún usuario seleccionado")
        
        self._actualizar_botones()
    
    def _actualizar_botones(self):
        """Actualiza el estado de los botones según la selección."""
        if self.selected_user:
            self.btn_editar.config(state="normal")
            self.btn_eliminar.config(state="normal")
            self.btn_cambiar_estado.config(state="normal")
        else:
            self.btn_editar.config(state="disabled")
            self.btn_eliminar.config(state="disabled")
            self.btn_cambiar_estado.config(state="disabled")
    
    def _limpiar_formulario(self):
        """Limpia los campos del formulario."""
        self.entry_username.delete(0, END)
        self.entry_nombre.delete(0, END)
        self.entry_email.delete(0, END)
        self.entry_password.delete(0, END)
        self.entry_empresa.delete(0, END)
        self.entry_centro.delete(0, END)
        self.entry_sucursal.delete(0, END)
        self.entry_marca.delete(0, END)
        self.combo_permisos.set("")
        self.combo_estado.set("")
        
        # Restablecer visibilidad de contraseña
        self.entry_password.config(show="*")
        self.btn_mostrar_pass.config(text="👁️")
        
        # Restablecer colores
        self.entry_email.config(bootstyle="default")
        self.entry_empresa.config(bootstyle="default")
        self.entry_centro.config(bootstyle="default")
        self.entry_sucursal.config(bootstyle="default")
        self.entry_marca.config(bootstyle="default")
    
    def _actualizar_vista_usuarios(self):
        """Actualiza la vista del Treeview con los datos de usuarios."""
        # Limpiar vista actual
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Agregar usuarios
        for usuario in self.usuarios_data:
            # Determinar color según estado o permisos
            tags = []
            if usuario.get('estado') == 'Inactivo':
                tags = ['inactivo']
            elif usuario.get('estado') == 'Suspendido':
                tags = ['suspendido']
            elif usuario.get('permisos') == 'Administrador':
                tags = ['admin']
            
            # Usar los campos del modelo Usuario
            self.tree.insert("", END, values=(
                usuario.get('codigo', ''),
                usuario.get('username', ''),
                usuario.get('nombre', ''),
                usuario.get('email', ''),
                usuario.get('empresa', ''),
                usuario.get('permisos', ''),
                usuario.get('estado', 'Activo')
            ), tags=tags)
        
        # Configurar colores para los tags
        self.tree.tag_configure('inactivo', foreground='gray')
        self.tree.tag_configure('suspendido', foreground='red')
        self.tree.tag_configure('admin', foreground='blue', font=('Segoe UI', 9, 'bold'))
    
    def _cargar_usuarios_desde_bd(self):
        """Carga usuarios desde la base de datos real."""
        if not self.db_disponible:
            self.logger.warning("Base de datos no disponible, cargando usuarios de ejemplo")
            self._cargar_usuarios_ejemplo()
            return
        
        try:
            # Limpiar datos existentes
            self.usuarios_data.clear()
            
            # Cargar usuarios desde la base de datos
            usuarios = Usuario.select()
            
            for usuario in usuarios:
                usuario_dict = {
                    'codigo': usuario.codigo,
                    'username': usuario.username,
                    'nombre': usuario.nombre,
                    'email': usuario.email,
                    'empresa': usuario.empresa,
                    'centro': usuario.centro,
                    'sucursal': usuario.sucursal,
                    'marca': usuario.marca,
                    'permisos': usuario.permisos,
                    'password_hash': usuario.password,
                    'estado': 'Activo'  # Campo personalizado, no está en el modelo original
                }
                self.usuarios_data.append(usuario_dict)
            
            self._actualizar_vista_usuarios()
            self.logger.info(f"Usuarios cargados desde BD: {len(self.usuarios_data)}")
            
        except Exception as e:
            self.logger.error(f"Error al cargar usuarios desde BD: {e}")
            # Fallback a usuarios de ejemplo
            self._cargar_usuarios_ejemplo()
    
    def _cargar_usuarios_ejemplo(self):
        """Carga usuarios de ejemplo compatibles con el modelo Usuario."""
        # Limpiar datos existentes
        self.usuarios_data.clear()
        
        # Usuarios de ejemplo basados en el modelo real
        usuarios_ejemplo = [
            {
                'codigo': 1,
                'username': 'admin',
                'nombre': 'Administrador Sistema',
                'email': 'admin@tcm-matehuala.com',
                'password_hash': self._generar_hash_password('admin123'),
                'empresa': 1,
                'centro': 1,
                'sucursal': 1,
                'marca': 1,
                'permisos': 'Administrador',
                'estado': 'Activo'
            },
            {
                'codigo': 2,
                'username': 'juan.perez',
                'nombre': 'Juan Pérez Martínez',
                'email': 'juan.perez@tcm-matehuala.com',
                'password_hash': self._generar_hash_password('usuario123'),
                'empresa': 1,
                'centro': 1,
                'sucursal': 1,
                'marca': 2,
                'permisos': 'Usuario',
                'estado': 'Activo'
            },
            {
                'codigo': 3,
                'username': 'maria.lopez',
                'nombre': 'María López García',
                'email': 'maria.lopez@tcm-matehuala.com',
                'password_hash': self._generar_hash_password('supervisor123'),
                'empresa': 1,
                'centro': 1,
                'sucursal': 2,
                'marca': 1,
                'permisos': 'Supervisor',
                'estado': 'Activo'
            },
            {
                'codigo': 4,
                'username': 'carlos.ruiz',
                'nombre': 'Carlos Ruiz Sánchez',
                'email': 'carlos.ruiz@tcm-matehuala.com',
                'password_hash': self._generar_hash_password('contador123'),
                'empresa': 1,
                'centro': 2,
                'sucursal': 1,
                'marca': 1,
                'permisos': 'Contador',
                'estado': 'Inactivo'
            },
            {
                'codigo': 5,
                'username': 'ana.gonzalez',
                'nombre': 'Ana González Morales',
                'email': 'ana.gonzalez@tcm-matehuala.com',
                'password_hash': self._generar_hash_password('gerente123'),
                'empresa': 1,
                'centro': 1,
                'sucursal': 1,
                'marca': 3,
                'permisos': 'Gerente',
                'estado': 'Suspendido'
            }
        ]
        
        self.usuarios_data = usuarios_ejemplo
        self._actualizar_vista_usuarios()
        
        self.logger.info("Usuarios de ejemplo cargados (compatibles con modelo Usuario)")
    
    def _guardar_usuario(self):
        """Guarda el usuario actual (nuevo o editado)."""
        # Validar campos obligatorios
        username = self.entry_username.get().strip()
        nombre = self.entry_nombre.get().strip()
        email = self.entry_email.get().strip()
        password = self.entry_password.get().strip()
        
        if not username:
            from tkinter import messagebox
            messagebox.showerror("Error", "El username es obligatorio")
            self.entry_username.focus()
            return
        
        if not nombre:
            from tkinter import messagebox
            messagebox.showerror("Error", "El nombre es obligatorio")
            self.entry_nombre.focus()
            return
        
        # Validar email si se proporcionó
        if email and not self._es_email_valido(email):
            from tkinter import messagebox
            messagebox.showerror("Error", "El formato del email no es válido")
            self.entry_email.focus()
            return
        
        # Validar contraseña para nuevos usuarios
        if not self.modo_edicion and not password:
            from tkinter import messagebox
            messagebox.showerror("Error", "La contraseña es obligatoria para nuevos usuarios")
            self.entry_password.focus()
            return
        
        # Obtener valores de los campos
        empresa = self.entry_empresa.get().strip() or "1"
        centro = self.entry_centro.get().strip() or "1"
        sucursal = self.entry_sucursal.get().strip() or "1"
        marca = self.entry_marca.get().strip() or "1"
        permisos = self.combo_permisos.get() or "Usuario"
        estado = self.combo_estado.get() or "Activo"
        
        # Validar campos numéricos
        try:
            empresa = int(empresa)
            centro = int(centro)
            sucursal = int(sucursal)
            marca = int(marca)
        except ValueError:
            from tkinter import messagebox
            messagebox.showerror("Error", "Los campos Empresa, Centro, Sucursal y Marca deben ser números")
            return
        
        if self.db_disponible:
            self._guardar_usuario_bd(username, nombre, email, password, empresa, centro, sucursal, marca, permisos, estado)
        else:
            self._guardar_usuario_memoria(username, nombre, email, password, empresa, centro, sucursal, marca, permisos, estado)
    
    def _guardar_usuario_bd(self, username, nombre, email, password, empresa, centro, sucursal, marca, permisos, estado):
        """Guarda usuario en la base de datos."""
        try:
            if self.modo_edicion:
                # Actualizar usuario existente
                usuario = Usuario.get(Usuario.codigo == int(self.selected_user))
                
                # Verificar si el username ya existe en otro usuario
                try:
                    usuario_existente = Usuario.get(Usuario.username == username)
                    if usuario_existente.codigo != usuario.codigo:
                        from tkinter import messagebox
                        messagebox.showerror("Error", f"El username '{username}' ya está en uso")
                        return
                except DoesNotExist:
                    pass  # Username disponible
                
                # Actualizar campos
                usuario.username = username
                usuario.nombre = nombre
                usuario.email = email if email else None
                usuario.empresa = empresa
                usuario.centro = centro
                usuario.sucursal = sucursal
                usuario.marca = marca
                usuario.permisos = permisos
                
                # Actualizar contraseña solo si se proporcionó una nueva
                if password:
                    usuario.password = self._generar_hash_password(password)
                
                usuario.save()
                
                self.info_label.config(text=f"Usuario '{nombre}' actualizado en la base de datos")
                self.logger.info(f"Usuario actualizado en BD: {nombre}")
                
            else:
                # Crear nuevo usuario
                try:
                    # Verificar si el username ya existe
                    Usuario.get(Usuario.username == username)
                    from tkinter import messagebox
                    messagebox.showerror("Error", f"El username '{username}' ya está en uso")
                    return
                except DoesNotExist:
                    pass  # Username disponible
                
                # Crear nuevo usuario
                usuario = Usuario.create(
                    username=username,
                    nombre=nombre,
                    email=email if email else None,
                    password=self._generar_hash_password(password),
                    empresa=empresa,
                    centro=centro,
                    sucursal=sucursal,
                    marca=marca,
                    permisos=permisos
                )
                
                self.info_label.config(text=f"Usuario '{nombre}' creado exitosamente en la base de datos")
                self.logger.info(f"Nuevo usuario creado en BD: {nombre}")
            
            # Recargar usuarios y limpiar formulario
            self._cargar_usuarios_desde_bd()
            self._limpiar_formulario()
            self.modo_edicion = False
            self.selected_user = None
            self._actualizar_botones()
            
        except IntegrityError as e:
            from tkinter import messagebox
            messagebox.showerror("Error", f"Error de integridad en la base de datos: {str(e)}")
            self.logger.error(f"Error de integridad al guardar usuario: {e}")
        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror("Error", f"Error al guardar usuario: {str(e)}")
            self.logger.error(f"Error al guardar usuario: {e}")
    
    def _guardar_usuario_memoria(self, username, nombre, email, password, empresa, centro, sucursal, marca, permisos, estado):
        """Guarda usuario en memoria para modo demo."""
        # Verificar username duplicado
        for usuario in self.usuarios_data:
            if usuario['username'] == username and (not self.modo_edicion or usuario['codigo'] != int(self.selected_user)):
                from tkinter import messagebox
                messagebox.showerror("Error", f"El username '{username}' ya está en uso")
                return
        
        # Preparar datos del usuario
        datos_usuario = {
            'username': username,
            'nombre': nombre,
            'email': email,
            'empresa': empresa,
            'centro': centro,
            'sucursal': sucursal,
            'marca': marca,
            'permisos': permisos,
            'estado': estado
        }
        
        # Agregar contraseña si se proporcionó
        if password:
            datos_usuario['password_hash'] = self._generar_hash_password(password)
        
        if self.modo_edicion:
            # Actualizar usuario existente
            for usuario in self.usuarios_data:
                if usuario['codigo'] == int(self.selected_user):
                    # Mantener la contraseña existente si no se proporcionó una nueva
                    if not password:
                        datos_usuario['password_hash'] = usuario.get('password_hash', '')
                    usuario.update(datos_usuario)
                    break
            self.info_label.config(text=f"Usuario '{nombre}' actualizado (modo demo)")
            self.logger.info(f"Usuario actualizado en memoria: {nombre}")
        else:
            # Crear nuevo usuario
            nuevo_codigo = max([u['codigo'] for u in self.usuarios_data], default=0) + 1
            datos_usuario['codigo'] = nuevo_codigo
            
            self.usuarios_data.append(datos_usuario)
            self.info_label.config(text=f"Usuario '{nombre}' creado exitosamente (modo demo)")
            self.logger.info(f"Nuevo usuario creado en memoria: {nombre}")
        
        # Actualizar vista y limpiar formulario
        self._actualizar_vista_usuarios()
        self._limpiar_formulario()
        self.modo_edicion = False
        self.selected_user = None
        self._actualizar_botones()
    
    def _get_usuario_actual(self) -> Optional[Dict]:
        """Obtiene los datos del usuario actualmente seleccionado."""
        if not self.selected_user:
            return None
        
        for usuario in self.usuarios_data:
            if usuario['codigo'] == int(self.selected_user):
                return usuario
        return None
    
    def _cancelar_edicion(self):
        """Cancela la edición actual."""
        self._limpiar_formulario()
        self.modo_edicion = False
        self.selected_user = None
        self._actualizar_botones()
        self.info_label.config(text="Edición cancelada")
    
    def inicializar(self):
        """Inicializa la vista cargando usuarios."""
        if self.db_disponible:
            self._cargar_usuarios_desde_bd()
            total_usuarios = len(self.usuarios_data)
            self.info_label.config(text=f"Conectado a BD - Total: {total_usuarios} usuarios")
        else:
            self._cargar_usuarios_ejemplo()
            total_usuarios = len(self.usuarios_data)
            self.info_label.config(text=f"Modo Demo - Total: {total_usuarios} usuarios de ejemplo")
    
    def obtener_estadisticas(self) -> Dict:
        """Obtiene estadísticas de usuarios."""
        total = len(self.usuarios_data)
        activos = len([u for u in self.usuarios_data if u.get('estado', 'Activo') == 'Activo'])
        inactivos = len([u for u in self.usuarios_data if u.get('estado') == 'Inactivo'])
        suspendidos = len([u for u in self.usuarios_data if u.get('estado') == 'Suspendido'])
        
        permisos = {}
        for usuario in self.usuarios_data:
            permiso = usuario.get('permisos', 'Usuario')
            permisos[permiso] = permisos.get(permiso, 0) + 1
        
        return {
            'total': total,
            'activos': activos,
            'inactivos': inactivos,
            'suspendidos': suspendidos,
            'por_permisos': permisos,
            'db_conectada': self.db_disponible
        }
