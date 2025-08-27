"""
Servicio de autenticación.
Maneja la validación de usuarios contra la base de datos.
"""
import hashlib
from typing import Optional, Tuple
from src.bd.models import Usuario
from peewee import DoesNotExist

class AuthService:
    """
    Servicio para autenticación de usuarios.
    """
    
    @staticmethod
    def authenticate(username: str, password: str) -> Tuple[bool, Optional[dict], str]:
        """
        Autentica un usuario.
        
        Args:
            username: Nombre de usuario
            password: Contraseña en texto plano
            
        Returns:
            Tupla con (éxito, datos_usuario, mensaje)
        """
        try:
            # Buscar usuario por username
            usuario = Usuario.get(Usuario.username == username)
            
            # Verificar contraseña
            password_hash = AuthService._hash_password(password)
            if usuario.password == password_hash:
                # Login exitoso
                user_data = {
                    'id': usuario.codigo,
                    'username': usuario.username,
                    'nombre': usuario.nombre,
                    'email': usuario.email,
                    'empresa': usuario.empresa,
                    'centro': usuario.centro,
                    'permisos': usuario.permisos or 'Usuario'
                }
                return True, user_data, "Login exitoso"
            else:
                return False, None, "Contraseña incorrecta"
                
        except DoesNotExist:
            return False, None, "Usuario no encontrado"
        except Exception as e:
            return False, None, f"Error de autenticación: {str(e)}"
    
    @staticmethod
    def _hash_password(password: str) -> str:
        """Genera hash SHA256 de la contraseña."""
        return hashlib.sha256(password.encode()).hexdigest()
    
    @staticmethod
    def validate_credentials(username: str, password: str) -> Tuple[bool, str]:
        """
        Valida que las credenciales tengan formato correcto.
        
        Returns:
            Tupla con (válido, mensaje_error)
        """
        if not username or not username.strip():
            return False, "El nombre de usuario es requerido"
        
        if not password or not password.strip():
            return False, "La contraseña es requerida"
        
        if len(username.strip()) < 3:
            return False, "El nombre de usuario debe tener al menos 3 caracteres"
        
        if len(password) < 6:
            return False, "La contraseña debe tener al menos 6 caracteres"
        
        return True, ""
