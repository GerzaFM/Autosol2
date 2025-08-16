"""
Modelos para la gestión de usuarios.
"""
from typing import List, Optional, Dict
from datetime import datetime

try:
    from src.bd.models import Usuario, db
    from peewee import DoesNotExist, IntegrityError
except ImportError:
    Usuario = None
    db = None

class UsuarioModel:
    """
    Modelo para manejo de datos de usuarios.
    Encapsula el acceso a la base de datos.
    """
    
    @staticmethod
    def get_all_usuarios() -> List[Dict]:
        """Obtiene todos los usuarios de la base de datos."""
        if Usuario is None:
            # Datos demo si no hay BD
            return [
                {
                    "id": 1,
                    "username": "admin",
                    "email": "admin@tcm.com",
                    "rol": "Administrador",
                    "activo": True,
                    "fecha_creacion": datetime.now().strftime("%Y-%m-%d %H:%M")
                },
                {
                    "id": 2,
                    "username": "usuario",
                    "email": "usuario@tcm.com",
                    "rol": "Usuario",
                    "activo": True,
                    "fecha_creacion": datetime.now().strftime("%Y-%m-%d %H:%M")
                }
            ]
        
        usuarios_data = []
        try:
            usuarios = Usuario.select()
            for usuario in usuarios:
                usuarios_data.append({
                    "id": usuario.codigo,  # El primary key es 'codigo', no 'id'
                    "username": usuario.username,
                    "email": usuario.email,
                    "rol": getattr(usuario, 'rol', 'Usuario'),  # Usar getattr con default
                    "activo": getattr(usuario, 'activo', True),  # Usar getattr con default
                    "fecha_creacion": getattr(usuario, 'fecha_creacion', '').strftime("%Y-%m-%d %H:%M") if hasattr(usuario, 'fecha_creacion') and usuario.fecha_creacion else ""
                })
        except Exception as e:
            print(f"Error al cargar usuarios: {e}")
        
        return usuarios_data
    
    @staticmethod
    def create_usuario(data: Dict) -> bool:
        """Crea un nuevo usuario."""
        if Usuario is None:
            print("Modo demo: Usuario creado (simulado)")
            return True
            
        try:
            # Crear usuario con los campos que existen en el modelo
            usuario_data = {
                'username': data["username"],
                'password': data["password"],  # Ya viene hasheada
                'email': data.get("email", ""),
                'nombre': data.get("username", ""),  # Usar username como nombre si no se proporciona
                'empresa': 1,  # Valores por defecto
                'centro': 1,
                'sucursal': 1,
                'marca': 1
            }
            
            # Agregar campos adicionales si existen en el modelo
            if hasattr(Usuario, 'rol'):
                usuario_data['rol'] = data["rol"]
            if hasattr(Usuario, 'activo'):
                usuario_data['activo'] = data.get("activo", True)
            if hasattr(Usuario, 'fecha_creacion'):
                usuario_data['fecha_creacion'] = datetime.now()
            
            Usuario.create(**usuario_data)
            return True
        except IntegrityError:
            return False
        except Exception as e:
            print(f"Error al crear usuario: {e}")
            return False
    
    @staticmethod
    def update_usuario(user_id: int, data: Dict) -> bool:
        """Actualiza un usuario existente."""
        if Usuario is None:
            print(f"Modo demo: Usuario {user_id} actualizado (simulado)")
            return True
            
        try:
            usuario = Usuario.get(Usuario.codigo == user_id)  # Usar codigo en lugar de get_by_id
            usuario.username = data["username"]
            usuario.email = data["email"]
            usuario.nombre = data.get("username", usuario.nombre)
            
            # Solo actualizar campos si existen en el modelo
            if hasattr(Usuario, 'rol') and 'rol' in data:
                usuario.rol = data["rol"]
            if hasattr(Usuario, 'activo') and 'activo' in data:
                usuario.activo = data.get("activo", True)
            
            # Solo actualizar password si se proporcionó
            if data.get("password"):
                usuario.password = data["password"]
            
            usuario.save()
            return True
        except DoesNotExist:
            return False
        except Exception as e:
            print(f"Error al actualizar usuario: {e}")
            return False
    
    @staticmethod
    def delete_usuario(user_id: int) -> bool:
        """Elimina un usuario."""
        if Usuario is None:
            print(f"Modo demo: Usuario {user_id} eliminado (simulado)")
            return True
            
        try:
            usuario = Usuario.get(Usuario.codigo == user_id)  # Usar codigo en lugar de get_by_id
            usuario.delete_instance()
            return True
        except DoesNotExist:
            return False
        except Exception as e:
            print(f"Error al eliminar usuario: {e}")
            return False
    
    @staticmethod
    def username_exists(username: str, exclude_id: Optional[int] = None) -> bool:
        """Verifica si un username ya existe."""
        if Usuario is None:
            return False
            
        try:
            query = Usuario.select().where(Usuario.username == username)
            if exclude_id:
                query = query.where(Usuario.codigo != exclude_id)  # Usar codigo en lugar de id
            return query.exists()
        except Exception:
            return False
    
    @staticmethod
    def email_exists(email: str, exclude_id: Optional[int] = None) -> bool:
        """Verifica si un email ya existe."""
        if Usuario is None:
            return False
            
        try:
            query = Usuario.select().where(Usuario.email == email)
            if exclude_id:
                query = query.where(Usuario.codigo != exclude_id)  # Usar codigo en lugar de id
            return query.exists()
        except Exception:
            return False
