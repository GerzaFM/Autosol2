"""
Servicios para la gestión de usuarios.
Contiene la lógica de negocio.
"""
import hashlib
import re
from typing import Dict, List, Tuple
from .models import UsuarioModel

class UsuarioService:
    """
    Servicio para gestión de usuarios.
    Contiene toda la lógica de negocio.
    """
    
    # Roles disponibles
    ROLES_DISPONIBLES = [
        "Administrador",
        "Supervisor", 
        "Usuario",
        "Contador",
        "Consultor"
    ]
    
    @staticmethod
    def get_all_usuarios() -> List[Dict]:
        """Obtiene todos los usuarios."""
        return UsuarioModel.get_all_usuarios()
    
    @staticmethod
    def validate_usuario_data(data: Dict, is_edit: bool = False, user_id: int = None) -> Tuple[bool, List[str]]:
        """Valida los datos de un usuario."""
        errors = []
        
        # Validar username
        username = data.get("username", "").strip()
        if not username:
            errors.append("El nombre de usuario es requerido")
        elif len(username) < 3:
            errors.append("El nombre de usuario debe tener al menos 3 caracteres")
        elif not re.match(r'^[a-zA-Z0-9_]+$', username):
            errors.append("El nombre de usuario solo puede contener letras, números y guiones bajos")
        elif UsuarioModel.username_exists(username, user_id if is_edit else None):
            errors.append("El nombre de usuario ya existe")
        
        # Validar email
        email = data.get("email", "").strip()
        if not email:
            errors.append("El email es requerido")
        elif not UsuarioService._is_valid_email(email):
            errors.append("El formato del email no es válido")
        elif UsuarioModel.email_exists(email, user_id if is_edit else None):
            errors.append("El email ya está en uso")
        
        # Validar password (solo requerido para nuevos usuarios)
        password = data.get("password", "")
        if not is_edit and not password:
            errors.append("La contraseña es requerida")
        elif password and len(password) < 6:
            errors.append("La contraseña debe tener al menos 6 caracteres")
        
        # Validar rol
        rol = data.get("rol", "")
        if not rol:
            errors.append("El rol es requerido")
        elif rol not in UsuarioService.ROLES_DISPONIBLES:
            errors.append("Rol no válido")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def create_usuario(data: Dict) -> Tuple[bool, str]:
        """Crea un nuevo usuario."""
        # Validar datos
        is_valid, errors = UsuarioService.validate_usuario_data(data, is_edit=False)
        if not is_valid:
            return False, "\n".join(errors)
        
        # Preparar datos
        user_data = data.copy()
        if user_data.get("password"):
            user_data["password"] = UsuarioService._hash_password(user_data["password"])
        
        # Crear usuario
        success = UsuarioModel.create_usuario(user_data)
        if success:
            return True, "Usuario creado exitosamente"
        else:
            return False, "Error al crear usuario"
    
    @staticmethod
    def update_usuario(user_id: int, data: Dict) -> Tuple[bool, str]:
        """Actualiza un usuario existente."""
        # Validar datos
        is_valid, errors = UsuarioService.validate_usuario_data(data, is_edit=True, user_id=user_id)
        if not is_valid:
            return False, "\n".join(errors)
        
        # Preparar datos
        user_data = data.copy()
        if user_data.get("password"):
            user_data["password"] = UsuarioService._hash_password(user_data["password"])
        
        # Actualizar usuario
        success = UsuarioModel.update_usuario(user_id, user_data)
        if success:
            return True, "Usuario actualizado exitosamente"
        else:
            return False, "Error al actualizar usuario"
    
    @staticmethod
    def delete_usuario(user_id: int) -> Tuple[bool, str]:
        """Elimina un usuario."""
        success = UsuarioModel.delete_usuario(user_id)
        if success:
            return True, "Usuario eliminado exitosamente"
        else:
            return False, "Error al eliminar usuario"
    
    @staticmethod
    def _hash_password(password: str) -> str:
        """Genera hash SHA256 de la contraseña."""
        return hashlib.sha256(password.encode()).hexdigest()
    
    @staticmethod
    def _is_valid_email(email: str) -> bool:
        """Valida formato de email."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def get_roles() -> List[str]:
        """Obtiene lista de roles disponibles."""
        return UsuarioService.ROLES_DISPONIBLES.copy()
