"""
Aplicación de administración de usuarios.
Arquitectura MVC refactorizada.
"""
from .views import UsuariosView
from .controllers import UsuarioController
from .services import UsuarioService
from .models import UsuarioModel

__all__ = ['UserAdminApp']

class UserAdminApp:
    """
    Aplicación principal de administración de usuarios.
    Coordina todos los componentes MVC.
    """
    
    def __init__(self, parent):
        """Inicializa la aplicación."""
        # Crear controller
        self.controller = UsuarioController(view=None)
        
        # Crear vista pasándole el controller
        self.view = UsuariosView(parent, self.controller)
        
        # Actualizar referencia en el controller
        self.controller.view = self.view
        
        # Layout
        self.pack = self.view.pack
        self.grid = self.view.grid
        self.place = self.view.place
    
    def inicializar(self):
        """Inicializa la aplicación cargando datos."""
        self.view.inicializar()
    
    def destroy(self):
        """Limpia recursos al cerrar."""
        if hasattr(self.view, 'destroy'):
            self.view.destroy()
