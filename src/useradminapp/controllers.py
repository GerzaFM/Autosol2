"""
Controladores para la gestión de usuarios.
Coordinan entre las vistas y los servicios.
"""
from typing import Dict, List, Optional, Callable
from .services import UsuarioService
from app.utils.logger import get_logger

class UsuarioController:
    """
    Controlador para gestión de usuarios.
    Coordina entre la vista y los servicios.
    """
    
    def __init__(self, view):
        """Inicializa el controlador."""
        self.view = view
        self.logger = get_logger(__name__)
        self.service = UsuarioService()
        
        # Callbacks de la vista
        self.on_usuarios_loaded: Optional[Callable] = None
        self.on_success_message: Optional[Callable] = None
        self.on_error_message: Optional[Callable] = None
    
    def set_callbacks(self, 
                     on_usuarios_loaded: Callable = None,
                     on_success_message: Callable = None, 
                     on_error_message: Callable = None):
        """Configura callbacks para comunicación con la vista."""
        self.on_usuarios_loaded = on_usuarios_loaded
        self.on_success_message = on_success_message
        self.on_error_message = on_error_message
    
    def load_usuarios(self):
        """Carga la lista de usuarios."""
        try:
            usuarios = self.service.get_all_usuarios()
            self.logger.info(f"Cargados {len(usuarios)} usuarios")
            
            if self.on_usuarios_loaded:
                self.on_usuarios_loaded(usuarios)
                
        except Exception as e:
            self.logger.error(f"Error al cargar usuarios: {e}")
            if self.on_error_message:
                self.on_error_message(f"Error al cargar usuarios: {str(e)}")
    
    def create_usuario(self, form_data: Dict):
        """Crea un nuevo usuario."""
        try:
            success, message = self.service.create_usuario(form_data)
            
            if success:
                self.logger.info(f"Usuario creado: {form_data.get('username')}")
                if self.on_success_message:
                    self.on_success_message(message)
                # Recargar lista
                self.load_usuarios()
            else:
                self.logger.warning(f"Error al crear usuario: {message}")
                if self.on_error_message:
                    self.on_error_message(message)
                    
        except Exception as e:
            self.logger.error(f"Excepción al crear usuario: {e}")
            if self.on_error_message:
                self.on_error_message(f"Error inesperado: {str(e)}")
    
    def update_usuario(self, user_id: int, form_data: Dict):
        """Actualiza un usuario existente."""
        try:
            success, message = self.service.update_usuario(user_id, form_data)
            
            if success:
                self.logger.info(f"Usuario actualizado: {form_data.get('username')}")
                if self.on_success_message:
                    self.on_success_message(message)
                # Recargar lista
                self.load_usuarios()
            else:
                self.logger.warning(f"Error al actualizar usuario: {message}")
                if self.on_error_message:
                    self.on_error_message(message)
                    
        except Exception as e:
            self.logger.error(f"Excepción al actualizar usuario: {e}")
            if self.on_error_message:
                self.on_error_message(f"Error inesperado: {str(e)}")
    
    def delete_usuario(self, user_id: int, username: str = ""):
        """Elimina un usuario."""
        try:
            success, message = self.service.delete_usuario(user_id)
            
            if success:
                self.logger.info(f"Usuario eliminado: {username} (ID: {user_id})")
                if self.on_success_message:
                    self.on_success_message(message)
                # Recargar lista
                self.load_usuarios()
            else:
                self.logger.warning(f"Error al eliminar usuario: {message}")
                if self.on_error_message:
                    self.on_error_message(message)
                    
        except Exception as e:
            self.logger.error(f"Excepción al eliminar usuario: {e}")
            if self.on_error_message:
                self.on_error_message(f"Error inesperado: {str(e)}")
    
    def get_roles(self) -> List[str]:
        """Obtiene lista de roles disponibles."""
        return self.service.get_roles()
    
    def validate_form_data(self, form_data: Dict, is_edit: bool = False, user_id: int = None) -> tuple:
        """Valida datos del formulario."""
        return self.service.validate_usuario_data(form_data, is_edit, user_id)
