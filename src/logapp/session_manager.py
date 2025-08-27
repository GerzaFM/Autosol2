"""
Manejo de sesiones de usuario.
"""
import json
import os
from typing import Optional, Dict
from datetime import datetime, timedelta

class SessionManager:
    """
    Maneja las sesiones de usuario del sistema.
    """
    
    def __init__(self, session_file: str = "user_session.json"):
        """
        Inicializa el manejador de sesiones.
        
        Args:
            session_file: Archivo donde se guardará la sesión
        """
        self.session_file = session_file
        self.session_duration = timedelta(hours=8)  # Sesión válida por 8 horas
    
    def save_session(self, user_data: Dict):
        """
        Guarda la sesión del usuario.
        
        Args:
            user_data: Datos del usuario autenticado
        """
        try:
            session_data = {
                'user': user_data,
                'login_time': datetime.now().isoformat(),
                'expires_at': (datetime.now() + self.session_duration).isoformat()
            }
            
            with open(self.session_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"Error al guardar sesión: {e}")
    
    def load_session(self) -> Optional[Dict]:
        """
        Carga la sesión guardada si es válida.
        
        Returns:
            Datos del usuario si la sesión es válida, None si no
        """
        try:
            if not os.path.exists(self.session_file):
                return None
            
            with open(self.session_file, 'r', encoding='utf-8') as f:
                session_data = json.load(f)
            
            # Verificar si la sesión no ha expirado
            expires_at = datetime.fromisoformat(session_data['expires_at'])
            if datetime.now() > expires_at:
                # Sesión expirada, eliminar archivo
                self.clear_session()
                return None
            
            return session_data['user']
            
        except Exception as e:
            print(f"Error al cargar sesión: {e}")
            # Si hay error, limpiar sesión corrupta
            self.clear_session()
            return None
    
    def clear_session(self):
        """Elimina la sesión guardada."""
        try:
            if os.path.exists(self.session_file):
                os.remove(self.session_file)
        except Exception as e:
            print(f"Error al limpiar sesión: {e}")
    
    def is_session_valid(self) -> bool:
        """
        Verifica si existe una sesión válida.
        
        Returns:
            True si la sesión es válida, False si no
        """
        return self.load_session() is not None
    
    def get_current_user(self) -> Optional[Dict]:
        """
        Obtiene el usuario de la sesión actual.
        
        Returns:
            Datos del usuario actual o None si no hay sesión válida
        """
        return self.load_session()
