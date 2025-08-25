"""
Modelo para la gestión de proveedores.
Maneja todas las operaciones CRUD y consultas relacionadas con proveedores.
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

try:
    # Importar modelos de la base de datos
    from src.bd.models import Proveedor, db
    from peewee import DoesNotExist, IntegrityError, fn
    DATABASE_AVAILABLE = True
except ImportError:
    # Fallback si no hay acceso a la base de datos
    Proveedor = None
    db = None
    DATABASE_AVAILABLE = False


class ProveedorModel:
    """
    Modelo para manejar operaciones de proveedores en la base de datos.
    Incluye operaciones CRUD, búsquedas y validaciones.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.db_available = DATABASE_AVAILABLE
        
        if self.db_available:
            try:
                # Verificar conexión a la base de datos
                if db and db.is_closed():
                    db.connect(reuse_if_open=True)
                self.logger.info("Conexión a base de datos de proveedores establecida")
            except Exception as e:
                self.logger.error(f"Error conectando a BD: {e}")
                self.db_available = False
        else:
            self.logger.warning("Base de datos no disponible, usando datos de ejemplo")

    # ==================== OPERACIONES CRUD ====================
    
    def crear_proveedor(self, datos: Dict[str, Any]) -> Tuple[bool, str, Optional[int]]:
        """
        Crear un nuevo proveedor
        
        Args:
            datos: Diccionario con datos del proveedor
            
        Returns:
            Tupla (éxito, mensaje, id_del_proveedor)
        """
        if not self.db_available:
            return False, "Base de datos no disponible", None
            
        try:
            # Validar datos requeridos
            is_valid, errors = self._validate_proveedor_data(datos)
            if not is_valid:
                return False, f"Datos inválidos: {', '.join(errors)}", None
            
            # Verificar si ya existe un proveedor con el mismo RFC (si se proporciona)
            rfc = datos.get('rfc', '').strip()
            if rfc:
                existing = Proveedor.get_or_none(Proveedor.rfc == rfc)
                if existing:
                    return False, f"Ya existe un proveedor con RFC: {rfc}", None
            
            # Crear nuevo proveedor
            proveedor = Proveedor.create(
                codigo_quiter=datos.get('codigo_quiter'),
                nombre=datos.get('nombre', '').strip() or None,
                nombre_en_quiter=datos.get('nombre_en_quiter', '').strip() or None,
                rfc=rfc or None,
                telefono=datos.get('telefono', '').strip() or None,
                email=datos.get('email', '').strip() or None,
                nombre_contacto=datos.get('nombre_contacto', '').strip() or None,
                cuenta_mayor=datos.get('cuenta_mayor') or None
            )
            
            self.logger.info(f"Proveedor creado exitosamente: ID {proveedor.id}")
            return True, "Proveedor creado exitosamente", proveedor.id
            
        except IntegrityError as e:
            error_msg = f"Error de integridad: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg, None
        except Exception as e:
            error_msg = f"Error creando proveedor: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg, None

    def actualizar_proveedor(self, proveedor_id: int, datos: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Actualizar un proveedor existente
        
        Args:
            proveedor_id: ID del proveedor a actualizar
            datos: Diccionario con nuevos datos
            
        Returns:
            Tupla (éxito, mensaje)
        """
        if not self.db_available:
            return False, "Base de datos no disponible"
            
        try:
            # Verificar que el proveedor existe
            proveedor = Proveedor.get_by_id(proveedor_id)
            
            # Validar datos
            is_valid, errors = self._validate_proveedor_data(datos, update=True)
            if not is_valid:
                return False, f"Datos inválidos: {', '.join(errors)}"
            
            # Verificar RFC duplicado (si se está cambiando)
            nuevo_rfc = datos.get('rfc', '').strip()
            if nuevo_rfc and nuevo_rfc != proveedor.rfc:
                existing = Proveedor.get_or_none(
                    (Proveedor.rfc == nuevo_rfc) & (Proveedor.id != proveedor_id)
                )
                if existing:
                    return False, f"Ya existe otro proveedor con RFC: {nuevo_rfc}"
            
            # Actualizar campos
            campos_actualizados = []
            for campo, valor in datos.items():
                if hasattr(proveedor, campo):
                    valor_limpio = valor.strip() if isinstance(valor, str) else valor
                    valor_final = valor_limpio or None
                    
                    if getattr(proveedor, campo) != valor_final:
                        setattr(proveedor, campo, valor_final)
                        campos_actualizados.append(campo)
            
            if campos_actualizados:
                proveedor.save()
                self.logger.info(f"Proveedor {proveedor_id} actualizado: {', '.join(campos_actualizados)}")
                return True, f"Proveedor actualizado exitosamente"
            else:
                return True, "No se realizaron cambios"
                
        except DoesNotExist:
            return False, f"Proveedor con ID {proveedor_id} no encontrado"
        except Exception as e:
            error_msg = f"Error actualizando proveedor: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg

    def eliminar_proveedor(self, proveedor_id: int) -> Tuple[bool, str]:
        """
        Eliminar un proveedor
        
        Args:
            proveedor_id: ID del proveedor a eliminar
            
        Returns:
            Tupla (éxito, mensaje)
        """
        if not self.db_available:
            return False, "Base de datos no disponible"
            
        try:
            proveedor = Proveedor.get_by_id(proveedor_id)
            
            # Verificar si tiene facturas asociadas
            if hasattr(proveedor, 'facturas') and proveedor.facturas.count() > 0:
                return False, "No se puede eliminar: el proveedor tiene facturas asociadas"
            
            nombre = proveedor.nombre or proveedor.nombre_en_quiter or f"ID {proveedor_id}"
            proveedor.delete_instance()
            
            self.logger.info(f"Proveedor eliminado: {nombre}")
            return True, f"Proveedor '{nombre}' eliminado exitosamente"
            
        except DoesNotExist:
            return False, f"Proveedor con ID {proveedor_id} no encontrado"
        except Exception as e:
            error_msg = f"Error eliminando proveedor: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg

    # ==================== CONSULTAS Y BÚSQUEDAS ====================
    
    def obtener_todos(self, limite: int = None) -> List[Dict[str, Any]]:
        """
        Obtener todos los proveedores
        
        Args:
            limite: Límite de resultados (opcional)
            
        Returns:
            Lista de diccionarios con datos de proveedores
        """
        if not self.db_available:
            return self._get_sample_data()
            
        try:
            query = Proveedor.select()
            if limite:
                query = query.limit(limite)
            
            proveedores = []
            for proveedor in query:
                proveedores.append(self._proveedor_to_dict(proveedor))
            
            return proveedores
            
        except Exception as e:
            self.logger.error(f"Error obteniendo proveedores: {e}")
            return self._get_sample_data()

    def buscar_proveedores(self, filtros: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Buscar proveedores con filtros
        
        Args:
            filtros: Diccionario con filtros de búsqueda
                   - texto: búsqueda en nombre, RFC o contacto
                   - incompletos: solo proveedores con datos incompletos
                   - codigo_quiter: filtro por código quiter
                   
        Returns:
            Lista de diccionarios con datos de proveedores
        """
        if not self.db_available:
            return self._get_sample_data()
            
        try:
            query = Proveedor.select()
            
            # Filtro de texto (nombre, RFC, contacto)
            texto = filtros.get('texto', '').strip()
            if texto:
                query = query.where(
                    (Proveedor.nombre.contains(texto)) |
                    (Proveedor.nombre_en_quiter.contains(texto)) |
                    (Proveedor.rfc.contains(texto)) |
                    (Proveedor.nombre_contacto.contains(texto))
                )
            
            # Filtro de incompletos
            if filtros.get('incompletos', False):
                query = query.where(
                    (Proveedor.nombre.is_null()) |
                    (Proveedor.rfc.is_null()) |
                    (Proveedor.telefono.is_null()) |
                    (Proveedor.email.is_null())
                )
            
            # Filtro por código quiter
            codigo_quiter = filtros.get('codigo_quiter')
            if codigo_quiter:
                query = query.where(Proveedor.codigo_quiter == codigo_quiter)
            
            # Ordenar por nombre
            query = query.order_by(
                fn.COALESCE(Proveedor.nombre, Proveedor.nombre_en_quiter)
            )
            
            proveedores = []
            for proveedor in query:
                proveedores.append(self._proveedor_to_dict(proveedor))
            
            return proveedores
            
        except Exception as e:
            self.logger.error(f"Error buscando proveedores: {e}")
            return self._get_sample_data()

    def obtener_por_id(self, proveedor_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtener un proveedor por su ID
        
        Args:
            proveedor_id: ID del proveedor
            
        Returns:
            Diccionario con datos del proveedor o None si no existe
        """
        if not self.db_available:
            sample_data = self._get_sample_data()
            return sample_data[0] if sample_data else None
            
        try:
            proveedor = Proveedor.get_by_id(proveedor_id)
            return self._proveedor_to_dict(proveedor)
        except DoesNotExist:
            return None
        except Exception as e:
            self.logger.error(f"Error obteniendo proveedor {proveedor_id}: {e}")
            return None

    def obtener_por_rfc(self, rfc: str) -> Optional[Dict[str, Any]]:
        """
        Obtener un proveedor por su RFC
        
        Args:
            rfc: RFC del proveedor
            
        Returns:
            Diccionario con datos del proveedor o None si no existe
        """
        if not self.db_available:
            return None
            
        try:
            proveedor = Proveedor.get_or_none(Proveedor.rfc == rfc.strip())
            return self._proveedor_to_dict(proveedor) if proveedor else None
        except Exception as e:
            self.logger.error(f"Error obteniendo proveedor por RFC {rfc}: {e}")
            return None

    # ==================== MÉTODOS DE UTILIDAD ====================
    
    def _validate_proveedor_data(self, datos: Dict[str, Any], update: bool = False) -> Tuple[bool, List[str]]:
        """
        Validar datos de proveedor
        
        Args:
            datos: Diccionario con datos a validar
            update: Si es True, permite validación más flexible para actualizaciones
            
        Returns:
            Tupla (es_válido, lista_de_errores)
        """
        errores = []
        
        # Para creación, requerir al menos nombre o nombre_en_quiter
        if not update:
            nombre = datos.get('nombre', '').strip()
            nombre_quiter = datos.get('nombre_en_quiter', '').strip()
            if not nombre and not nombre_quiter:
                errores.append("Debe proporcionar al menos un nombre")
        
        # Validar RFC si se proporciona
        rfc = datos.get('rfc', '').strip()
        if rfc and len(rfc) < 12:
            errores.append("RFC debe tener al menos 12 caracteres")
        
        # Validar email si se proporciona
        email = datos.get('email', '').strip()
        if email and '@' not in email:
            errores.append("Email inválido")
        
        # Validar código quiter si se proporciona
        codigo_quiter = datos.get('codigo_quiter')
        if codigo_quiter is not None:
            try:
                int(codigo_quiter)
            except (ValueError, TypeError):
                errores.append("Código quiter debe ser un número")
        
        return len(errores) == 0, errores
    
    def _proveedor_to_dict(self, proveedor) -> Dict[str, Any]:
        """
        Convertir objeto Proveedor a diccionario
        
        Args:
            proveedor: Instancia del modelo Proveedor
            
        Returns:
            Diccionario con datos del proveedor
        """
        return {
            'id': proveedor.id,
            'codigo_quiter': proveedor.codigo_quiter,
            'nombre': proveedor.nombre or '',
            'nombre_en_quiter': proveedor.nombre_en_quiter or '',
            'rfc': proveedor.rfc or '',
            'telefono': proveedor.telefono or '',
            'email': proveedor.email or '',
            'nombre_contacto': proveedor.nombre_contacto or '',
            'cuenta_mayor': proveedor.cuenta_mayor,
            # Campo calculado para mostrar el nombre preferido
            'nombre_display': proveedor.nombre or proveedor.nombre_en_quiter or 'Sin nombre',
            # Campos de estado
            'incompleto': self._is_incompleto(proveedor)
        }
    
    def _is_incompleto(self, proveedor) -> bool:
        """
        Verificar si un proveedor tiene datos incompletos
        
        Args:
            proveedor: Instancia del modelo Proveedor
            
        Returns:
            True si tiene datos incompletos
        """
        return (
            not proveedor.nombre or
            not proveedor.rfc or
            not proveedor.telefono or
            not proveedor.email
        )
    
    def _get_sample_data(self) -> List[Dict[str, Any]]:
        """
        Obtener datos de ejemplo cuando la BD no está disponible
        
        Returns:
            Lista con datos de ejemplo
        """
        return [
            {
                'id': 1,
                'codigo_quiter': 1001,
                'nombre': 'Proveedor Ejemplo SA',
                'nombre_en_quiter': 'PROV EJEMPLO',
                'rfc': 'PEJ123456789',
                'telefono': '444-123-4567',
                'email': 'contacto@proveedorejemplo.com',
                'nombre_contacto': 'Juan Pérez',
                'cuenta_mayor': 2100,
                'nombre_display': 'Proveedor Ejemplo SA',
                'incompleto': False
            },
            {
                'id': 2,
                'codigo_quiter': 1002,
                'nombre': '',
                'nombre_en_quiter': 'SERV MANTEN',
                'rfc': '',
                'telefono': '',
                'email': '',
                'nombre_contacto': '',
                'cuenta_mayor': None,
                'nombre_display': 'SERV MANTEN',
                'incompleto': True
            },
            {
                'id': 3,
                'codigo_quiter': 1003,
                'nombre': 'Servicios Integrales XYZ',
                'nombre_en_quiter': 'SERV INTEG XYZ',
                'rfc': 'SIX890123456',
                'telefono': '444-987-6543',
                'email': 'admin@serviciosxyz.com',
                'nombre_contacto': 'María González',
                'cuenta_mayor': 2150,
                'nombre_display': 'Servicios Integrales XYZ',
                'incompleto': False
            }
        ]

    # ==================== MÉTODOS ADICIONALES ====================
    
    def contar_proveedores(self, filtros: Dict[str, Any] = None) -> int:
        """
        Contar proveedores con filtros opcionales
        
        Args:
            filtros: Diccionario con filtros (opcional)
            
        Returns:
            Número de proveedores
        """
        if not self.db_available:
            return len(self._get_sample_data())
            
        try:
            query = Proveedor.select()
            
            if filtros:
                # Aplicar los mismos filtros que en buscar_proveedores
                texto = filtros.get('texto', '').strip()
                if texto:
                    query = query.where(
                        (Proveedor.nombre.contains(texto)) |
                        (Proveedor.nombre_en_quiter.contains(texto)) |
                        (Proveedor.rfc.contains(texto)) |
                        (Proveedor.nombre_contacto.contains(texto))
                    )
                
                if filtros.get('incompletos', False):
                    query = query.where(
                        (Proveedor.nombre.is_null()) |
                        (Proveedor.rfc.is_null()) |
                        (Proveedor.telefono.is_null()) |
                        (Proveedor.email.is_null())
                    )
            
            return query.count()
            
        except Exception as e:
            self.logger.error(f"Error contando proveedores: {e}")
            return 0

    def obtener_estadisticas(self) -> Dict[str, Any]:
        """
        Obtener estadísticas de proveedores
        
        Returns:
            Diccionario con estadísticas
        """
        if not self.db_available:
            return {
                'total': 3,
                'incompletos': 1,
                'completos': 2,
                'con_rfc': 2,
                'sin_rfc': 1
            }
        
        try:
            total = Proveedor.select().count()
            incompletos = Proveedor.select().where(
                (Proveedor.nombre.is_null()) |
                (Proveedor.rfc.is_null()) |
                (Proveedor.telefono.is_null()) |
                (Proveedor.email.is_null())
            ).count()
            con_rfc = Proveedor.select().where(Proveedor.rfc.is_null(False)).count()
            
            return {
                'total': total,
                'incompletos': incompletos,
                'completos': total - incompletos,
                'con_rfc': con_rfc,
                'sin_rfc': total - con_rfc
            }
            
        except Exception as e:
            self.logger.error(f"Error obteniendo estadísticas: {e}")
            return {'error': str(e)}
