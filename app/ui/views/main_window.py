"""
Ventana principal de la aplicación refactorizada.
"""
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from typing import Optional
import logging

from config.settings import config
from app.ui.components.sidebar import SidebarComponent
from app.ui.views.solicitud_view import SolicitudView
from app.ui.views.user_admin import AdministradorUsuarios
from app.ui.views.facturas_view import FacturasView
from app.ui.views.cheques_view import ChequesView
from app.utils.logger import get_logger

class MainWindow(tb.Window):
    """
    Ventana principal de la aplicación con arquitectura modular.
    """
    
    def __init__(self, title: str, size: str, theme: str, db_manager):
        """
        Inicializa la ventana principal.
        
        Args:
            title: Título de la ventana
            size: Tamaño inicial (ej: "1200x900")
            theme: Tema de ttkbootstrap
            db_manager: Gestor de base de datos
        """
        super().__init__(themename=theme)
        
        self.logger = get_logger(__name__)
        self.db_manager = db_manager
        
        # Configurar ventana
        self.title(title)
        self.geometry(size)
        self.resizable(True, True)
        
        # Establecer tamaño mínimo
        min_width, min_height = config.ui.min_window_size
        self.minsize(min_width, min_height)
        
        # Referencias a componentes
        self.sidebar: Optional[SidebarComponent] = None
        self.content_frame: Optional[tb.Frame] = None
        self.current_view: Optional[tb.Widget] = None
        
        self._create_layout()
        self._setup_menu_items()
        
        self.logger.info("Ventana principal inicializada")
    
    def _create_layout(self):
        """Crea el layout principal de la ventana."""
        # Barra superior
        self.header_frame = tb.Frame(self, bootstyle="secondary", height=50)
        self.header_frame.pack(side=TOP, fill=X)
        self.header_frame.pack_propagate(False)
        
        # Contenedor principal
        self.main_container = tb.Frame(self)
        self.main_container.pack(side=TOP, fill=BOTH, expand=True)
        
        # Barra lateral
        self.sidebar = SidebarComponent(
            self.main_container,
            width_expanded=config.ui.sidebar_width_expanded,
            width_collapsed=config.ui.sidebar_width_collapsed
        )
        self.sidebar.pack(side=LEFT, fill=Y)
        
        # Área de contenido
        self.content_frame = tb.Frame(self.main_container, bootstyle="dark")
        self.content_frame.pack(side=RIGHT, fill=BOTH, expand=True)
        
        self._create_header_content()
        self._create_initial_content()
    
    def _create_header_content(self):
        """Crea el contenido de la barra superior."""
        # Título de la aplicación
        title_label = tb.Label(
            self.header_frame,
            text=config.app_name,
            font=("Segoe UI", 15, "bold"),
            bootstyle="inverse-secondary"
        )
        title_label.pack(side=LEFT, padx=10, pady=10)
        
        # Información del usuario/departamento
        info_label = tb.Label(
            self.header_frame,
            text="Administración",
            font=("Segoe UI", 10),
            bootstyle="inverse-secondary"
        )
        info_label.pack(side=RIGHT, padx=10, pady=10)
        
        # Versión (opcional)
        version_label = tb.Label(
            self.header_frame,
            text=f"v{config.version}",
            font=("Segoe UI", 8),
            bootstyle="inverse-secondary"
        )
        version_label.pack(side=RIGHT, padx=(0, 10), pady=10)
    
    def _create_initial_content(self):
        """Crea el contenido inicial del área principal."""
        welcome_frame = tb.Frame(self.content_frame)
        welcome_frame.pack(fill=BOTH, expand=True)
        
        # Mensaje de bienvenida
        welcome_label = tb.Label(
            welcome_frame,
            text=f"Bienvenido a {config.app_name}",
            font=("Segoe UI", 24, "bold"),
            bootstyle="inverse-dark"
        )
        welcome_label.pack(pady=100)
        
        subtitle_label = tb.Label(
            welcome_frame,
            text="Seleccione una opción del menú lateral para comenzar",
            font=("Segoe UI", 14),
            bootstyle="inverse-dark"
        )
        subtitle_label.pack(pady=20)
        
        self.current_view = welcome_frame
    
    def _setup_menu_items(self):
        """Configura los elementos del menú lateral."""
        # Elementos principales (parte superior)
        self.sidebar.add_menu_item(
            "Nueva Solicitud", "📄", 
            lambda: self._show_view("nueva"), 
            "top"
        )
        self.sidebar.add_menu_item(
            "Buscar", "🔍", 
            lambda: self._show_view("buscar"), 
            "top"
        )
        self.sidebar.add_menu_item(
            "Cheques", "🏦", 
            lambda: self._show_view("cheques"), 
            "top"
        )
        self.sidebar.add_menu_item(
            "Reportes", "📊", 
            lambda: self._show_view("reportes"), 
            "top"
        )
        self.sidebar.add_menu_item(
            "Pagos", "💵", 
            lambda: self._show_view("pagos"), 
            "top"
        )
        self.sidebar.add_menu_item(
            "Usuarios", "👥", 
            lambda: self._show_view("nueva_vista"), 
            "top"
        )
        
        # Elementos de configuración (parte inferior)
        self.sidebar.add_menu_item(
            "Configuración", "⚙️", 
            lambda: self._show_view("config"), 
            "bottom"
        )
        self.sidebar.add_menu_item(
            "Base de Datos", "💾", 
            lambda: self._show_view("database"), 
            "bottom"
        )
        self.sidebar.add_menu_item(
            "Cuenta", "👤", 
            lambda: self._show_view("cuenta"), 
            "bottom"
        )
    
    def _show_view(self, view_name: str):
        """
        Muestra una vista específica en el área de contenido.
        
        Args:
            view_name: Nombre de la vista a mostrar
        """
        try:
            # Colapsar sidebar al seleccionar una opción
            self.sidebar.collapse()
            
            # Limpiar contenido actual
            self._clear_content()
            
            # Marcar elemento activo en el sidebar
            view_names = {
                "nueva": "Nueva Solicitud",
                "buscar": "Buscar",
                "cheques": "Cheques",
                "reportes": "Reportes",
                "pagos": "Pagos",
                "nueva_vista": "Usuarios",
                "config": "Configuración",
                "database": "Base de Datos",
                "cuenta": "Cuenta"
            }
            
            if view_name in view_names:
                self.sidebar.set_active_item(view_names[view_name])
            
            # Mostrar la vista correspondiente
            if view_name == "nueva":
                self._show_solicitud_view()
            elif view_name == "buscar":
                self._show_facturas_view()
            elif view_name == "cheques":
                self._show_cheques_view()
            elif view_name == "nueva_vista":
                self._administrador_usuarios()
            else:
                self._show_placeholder_view(view_name)
            
            self.logger.info(f"Vista mostrada: {view_name}")
            
        except Exception as e:
            self.logger.error(f"Error al mostrar vista '{view_name}': {e}")
            self._show_error_view(str(e))
    
    def _show_solicitud_view(self):
        """Muestra la vista de nueva solicitud."""
        try:
            # Limpiar contenido anterior
            self._clear_content()
            
            solicitud_view = SolicitudView(self.content_frame, self.db_manager)
            solicitud_view.pack(fill=BOTH, expand=True)
            self.current_view = solicitud_view
            
        except Exception as e:
            self.logger.error(f"Error al crear vista de solicitud: {e}")
            self._show_error_view(f"Error al cargar solicitud: {str(e)}")
    
    def _show_facturas_view(self):
        """Muestra la vista de facturas guardadas."""
        try:
            # Limpiar contenido anterior
            self._clear_content()
            
            facturas_view = FacturasView(self.content_frame, self.db_manager)
            facturas_view.pack(fill=BOTH, expand=True)
            self.current_view = facturas_view
            
            self.logger.info("Vista de facturas mostrada exitosamente")
            
        except Exception as e:
            self.logger.error(f"Error al crear vista de facturas: {e}")
            self._show_error_view(f"Error al cargar facturas: {str(e)}")
    
    def _show_cheques_view(self):
        """Muestra la vista de gestión de cheques."""
        try:
            # Limpiar contenido anterior
            self._clear_content()
            
            cheques_view = ChequesView(self.content_frame, self.db_manager)
            cheques_view.pack(fill=BOTH, expand=True)
            self.current_view = cheques_view
            
            self.logger.info("Vista de cheques mostrada exitosamente")
            
        except Exception as e:
            self.logger.error(f"Error al crear vista de cheques: {e}")
            self._show_error_view(f"Error al cargar cheques: {str(e)}")
    
    def _administrador_usuarios(self):
        """Muestra el administrador de usuarios."""
        try:
            # Limpiar contenido anterior
            self._clear_content()
            
            # Crear el administrador de usuarios
            admin_usuarios = AdministradorUsuarios(self.content_frame, self.db_manager)
            admin_usuarios.pack(fill=BOTH, expand=True)
            
            # Inicializar con datos
            admin_usuarios.inicializar()
            
            self.current_view = admin_usuarios
            self.logger.info("Administrador de usuarios mostrado exitosamente")
            
        except Exception as e:
            self.logger.error(f"Error al crear administrador de usuarios: {e}")
            self._show_error_view(f"Error al cargar administrador de usuarios: {str(e)}")
    
    def _accion_personalizada(self, accion: str):
        """
        Método de ejemplo para manejar acciones de tu nueva vista.
        
        Args:
            accion: Nombre de la acción ejecutada
        """
        self.logger.info(f"Acción ejecutada: {accion}")
        # Aquí puedes agregar la lógica específica para cada acción
    
    def _show_placeholder_view(self, view_name: str):
        """
        Muestra una vista placeholder para funcionalidades no implementadas.
        
        Args:
            view_name: Nombre de la vista
        """
        placeholder_frame = tb.Frame(self.content_frame)
        placeholder_frame.pack(fill=BOTH, expand=True)
        
        # Título
        title_label = tb.Label(
            placeholder_frame,
            text=f"Vista: {view_name.title()}",
            font=("Segoe UI", 20, "bold"),
            bootstyle="inverse-dark"
        )
        title_label.pack(pady=50)
        
        # Mensaje
        message_label = tb.Label(
            placeholder_frame,
            text="Esta funcionalidad estará disponible en una próxima versión",
            font=("Segoe UI", 12),
            bootstyle="inverse-dark"
        )
        message_label.pack(pady=20)
        
        # Botón para volver
        back_button = tb.Button(
            placeholder_frame,
            text="Volver al Inicio",
            bootstyle="primary",
            command=self._show_welcome
        )
        back_button.pack(pady=20)
        
        self.current_view = placeholder_frame
    
    def _show_error_view(self, error_message: str):
        """
        Muestra una vista de error.
        
        Args:
            error_message: Mensaje de error a mostrar
        """
        error_frame = tb.Frame(self.content_frame)
        error_frame.pack(fill=BOTH, expand=True)
        
        error_label = tb.Label(
            error_frame,
            text="Error",
            font=("Segoe UI", 20, "bold"),
            bootstyle="danger"
        )
        error_label.pack(pady=50)
        
        message_label = tb.Label(
            error_frame,
            text=error_message,
            font=("Segoe UI", 12),
            bootstyle="inverse-dark"
        )
        message_label.pack(pady=20)
        
        self.current_view = error_frame
    
    def _show_welcome(self):
        """Muestra la vista de bienvenida."""
        self._clear_content()
        self.sidebar.clear_active()
        self._create_initial_content()
    
    def _clear_content(self):
        """Limpia el contenido actual del área principal."""
        if self.current_view:
            self.current_view.destroy()
            self.current_view = None
