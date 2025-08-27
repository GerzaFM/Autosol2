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
                    "id": usuario.codigo,  # El primary key es 'codigo'
                    "username": usuario.username,
                    "email": usuario.email or "",
                    "rol": usuario.permisos or "Usuario",  # Mapear permisos a rol
                    "activo": True,  # Valor fijo ya que no existe en BD
                    "fecha_creacion": "",  # Valor fijo ya que no existe en BD
                    "nombre": usuario.nombre or "",
                    "empresa": usuario.empresa,
                    "centro": usuario.centro,
                    "sucursal": usuario.sucursal,
                    "marca": usuario.marca
                })
        except Exception as e:
            print(f"Error al cargar usuarios: {e}")
        
        return usuarios_data
    
    @staticmethod
    def create_usuario(data: Dict) -> tuple[bool, str]:
        """Crea un nuevo usuario."""
        if Usuario is None:
            print("Modo demo: Usuario creado (simulado)")
            return True, "Usuario creado (modo demo)"
            
        try:
            # Crear usuario solo con los campos reales del modelo PostgreSQL
            usuario_data = {
                'username': data["username"],
                'password': data["password"],  # Ya viene hasheada
                'email': data.get("email", ""),
                'nombre': data.get("nombre", data["username"]),  # Usar nombre o username
                'empresa': data.get("empresa", 1),  # Valores por defecto
                'centro': data.get("centro", 1),
                'sucursal': data.get("sucursal", 1),
                'marca': data.get("marca", 1),
                'permisos': data.get("rol", "Usuario"),  # Mapear rol a permisos
                'responsable': data.get("responsable")  # Puede ser None
            }
            
            # Agregar código si se especifica
            if 'codigo' in data and data['codigo']:
                usuario_data['codigo'] = data['codigo']
            
            Usuario.create(**usuario_data)
            return True, "Usuario creado exitosamente"
        except IntegrityError as e:
            error_msg = f"Error de integridad: {str(e)}"
            print(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"Error al crear usuario: {str(e)}"
            print(error_msg)
            return False, error_msg
    
    @staticmethod
    def update_usuario(user_id: int, data: Dict) -> tuple[bool, str]:
        """Actualiza un usuario existente."""
        if Usuario is None:
            print(f"Modo demo: Usuario {user_id} actualizado (simulado)")
            return True, "Usuario actualizado (modo demo)"
            
        try:
            usuario = Usuario.get(Usuario.codigo == user_id)
            usuario.username = data["username"]
            usuario.email = data.get("email", "")
            usuario.nombre = data.get("nombre", data["username"])
            
            # Mapear rol a permisos (campo real en PostgreSQL)
            if 'rol' in data:
                usuario.permisos = data["rol"]
            
            # Actualizar otros campos si se proporcionan
            for field in ['empresa', 'centro', 'sucursal', 'marca']:
                if field in data:
                    setattr(usuario, field, data[field])
            
            # Solo actualizar password si se proporcionó
            if data.get("password"):
                usuario.password = data["password"]
            
            usuario.save()
            return True, "Usuario actualizado exitosamente"
        except DoesNotExist:
            error_msg = f"Usuario con ID {user_id} no encontrado"
            print(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"Error al actualizar usuario: {str(e)}"
            print(error_msg)
            return False, error_msg
    
    @staticmethod
    def delete_usuario(user_id: int) -> tuple[bool, str]:
        """Elimina un usuario."""
        if Usuario is None:
            print(f"Modo demo: Usuario {user_id} eliminado (simulado)")
            return True, "Usuario eliminado (modo demo)"
            
        try:
            usuario = Usuario.get(Usuario.codigo == user_id)
            usuario.delete_instance()
            return True, "Usuario eliminado exitosamente"
        except DoesNotExist:
            error_msg = f"Usuario con ID {user_id} no encontrado"
            print(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"Error al eliminar usuario: {str(e)}"
            print(error_msg)
            return False, error_msg
    
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
