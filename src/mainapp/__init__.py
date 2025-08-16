"""
Aplicación principal - MainApp.
Contiene la ventana principal y navegación.
"""
from .main_window import MainWindow
from .sidebar import SidebarComponent

__all__ = ['MainApp']

class MainApp:
    """
    Aplicación principal del sistema.
    Maneja la ventana principal y la navegación.
    """
    
    def __init__(self, title: str, size: str, theme: str):
        """Inicializa la aplicación principal."""
        self.main_window = MainWindow(title, size, theme)
        
    def run(self):
        """Ejecuta la aplicación."""
        self.main_window.mainloop()
