"""
Ventana de login del sistema.
"""
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import messagebox
import tkinter as tk
from tkinter import ttk
import os
from .auth_service import AuthService

class LoginWindow:
    """
    Ventana de autenticación del sistema.
    """
    
    def __init__(self, parent=None):
        """Inicializa la ventana de login."""
        if parent is None:
            # Para uso standalone, usar ttkbootstrap Window
            self.root = tb.Window(
                title="TCM Matehuala - Iniciar Sesión",
                themename="cosmo",  # Tema claro y legible
                size=(450, 430),
                resizable=(False, False)
            )
            self.is_standalone = True
        else:
            # Crear como ventana modal
            self.root = tb.Toplevel(parent)
            self.root.title("TCM Matehuala - Iniciar Sesión")
            self.root.geometry("450x430")
            self.root.resizable(False, False)
            self.root.transient(parent)
            self.root.grab_set()
            self.is_standalone = False
        
        # Variables
        self.authenticated_user = None
        self.login_successful = False
        
        # Centrar ventana
        self._center_window()
        
        # Crear interfaz
        self._create_interface()
        
        # Focus en username
        self.username_entry.focus_set()

    def _center_window(self):
        """Centra la ventana en la pantalla."""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def _create_interface(self):
        """Crear la interfaz de usuario."""
        main_frame = tb.Frame(self.root)
        main_frame.pack(fill=BOTH, expand=True)

        # Título
        title_frame = tb.Frame(main_frame)
        title_frame.pack(pady=20)
        
        title_label = tb.Label(
            title_frame,
            text="🔐 Iniciar Sesión",
            font=("Segoe UI", 18, "bold"),
            bootstyle="primary"
        )
        title_label.pack()
        
        subtitle_label = tb.Label(
            title_frame,
            text="TCM Matehuala - Sistema de Gestión",
            font=("Segoe UI", 10),
            bootstyle="secondary"
        )
        subtitle_label.pack(pady=(5, 0))

        # Formulario
        form_frame = tb.Frame(main_frame)
        form_frame.pack(pady=20, padx=40, fill=X)

        # Usuario
        tb.Label(
            form_frame,
            text="👤 Usuario:",
            font=("Segoe UI", 11, "bold")
        ).pack(anchor=W, pady=(0, 5))
        
        self.username_entry = tb.Entry(
            form_frame,
            font=("Segoe UI", 11),
            width=30,
            bootstyle="primary"
        )
        self.username_entry.pack(fill=X, pady=(0, 15))

        # Contraseña
        tb.Label(
            form_frame,
            text="🔒 Contraseña:",
            font=("Segoe UI", 11, "bold")
        ).pack(anchor=W, pady=(0, 5))
        
        self.password_entry = tb.Entry(
            form_frame,
            font=("Segoe UI", 11),
            width=30,
            show="*",
            bootstyle="primary"
        )
        self.password_entry.pack(fill=X, pady=(0, 20))

        # Botones
        button_frame = tb.Frame(form_frame)
        button_frame.pack(fill=X, pady=(10, 0))

        login_button = tb.Button(
            button_frame,
            text="🚀 Iniciar Sesión",
            command=self._handle_login,
            bootstyle="success",
            width=20
        )
        login_button.pack(side=LEFT, padx=(0, 10))

        exit_button = tb.Button(
            button_frame,
            text="❌ Salir",
            command=self._handle_exit,
            bootstyle="secondary-outline",
            width=15
        )
        exit_button.pack(side=RIGHT)

        # Enter key binding
        self.password_entry.bind('<Return>', lambda e: self._handle_login())

        # Label de estado
        self.status_label = tb.Label(
            main_frame,
            text="",
            bootstyle="info"
        )
        self.status_label.pack(pady=(15, 0))

    def _handle_login(self):
        """Maneja el intento de login."""
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        
        # Validar formato
        valid, error_msg = AuthService.validate_credentials(username, password)
        if not valid:
            self._show_error(error_msg)
            return
        
        # Mostrar estado de cargando
        self._show_status("🔄 Verificando credenciales...", "info")
        self.root.update()
        
        # Autenticar
        success, user_data, message = AuthService.authenticate(username, password)
        
        if success:
            self.authenticated_user = user_data
            self.login_successful = True
            self._show_status("✅ Login exitoso", "success")
            self.root.after(1000, self._close_window)
        else:
            self._show_error(message)
            # Limpiar contraseña
            self.password_entry.delete(0, 'end')
            self.password_entry.focus_set()
    
    def _handle_exit(self):
        """Maneja la salida del sistema."""
        self.login_successful = False
        self.authenticated_user = None
        self._close_window()
    
    def _show_error(self, message: str):
        """Muestra un mensaje de error."""
        self._show_status(f"❌ {message}", "danger")
    
    def _show_status(self, message: str, style: str = "info"):
        """Muestra un mensaje de estado."""
        self.status_label.config(text=message, bootstyle=style)
    
    def _close_window(self):
        """Cierra la ventana."""
        # Para modal, solo destruir la ventana
        self.root.destroy()
    
    def show_login(self) -> tuple:
        """
        Muestra la ventana de login y espera resultado.
        
        Returns:
            Tupla (login_exitoso, datos_usuario)
        """
        try:
            if self.is_standalone:
                # Para standalone (no debería usarse más)
                self.root.mainloop()
            else:
                # Para modal, usar wait_window
                self.root.wait_window()
        except:
            pass
        
        return self.login_successful, self.authenticated_user
