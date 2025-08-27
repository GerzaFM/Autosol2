"""
Utilidades de autenticación para usar en toda la aplicación.
"""
from .session_manager import SessionManager
import sys

class AuthUtils:
    """
    Utilidades de autenticación para la aplicación.
    """
    
    @staticmethod
    def get_current_user():
        """Obtiene el usuario actual de la sesión."""
        session_manager = SessionManager()
        return session_manager.get_current_user()
    
    @staticmethod
    def logout():
        """Cierra la sesión del usuario actual."""
        session_manager = SessionManager()
        session_manager.clear_session()
    
    @staticmethod
    def is_logged_in():
        """Verifica si hay un usuario logueado."""
        session_manager = SessionManager()
        return session_manager.is_session_valid()
    
    @staticmethod
    def logout_and_exit():
        """Cierra la sesión y termina la aplicación."""
        AuthUtils.logout()
        print("👋 Sesión cerrada exitosamente")
        sys.exit(0)
