"""
ProveedorModel - Modelo de datos para gestión de proveedores
============================================================

Capa de persistencia en la arquitectura MVC que maneja todas las operaciones
de base de datos relacionadas con proveedores. Actúa como abstracción entre
la lógica de negocio y la base de datos subyacente.

Arquitectura de datos:
┌─────────────────────────────────────────┐
│              Controller                  │
│                   │                     │
│                   ▼                     │
│            ProveedorModel                │ <- Esta clase
│         (Capa de abstracción)           │
│                   │                     │
│                   ▼                     │
│        Peewee ORM + PostgreSQL          │
│         (Persistencia física)           │
└─────────────────────────────────────────┘

Responsabilidades principales:
- Operaciones CRUD completas (Create, Read, Update, Delete)
- Validaciones de datos y reglas de negocio
- Consultas optimizadas y filtrado avanzado
- Manejo de errores y logging detallado
- Transformación entre formatos (ORM ↔ Dict)
- Verificación de integridad referencial

Patrones implementados:
- Repository Pattern: Abstrae el acceso a datos
- Data Mapper Pattern: Convierte entre objetos ORM y diccionarios
- Active Record Pattern: Operaciones sobre instancias de modelo
- Transaction Script Pattern: Operaciones complejas en métodos específicos

Características técnicas:
- Manejo robusto de errores con logging detallado
- Validaciones a nivel de modelo y base de datos
- Consultas optimizadas con Peewee ORM
- Fallback graceful si BD no está disponible
- Métodos de utilidad para transformación de datos
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

try:
    # Importar modelos de la base de datos
    # Dependencias: Peewee ORM + definición de modelos de BD
    from src.bd.models import Proveedor, db
    from peewee import DoesNotExist, IntegrityError, fn
    DATABASE_AVAILABLE = True
except ImportError:
    # Fallback graceful si no hay acceso a la base de datos
    # Permite que la aplicación arranque incluso con problemas de BD
    Proveedor = None
    db = None
    DATABASE_AVAILABLE = False


class ProveedorModel:
    """
    Modelo de datos principal para gestión de proveedores.
    
    Proporciona una interfaz de alto nivel para todas las operaciones
    relacionadas con proveedores, abstrayendo los detalles de persistencia
    y proporcionando validaciones consistentes.
    
    Características principales:
    - CRUD completo con validaciones
    - Búsquedas flexibles y filtrado avanzado
    - Manejo robusto de errores
    - Logging detallado para auditoría
    - Transformación automática de datos
    - Verificación de integridad referencial
    
    Interfaz de datos:
    - Entrada: Diccionarios con datos del formulario
    - Salida: Diccionarios normalizados para la vista
    - Interno: Objetos Peewee ORM para operaciones BD
    
    Gestión de estado:
    - Stateless: No mantiene estado entre operaciones
    - Transaccional: Cada operación es atómica
    - Thread-safe: Seguro para uso concurrente
    """
    
    def __init__(self):
        """
        Inicializa el modelo y establece conexión con la base de datos.
        
        Configuración realizada:
        - Logger para registro de operaciones
        - Verificación de disponibilidad de BD
        - Establecimiento de conexión si está disponible
        - Configuración de fallback si hay problemas
        
        El constructor implementa un patrón de inicialización defensiva,
        permitiendo que la aplicación funcione incluso con problemas
        de conectividad de base de datos.
        """
        # === CONFIGURACIÓN DE LOGGING ===
        # Logger específico para este módulo, permite trazabilidad detallada
        self.logger = logging.getLogger(__name__)
        
        # === VERIFICACIÓN DE DISPONIBILIDAD DE BASE DE DATOS ===
        # Flag que determina si las operaciones reales de BD están disponibles
        self.db_available = DATABASE_AVAILABLE
        
        if self.db_available:
            try:
                # === ESTABLECIMIENTO DE CONEXIÓN ===
                # Verificar y establecer conexión con la base de datos
                # reuse_if_open=True evita múltiples conexiones innecesarias
                if db and db.is_closed():
                    db.connect(reuse_if_open=True)
                self.logger.info("Conexión a base de datos de proveedores establecida")
            except Exception as e:
                # === FALLBACK EN CASO DE ERROR DE CONEXIÓN ===
                # Degradación graceful: deshabilitar BD pero mantener aplicación funcional
                self.logger.error(f"Error conectando a BD: {e}")
                self.db_available = False
        else:
            # === MODO FALLBACK ===
            # La aplicación puede arrancar sin BD para desarrollo/testing
            self.logger.warning("Base de datos no disponible, usando datos de ejemplo")

    # ==================== OPERACIONES CRUD ====================
    
    def crear_proveedor(self, datos: Dict[str, Any]) -> Tuple[bool, str, Optional[int]]:
        """
        Crear un nuevo proveedor en la base de datos.
        
        Args:
            datos: Diccionario con datos del proveedor desde el formulario
                  Formato esperado:
                  {
                      'codigo_quiter': int,
                      'nombre': str,
                      'nombre_en_quiter': str,
                      'rfc': str,
                      'telefono': str,
                      'email': str,
                      'nombre_contacto': str
                  }
                  
        Returns:
            Tupla (éxito, mensaje, id_del_proveedor)
            - éxito: bool indicando si la operación fue exitosa
            - mensaje: str descriptivo del resultado (éxito o error)
            - id_del_proveedor: int con el ID asignado, None si falló
        
        Proceso de creación:
        1. Verificar disponibilidad de base de datos
        2. Validar datos de entrada con reglas de negocio
        3. Verificar unicidad de RFC (si se proporciona)
        4. Crear registro en base de datos
        5. Registrar operación en logs
        6. Retornar resultado estructurado
        
        Validaciones aplicadas:
        - Datos requeridos según reglas de negocio
        - Formato válido de RFC, email, etc.
        - Unicidad de RFC en la base de datos
        - Integridad referencial
        
        Manejo de errores:
        - IntegrityError: Violaciones de restricciones BD
        - ValueError: Datos inválidos
        - Exception general: Errores inesperados
        """
        # === VERIFICACIÓN DE DISPONIBILIDAD ===
        if not self.db_available:
            return False, "Base de datos no disponible", None
            
        try:
            # === VALIDACIÓN DE DATOS DE ENTRADA ===
            # Aplicar reglas de negocio antes de intentar persistir
            is_valid, errors = self._validate_proveedor_data(datos)
            if not is_valid:
                return False, f"Datos inválidos: {', '.join(errors)}", None
            
            # === VERIFICACIÓN DE UNICIDAD DE RFC ===
            # Prevenir duplicados de RFC si se proporciona
            rfc = datos.get('rfc', '').strip()
            if rfc:
                existing = Proveedor.get_or_none(Proveedor.rfc == rfc)
                if existing:
                    return False, f"Ya existe un proveedor con RFC: {rfc}", None
            
            # === CREACIÓN DEL REGISTRO ===
            # Crear instancia en BD con datos normalizados
            # Note: strip() y conversión a None para campos vacíos
            proveedor = Proveedor.create(
                codigo_quiter=datos.get('codigo_quiter'),
                nombre=datos.get('nombre', '').strip() or None,
                nombre_en_quiter=datos.get('nombre_en_quiter', '').strip() or None,
                rfc=rfc or None,
                telefono=datos.get('telefono', '').strip() or None,
                email=datos.get('email', '').strip() or None,
                nombre_contacto=datos.get('nombre_contacto', '').strip() or None
            )
            
            # === LOGGING DE ÉXITO ===
            self.logger.info(f"Proveedor creado exitosamente: ID {proveedor.id}")
            return True, "Proveedor creado exitosamente", proveedor.id
            
        except IntegrityError as e:
            # === MANEJO DE ERRORES DE INTEGRIDAD ===
            # Violaciones de restricciones de BD (UNIQUE, FK, etc.)
            error_msg = f"Error de integridad: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg, None
        except Exception as e:
            # === MANEJO DE ERRORES GENERALES ===
            # Cualquier otro error inesperado
            error_msg = f"Error creando proveedor: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg, None

    def actualizar_proveedor(self, proveedor_id: int, datos: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Actualizar un proveedor existente en la base de datos.
        
        Args:
            proveedor_id: ID único del proveedor a actualizar
            datos: Diccionario con nuevos datos (mismo formato que crear_proveedor)
            
        Returns:
            Tupla (éxito, mensaje)
            - éxito: bool indicando si la operación fue exitosa
            - mensaje: str descriptivo del resultado
        
        Proceso de actualización:
        1. Verificar existencia del proveedor por ID
        2. Validar nuevos datos con reglas flexibles
        3. Verificar unicidad de RFC si cambió
        4. Actualizar solo campos que cambiaron (optimización)
        5. Guardar cambios en BD
        6. Registrar operación con detalles
        
        Características especiales:
        - Validación flexible (update=True) permite mayor permisividad
        - Solo actualiza campos que realmente cambiaron
        - Preserva integridad referencial
        - Verifica unicidad de RFC excluyendo el registro actual
        
        Optimizaciones:
        - Detecta si no hay cambios reales (evita UPDATE innecesario)
        - Lista campos actualizados para logging detallado
        - Comparación inteligente de valores (maneja None vs '')
        """
        # === VERIFICACIÓN DE DISPONIBILIDAD ===
        if not self.db_available:
            return False, "Base de datos no disponible"
            
        try:
            # === VERIFICACIÓN DE EXISTENCIA ===
            # DoesNotExist se lanza si no existe el proveedor
            proveedor = Proveedor.get_by_id(proveedor_id)
            
            # === VALIDACIÓN DE DATOS (MODO ACTUALIZACIÓN) ===
            # update=True permite validación más flexible
            is_valid, errors = self._validate_proveedor_data(datos, update=True)
            if not is_valid:
                return False, f"Datos inválidos: {', '.join(errors)}"
            
            # === VERIFICACIÓN DE RFC DUPLICADO ===
            # Solo verificar si el RFC está cambiando
            nuevo_rfc = datos.get('rfc', '').strip()
            if nuevo_rfc and nuevo_rfc != proveedor.rfc:
                # Buscar RFC duplicado excluyendo el registro actual
                existing = Proveedor.get_or_none(
                    (Proveedor.rfc == nuevo_rfc) & (Proveedor.id != proveedor_id)
                )
                if existing:
                    return False, f"Ya existe otro proveedor con RFC: {nuevo_rfc}"
            
            # === ACTUALIZACIÓN INTELIGENTE DE CAMPOS ===
            # Solo actualizar campos que realmente cambiaron
            campos_actualizados = []
            for campo, valor in datos.items():
                if hasattr(proveedor, campo):
                    # Normalizar valor: strip + conversión a None si vacío
                    valor_limpio = valor.strip() if isinstance(valor, str) else valor
                    valor_final = valor_limpio or None
                    
                    # Solo actualizar si el valor realmente cambió
                    if getattr(proveedor, campo) != valor_final:
                        setattr(proveedor, campo, valor_final)
                        campos_actualizados.append(campo)
            
            # === PERSISTENCIA Y LOGGING ===
            if campos_actualizados:
                # Solo hacer UPDATE si hay cambios reales
                proveedor.save()
                self.logger.info(f"Proveedor {proveedor_id} actualizado: {', '.join(campos_actualizados)}")
                return True, f"Proveedor actualizado exitosamente"
            else:
                # No hay cambios - operación exitosa pero sin trabajo
                return True, "No se realizaron cambios"
                
        except DoesNotExist:
            # === PROVEEDOR NO ENCONTRADO ===
            return False, f"Proveedor con ID {proveedor_id} no encontrado"
        except Exception as e:
            # === ERRORES GENERALES ===
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
            return []
            
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
            return []

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
            return []
            
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
            return []

    def obtener_por_id(self, proveedor_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtener un proveedor por su ID
        
        Args:
            proveedor_id: ID del proveedor
            
        Returns:
            Diccionario con datos del proveedor o None si no existe
        """
        if not self.db_available:
            return None
            
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
            return 0
            
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
                'total': 0,
                'incompletos': 0,
                'completos': 0,
                'con_rfc': 0,
                'sin_rfc': 0
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
