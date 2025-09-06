"""
Ventana principal de la aplicación refactorizada.
MainApp - Aplicación independiente en src/
"""
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from typing import Optional
import logging
import sys
import os

from config.settings import config
from .sidebar import SidebarComponent
from logapp import AuthUtils

from app.utils.logger import get_logger

# Importar aplicaciones - corrección de paths
solicitud_app_error = None
try:
    from solicitudapp.solicitud_app_professional import SolicitudApp
except ImportError as e1:
    try:
        from src.solicitudapp.solicitud_app_professional import SolicitudApp
    except ImportError as e2:
        SolicitudApp = None
        solicitud_app_error = f"Error importando SolicitudApp:\n1. solicitudapp.solicitud_app_professional: {str(e1)}\n2. src.solicitudapp.solicitud_app_professional: {str(e2)}"

try:
    from buscarapp.buscar_app_refactored import BuscarAppRefactored
except ImportError:
    try:
        from src.buscarapp.buscar_app_refactored import BuscarAppRefactored
    except ImportError:
        BuscarAppRefactored = None

try:
    from chequeapp.cheque_app_professional import ChequeAppProfessional
except ImportError:
    try:
        from src.chequeapp.cheque_app_professional import ChequeAppProfessional
    except ImportError:
        ChequeAppProfessional = None

try:
    from useradminapp import UserAdminApp
except ImportError:
    UserAdminApp = None

try:
    from proveedoresapp.__init__ import ProveedoresApp
except ImportError:
    ProveedoresApp = None


class MainWindow(tb.Window):
    """
    Ventana principal de la aplicación con arquitectura modular.
    """
    
    def __init__(self, title: str, size: str, theme: str):
        """
        Inicializa la ventana principal.
        
        Args:
            title: Título de la ventana
            size: Tamaño inicial (ej: "1200x900")
            theme: Tema de ttkbootstrap
        """
        super().__init__(themename=theme)
        
        self.logger = get_logger(__name__)
        
        # Configurar ventana
        self.title(title)
        self.geometry(size)
        self.resizable(True, True)
        
        # Establecer tamaño mínimo
        min_width, min_height = config.ui.min_window_size
        self.minsize(min_width, min_height)
        
        # Centrar la ventana
        self._center_window()
        
        # Referencias a componentes
        self.sidebar: Optional[SidebarComponent] = None
        self.content_frame: Optional[tb.Frame] = None
        self.current_view: Optional[tb.Widget] = None
        
        self._create_layout()
        self._setup_menu_items()
        
        # Iniciar directamente con la vista de Nueva Solicitud
        self._show_view("nueva")
        
        self.logger.info("Ventana principal inicializada")
    
    def _center_window(self):
        """Centra la ventana en la pantalla."""
        try:
            # Actualizar la ventana para obtener las dimensiones correctas
            self.update_idletasks()
            
            # Obtener dimensiones de la ventana
            window_width = self.winfo_width()
            window_height = self.winfo_height()
            
            # Si las dimensiones son muy pequeñas, usar las del geometry()
            if window_width < 100 or window_height < 100:
                geometry = self.geometry()
                if 'x' in geometry:
                    size_part = geometry.split('+')[0]  # Obtener solo "1200x900"
                    window_width, window_height = map(int, size_part.split('x'))
            
            # Obtener dimensiones de la pantalla
            screen_width = self.winfo_screenwidth()
            screen_height = self.winfo_screenheight()
            
            # Calcular posición para centrar
            x = (screen_width - window_width) // 2
            y = (screen_height - window_height) // 2
            
            # Asegurar que la ventana no se salga de la pantalla
            x = max(0, x)
            y = max(0, y)
            
            # Aplicar la nueva geometría
            self.geometry(f"{window_width}x{window_height}+{x}+{y}")
            
            self.logger.info(f"Ventana centrada en posición {x}, {y}")
            
        except Exception as e:
            self.logger.error(f"Error al centrar ventana: {e}")
    
    def _create_layout(self):
        """Crea el layout principal de la ventana."""
        # Contenedor principal 
        self.main_container = tb.Frame(self)
        self.main_container.pack(fill=BOTH, expand=True)
        
        # Barra lateral (ahora como navbar horizontal en la parte superior)
        self.sidebar = SidebarComponent(
            self.main_container,
            width_expanded=config.ui.sidebar_width_expanded,
            width_collapsed=config.ui.sidebar_width_collapsed
        )
        self.sidebar.pack(side=TOP, fill=X)
        
        # Área de contenido (ahora debajo de la navbar)
        self.content_frame = tb.Frame(self.main_container, bootstyle="dark")
        self.content_frame.pack(side=TOP, fill=BOTH, expand=True)
        
        # No crear contenido inicial, se mostrará la vista después de setup_menu_items
    
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
        # Diccionario para mapear nombres de vista a botones
        self.view_buttons = {}
        
        # Elementos principales (parte superior)
        self.view_buttons["nueva"] = self.sidebar.add_menu_item(
            "Nueva", "📄", 
            lambda: self._show_view("nueva"), 
            "top"
        )
        self.view_buttons["buscar"] = self.sidebar.add_menu_item(
            "Buscar", "🔍", 
            lambda: self._show_view("buscar"), 
            "top"
        )
        self.view_buttons["cheques"] = self.sidebar.add_menu_item(
            "Cheques", "🏦", 
            lambda: self._show_view("cheques"), 
            "top"
        )
        
        """
        # Elementos de configuración (parte inferior)
        self.view_buttons["config"] = self.sidebar.add_menu_item(
            "Configuración", "⚙️", 
            lambda: self._show_view("config"), 
            "bottom"
        )
        self.view_buttons["database"] = self.sidebar.add_menu_item(
            "Base de Datos", "💾", 
            lambda: self._show_view("database"), 
            "bottom"
        )
        self.view_buttons["cuenta"] = self.sidebar.add_menu_item(
            "Cuenta", "👤", 
            lambda: self._show_view("cuenta"), 
            "bottom"
        )
        """
        
        # Verificar si el usuario es administrador para mostrar botones administrativos
        is_admin = AuthUtils.is_admin()
        
        # Botones solo para administradores
        if is_admin:
            self.view_buttons["proveedores"] = self.sidebar.add_menu_item(
               "Proveedores", "🏢",
                lambda: self._show_view("proveedores"),
                "bottom"
            )
            
            self.view_buttons["nueva_vista"] = self.sidebar.add_menu_item(
                "Usuarios", "👥", 
                lambda: self._show_view("nueva_vista"), 
                "bottom"
            )
        
            # Botón de logout
            self.view_buttons["logout"] = self.sidebar.add_menu_item(
                "Cerrar Sesión", "🚪", 
                lambda: self._handle_logout(), 
                "bottom"
            )

    def _handle_logout(self):
        """Maneja el cierre de sesión del usuario."""
        from tkinter import messagebox
        
        # Confirmar logout
        result = messagebox.askyesno(
            "Cerrar Sesión",
            "¿Estás seguro de que quieres cerrar la sesión?\n\nLa aplicación se cerrará.",
            icon='question'
        )
        
        if result:
            self.logger.info("Usuario solicitó cerrar sesión")
            try:
                # Cerrar sesión y salir
                AuthUtils.logout_and_exit()
            except Exception as e:
                self.logger.error(f"Error al cerrar sesión: {e}")
                # Fallback: cerrar aplicación directamente
                self.quit()
                sys.exit(0)

    def _show_view(self, view_name: str):
        """
        Muestra una vista específica en el área de contenido.
        
        Args:
            view_name: Nombre de la vista a mostrar
        """
        try:
            # Establecer el botón activo (fuente en negrita)
            if view_name in self.view_buttons:
                self.sidebar.set_active_item(self.view_buttons[view_name])
            
            # Limpiar contenido actual
            self._clear_content()
            
            # Mostrar la vista correspondiente
            if view_name == "nueva":
                self._show_solicitud_view()
            elif view_name == "buscar":
                self._show_facturas_view()
            elif view_name == "cheques":
                self._show_cheques_view()
            elif view_name == "nueva_vista":
                self._administrador_usuarios()
            elif view_name == "proveedores":
                self._show_proveedores_view()
            else:
                self._show_placeholder_view(view_name)
            
            self.logger.info(f"Vista mostrada: {view_name}")
            
        except Exception as e:
            self.logger.error(f"Error al mostrar vista '{view_name}': {e}")
            self._show_error_view(str(e))
    
    def _show_solicitud_view(self):
        """Muestra la aplicación de nueva solicitud directamente."""
        try:
            # Limpiar contenido anterior
            self._clear_content()
            
            if SolicitudApp is None:
                error_msg = solicitud_app_error if solicitud_app_error else "SolicitudApp no está disponible"
                self._show_error_view(error_msg)
                return
            
            # Instanciar directamente la aplicación legacy
            self.current_view = SolicitudApp(master=self.content_frame)
            self.current_view.pack(fill=BOTH, expand=True)
            
            self.logger.info("Aplicación de solicitud cargada directamente")
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            self.logger.error(f"Error al crear aplicación de solicitud: {e}")
            self.logger.error(f"Traceback completo: {error_details}")
            self._show_error_view(f"Error al crear SolicitudApp:\n{error_details}")
            self._show_error_view(f"Error al cargar solicitud: {str(e)}")
    
    def _show_facturas_view(self):
        """Muestra la aplicación de facturas directamente."""
        try:
            # Limpiar contenido anterior
            self._clear_content()
            
            if BuscarAppRefactored is None:
                self._show_error_view("BuscarAppRefactored no está disponible")
                return
            
            # Instanciar directamente la aplicación legacy
            self.current_view = BuscarAppRefactored(master=self.content_frame)
            self.current_view.pack(fill=BOTH, expand=True)
            
            self.logger.info("Aplicación de facturas cargada directamente")
            
        except Exception as e:
            self.logger.error(f"Error al crear aplicación de facturas: {e}")
            self._show_error_view(f"Error al cargar facturas: {str(e)}")
    
    def _show_cheques_view(self):
        """Muestra la aplicación de cheques directamente."""
        try:
            # Limpiar contenido anterior
            self._clear_content()
            
            if ChequeAppProfessional is None:
                self._show_error_view("ChequeAppProfessional no está disponible")
                return
            
            # Instanciar directamente la aplicación legacy
            self.current_view = ChequeAppProfessional(self.content_frame)
            # Nota: ChequeAppProfessional maneja su propio pack() internamente
            
            self.logger.info("Aplicación de cheques cargada directamente")
            
        except Exception as e:
            self.logger.error(f"Error al crear vista de cheques: {e}")
            self._show_error_view(f"Error al cargar cheques: {str(e)}")
    
    def _administrador_usuarios(self):
        """Muestra la aplicación de administración de usuarios (MVC)."""
        # Verificar permisos de administrador
        if not AuthUtils.is_admin():
            self._show_error_view("Acceso denegado: Solo los administradores pueden acceder a esta sección")
            return
            
        try:
            # Limpiar contenido anterior
            self._clear_content()
            
            if UserAdminApp is None:
                self._show_error_view("UserAdminApp no está disponible")
                return
            
            # Instanciar directamente la aplicación MVC
            self.current_view = UserAdminApp(self.content_frame)
            self.current_view.pack(fill=BOTH, expand=True)
            
            # Inicializar con datos
            self.current_view.inicializar()
            
            self.logger.info("Aplicación de usuarios (MVC) cargada directamente")
            
        except Exception as e:
            self.logger.error(f"Error al crear aplicación de usuarios: {e}")
            self._show_error_view(f"Error al cargar aplicación de usuarios: {str(e)}")
    
    def _show_proveedores_view(self):
        """Muestra la aplicación de proveedores directamente."""
        # Verificar permisos de administrador
        if not AuthUtils.is_admin():
            self._show_error_view("Acceso denegado: Solo los administradores pueden acceder a esta sección")
            return
            
        try:
            # Limpiar contenido anterior
            self._clear_content()

            if ProveedoresApp is None:
                self._show_error_view("ProveedoresApp no está disponible")
                return

            # Instanciar directamente la aplicación de proveedores
            self.current_view = ProveedoresApp(self.content_frame)
            
            # Asegurar que se empaquete correctamente
            if hasattr(self.current_view, 'pack'):
                self.current_view.pack(fill=BOTH, expand=True)
            
            self.logger.info("Aplicación de proveedores cargada directamente")

        except Exception as e:
            self.logger.error(f"Error al crear aplicación de proveedores: {e}")
            self._show_error_view(f"Error al cargar proveedores: {str(e)}")

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
        
        # Crear un área con scroll para errores largos
        text_frame = tb.Frame(error_frame)
        text_frame.pack(fill=BOTH, expand=True, padx=20, pady=20)
        
        # Usar Text widget con scrollbar para errores largos
        import tkinter as tk
        from tkinter import scrolledtext
        
        text_widget = scrolledtext.ScrolledText(
            text_frame,
            font=("Consolas", 10),
            wrap=tk.WORD,
            height=15,
            bg="#2b2b2b",
            fg="#ffffff",
            insertbackground="#ffffff"
        )
        text_widget.pack(fill=BOTH, expand=True)
        text_widget.insert("1.0", error_message)
        text_widget.config(state=tk.DISABLED)  # Solo lectura
        
        self.current_view = error_frame
    
    def _show_welcome(self):
        """Muestra la vista de bienvenida."""
        self._clear_content()
        self.sidebar.clear_active()
        self._create_initial_content()
    
    def _clear_content(self):
        """Limpia el contenido actual del área principal."""
        if self.current_view:
            try:
                # Forzar la limpieza de todos los widgets hijos primero
                for child in self.content_frame.winfo_children():
                    child.destroy()
                
                # Luego destruir la vista actual
                if hasattr(self.current_view, 'destroy'):
                    self.current_view.destroy()
                
                self.current_view = None
                
                # Forzar actualización del contenedor
                self.content_frame.update_idletasks()
                
            except Exception as e:
                self.logger.error(f"Error limpiando contenido: {e}")
                # En caso de error, intenta limpiar manualmente
                try:
                    for child in self.content_frame.winfo_children():
                        child.destroy()
                    self.current_view = None
                except Exception as e2:
                    self.logger.error(f"Error en limpieza de emergencia: {e2}")
                    self.current_view = None
