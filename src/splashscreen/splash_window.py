"""
Ventana de splash como ventana hija de la principal.
"""
import ttkbootstrap as tb
from ttkbootstrap.constants import *
import tkinter as tk
import time


class SplashWindow:
    """Ventana de splash que es hija de la ventana principal."""
    
    def __init__(self, parent_window):
        """
        Inicializa la ventana de splash como hija de la ventana principal.
        
        Args:
            parent_window: La ventana principal (tb.Window)
        """
        self.parent = parent_window
        self.splash = None
        self.progress_value = 0
        
    def create_splash(self):
        """Crea la ventana de splash como ventana hija."""
        # Crear Toplevel como hija de la ventana principal
        self.splash = tb.Toplevel(self.parent)
        self.splash.title("Autoforms")
        self.splash.overrideredirect(True)  # Sin bordes
        
        # Configurar tamaño más grande y centrado
        width = 480
        height = 350
        screen_width = self.splash.winfo_screenwidth()
        screen_height = self.splash.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.splash.geometry(f"{width}x{height}+{x}+{y}")
        
        # Configurar fondo y transparencia
        self.splash.configure(bg='#2c3e50')  # Fondo oscuro elegante
        
        # Mantener al frente
        self.splash.attributes('-topmost', True)
        
        # Agregar un poco de transparencia (opcional)
        try:
            self.splash.attributes('-alpha', 0.95)  # Ligeramente transparente
        except:
            pass  # Si no es compatible, continuar sin transparencia
        
        # Crear contenido
        self._create_content()
        
        # Hacer que la ventana principal no sea visible aún
        self.parent.withdraw()
        
        # Asegurar que el splash sea visible
        self.splash.update()
        
    def _create_content(self):
        """Crea el contenido del splash con diseño profesional."""
        # Frame principal con fondo oscuro
        main_frame = tb.Frame(self.splash)
        main_frame.pack(fill=BOTH, expand=True)
        
        # Frame superior para el logo/imagen (si tienes una)
        header_frame = tb.Frame(main_frame, padding=20)
        header_frame.pack(fill=X, pady=(30, 20))
        
        # Título principal con estilo más moderno
        title_label = tb.Label(
            header_frame,
            text="AUTOFORMS",
            font=("Segoe UI", 28, "bold"),
            anchor=CENTER
        )
        title_label.pack()
        
        # Subtítulo más elegante
        subtitle_label = tb.Label(
            header_frame,
            text="Sistema de Gestión de Solicitudes",
            font=("Segoe UI", 14),
            anchor=CENTER
        )
        subtitle_label.pack(pady=(5, 0))
        
        # Frame central para la barra de progreso
        progress_frame = tb.Frame(main_frame, padding=30)
        progress_frame.pack(fill=X, expand=True)
        
        # Barra de progreso más moderna
        self.progress = tb.Progressbar(
            progress_frame,
            mode='determinate',
            length=320,
            maximum=100,
            style="success.Striped.Horizontal.TProgressbar"
        )
        self.progress.pack(pady=20)
        
        # Texto de estado más elegante
        self.status_label = tb.Label(
            progress_frame,
            text="Iniciando aplicación...",
            font=("Segoe UI", 11),
            anchor=CENTER
        )
        self.status_label.pack(pady=(10, 0))
        
        # Frame inferior para información adicional
        footer_frame = tb.Frame(main_frame, bootstyle="dark", padding=20)
        footer_frame.pack(fill=X, side=BOTTOM)
        
        # Información de empresa/sistema
        company_label = tb.Label(
            footer_frame,
            text="TCM Matehuala - Todos los derechos reservados",
            font=("Segoe UI", 9),
            anchor=CENTER
        )
        company_label.pack()
        
        # Versión en la esquina
        version_label = tb.Label(
            footer_frame,
            text="v0.1.0",
            font=("Segoe UI", 8),
            anchor=CENTER
        )
        version_label.pack(pady=(5, 0))
    
    def update_progress(self, value, message=None):
        """Actualiza la barra de progreso y el mensaje con animación suave."""
        if self.splash and self.splash.winfo_exists():
            # Animación suave de la barra de progreso
            current_value = self.progress.cget('value')
            target_value = value
            
            # Si la diferencia es pequeña, actualizar directamente
            if abs(target_value - current_value) <= 5:
                self.progress.config(value=target_value)
            else:
                # Animación gradual
                step = 2 if target_value > current_value else -2
                while abs(self.progress.cget('value') - target_value) > 1:
                    current = self.progress.cget('value')
                    new_value = min(target_value, current + step) if step > 0 else max(target_value, current + step)
                    self.progress.config(value=new_value)
                    self.splash.update()
                    time.sleep(0.01)  # Pausa pequeña para la animación
                
                # Asegurar valor final
                self.progress.config(value=target_value)
            
            # Actualizar mensaje si se proporciona
            if message:
                self.status_label.config(text=message)
            
            # Forzar actualización
            self.splash.update()
            self.progress_value = value
    
    def close_and_show_main(self):
        """Cierra el splash y muestra la ventana principal."""
        if self.splash and self.splash.winfo_exists():
            # Cerrar splash
            self.splash.destroy()
            self.splash = None
            
            # Mostrar ventana principal
            self.parent.deiconify()
            self.parent.lift()
            self.parent.focus_force()
