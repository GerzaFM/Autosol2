"""
Clase para manejar la base de datos de cheques
"""
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, date

# Importar modelos de la base de datos
try:
    import sys
    import os
    # Agregar el directorio src al path
    bd_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'bd')
    sys.path.insert(0, bd_path)
    
    from src.bd.models import Cheque, Proveedor, Layout
    from peewee import fn
    DATABASE_AVAILABLE = True
    DATABASE_AVAILABLE = True
except ImportError as e:
    Cheque = Proveedor = Layout = fn = None
    DATABASE_AVAILABLE = False


class ChequeDatabase:
    """Clase para manejar operaciones de base de datos de cheques"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.db_available = DATABASE_AVAILABLE
        
        if self.db_available:
            try:
                # Inicializar la conexión a la base de datos directamente
                self.logger.info("Conexión a base de datos de cheques establecida")
            except Exception as e:
                self.logger.error(f"Error conectando a BD: {e}")
                self.db_available = False
        else:
            self.logger.warning("Base de datos no disponible")
    
    def search_cheques(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Busca cheques en la base de datos aplicando filtros
        
        Args:
            filters: Diccionario con filtros de búsqueda
            
        Returns:
            Lista de diccionarios con datos de cheques
        """
        if not self.db_available:
            return []
        
        try:
            # Construir consulta base
            query = Cheque.select()
            
            # Aplicar filtro de fecha inicial
            if filters.get('fecha_inicial'):
                fecha_inicial = self._parse_date(filters['fecha_inicial'])
                if fecha_inicial:
                    query = query.where(Cheque.fecha >= fecha_inicial)
            
            # Aplicar filtro de fecha final
            if filters.get('fecha_final'):
                fecha_final = self._parse_date(filters['fecha_final'])
                if fecha_final:
                    query = query.where(Cheque.fecha <= fecha_final)
            
            # Aplicar filtro de clase (en las facturas relacionadas)
            if filters.get('clase'):
                clase = filters['clase'].strip()
                if clase:
                    # Importar Factura para hacer el join
                    try:
                        from src.bd.models import Factura
                        # Filtrar cheques que tengan facturas con la clase especificada
                        # Usar la relación inversa: cheques que tienen facturas con esa clase
                        query = query.join(Factura, on=(Cheque.id == Factura.cheque)).where(
                            Factura.clase.contains(clase)
                        ).distinct()
                    except Exception as e:
                        self.logger.warning(f"Error al aplicar filtro de clase: {e}")
                        # Fallback: buscar en vale o folio como antes
                        query = query.where(
                            (Cheque.vale.contains(clase)) | 
                            (Cheque.folio.contains(clase))
                        )
            
            # Aplicar filtro de proveedor
            if filters.get('proveedor'):
                proveedor = filters['proveedor'].strip()
                if proveedor:
                    query = query.where(Cheque.proveedor.nombre.contains(proveedor))
            
            # Ejecutar consulta y convertir a lista de diccionarios
            cheques = []
            for cheque in query:
                # Obtener la clase de la primera factura relacionada
                clase_factura = ""
                try:
                    if hasattr(cheque, 'facturas') and cheque.facturas:
                        primera_factura = cheque.facturas.first()
                        if primera_factura and hasattr(primera_factura, 'clase'):
                            clase_factura = primera_factura.clase or ""
                except Exception as e:
                    self.logger.warning(f"Error al obtener clase de factura para cheque {cheque.id}: {e}")
                
                cheques.append({
                    'id': cheque.id,
                    'fecha': cheque.fecha.strftime('%Y-%m-%d') if cheque.fecha else '',
                    'vale': cheque.vale or '',
                    'folio': cheque.folio or '',
                    'proveedor': cheque.proveedor.nombre if cheque.proveedor else '',
                    'monto': str(cheque.monto) if cheque.monto else '0.00',
                    'clase': clase_factura,
                    'layout': cheque.layout.id if cheque.layout else None,
                    'layout_nombre': cheque.layout.nombre if cheque.layout else None
                })
            
            self.logger.info(f"Búsqueda completada: {len(cheques)} cheques encontrados")
            return cheques
            
        except Exception as e:
            self.logger.error(f"Error en búsqueda de cheques: {e}")
            return []
    
    def search_layouts(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Busca layouts en la base de datos aplicando filtros
        
        Args:
            filters: Diccionario con filtros de búsqueda
            
        Returns:
            Lista de diccionarios con datos de layouts
        """
        if not self.db_available:
            return None

        try:
            # Construir consulta base
            query = Layout.select()
            
            # Aplicar filtro de fecha inicial
            if filters.get('fecha_inicial'):
                fecha_inicial = self._parse_date(filters['fecha_inicial'])
                if fecha_inicial:
                    query = query.where(Layout.fecha >= fecha_inicial)
            
            # Aplicar filtro de fecha final
            if filters.get('fecha_final'):
                fecha_final = self._parse_date(filters['fecha_final'])
                if fecha_final:
                    query = query.where(Layout.fecha <= fecha_final)
            
            # Ejecutar consulta y convertir a lista de diccionarios
            layouts = []
            for layout in query:
                layouts.append({
                    'id': layout.id,
                    'fecha': layout.fecha.strftime('%Y-%m-%d') if layout.fecha else '',
                    'nombre': layout.nombre or '',
                    'monto': str(layout.monto) if layout.monto else '0.00'
                })
            
            self.logger.info(f"Búsqueda de layouts completada: {len(layouts)} layouts encontrados")
            return layouts
            
        except Exception as e:
            self.logger.error(f"Error en búsqueda de layouts: {e}")
            return None
        
    def show_layout_content(self, layout_id: int):
        """ Muestra el contenido de un layout"""
        if not self.db_available:
            self.logger.warning("Base de datos no disponible para mostrar contenido de Layout")
            return None

        try:
            layout = Layout.get(Layout.id == layout_id)
            if layout:
                self.logger.info(f"Contenido del Layout {layout_id}: {layout.nombre}")
                # Obtener los cheques relacionados al layout
                cheques = []
                for cheque in layout.cheques:
                    descripcion = ""
                    for factura in cheque.facturas:
                        # Si la factura tiene un vale asociado
                        if hasattr(factura, "vale") and factura.vale:
                            try:
                                # Obtener el primer (y único) vale de la consulta
                                vale_obj = factura.vale.first()
                                
                                if vale_obj and hasattr(vale_obj, "descripcion") and vale_obj.descripcion:
                                    descripcion += f"{vale_obj.descripcion} "
                            except Exception as e:
                                self.logger.warning(f"Error al obtener vale de factura: {e}")
                    
                    descripcion = descripcion.strip()

                    cheques.append({
                        'id': cheque.id,
                        'fecha': cheque.fecha.strftime('%Y-%m-%d') if cheque.fecha else '',
                        'vale': cheque.vale or '',
                        'folio': cheque.folio or '',
                        'codigo': cheque.proveedor.codigo_quiter if cheque.proveedor else '',
                        'proveedor': cheque.proveedor.nombre or '',
                        'descripcion': descripcion,
                        'monto': float(cheque.monto) if cheque.monto else 0.00,
                        'banco': cheque.banco or ''
                    })
                self.logger.info(f"Cheques en el Layout {layout_id}: {len(cheques)} encontrados")

                return cheques

        except Exception as e:
            self.logger.error(f"Error mostrando contenido de layout {layout_id}: {e}")
            return None

    def _parse_date(self, date_str: str) -> Optional[date]:
        """Convierte string de fecha a objeto date"""
        if not date_str:
            return None
        
        try:
            # Intentar diferentes formatos de fecha
            for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y']:
                try:
                    return datetime.strptime(date_str, fmt).date()
                except ValueError:
                    continue
            
            self.logger.warning(f"No se pudo parsear la fecha: {date_str}")
            return None
            
        except Exception as e:
            self.logger.error(f"Error parseando fecha {date_str}: {e}")
            return None
    
    def is_available(self) -> bool:
        """Retorna True si la base de datos está disponible"""
        return self.db_available
    
    def get_database_info(self) -> Dict[str, Any]:
        """Retorna información sobre el estado de la base de datos"""
        return {
            'available': self.db_available,
            'cheque_model': Cheque is not None,
            'layout_model': Layout is not None,
            'connection_status': 'connected' if self.db_available else 'disconnected'
        }
    
    def create_layout(self, nombre: str, fecha: str, monto: float = 0.0) -> Optional[int]:
        """
        Crea un nuevo layout
        
        Args:
            nombre: Nombre del layout
            fecha: Fecha del layout en formato YYYY-MM-DD
            monto: Monto total del layout
            
        Returns:
            ID del layout creado o None si hay error
        """
        if not self.db_available:
            self.logger.warning("Base de datos no disponible para crear layout")
            return None
        
        try:
            fecha_obj = self._parse_date(fecha)
            if not fecha_obj:
                self.logger.error(f"Fecha inválida: {fecha}")
                return None
            
            layout = Layout.create(
                nombre=nombre,
                fecha=fecha_obj,
                monto=monto
            )
            
            self.logger.info(f"Layout creado con ID: {layout.id}")
            return layout.id
            
        except Exception as e:
            self.logger.error(f"Error creando layout: {e}")
            return None
    
    def assign_cheques_to_layout(self, layout_id: int, cheque_ids: List[int]) -> bool:
        """
        Asigna una lista de cheques a un layout
        
        Args:
            layout_id: ID del layout
            cheque_ids: Lista de IDs de cheques
            
        Returns:
            True si la asignación fue exitosa
        """
        if not self.db_available:
            self.logger.warning("Base de datos no disponible para asignar cheques")
            return False
        
        try:
            # Verificar que el layout existe
            layout = Layout.get_by_id(layout_id)
            
            # Actualizar los cheques
            updated_count = 0
            for cheque_id in cheque_ids:
                try:
                    cheque = Cheque.get_by_id(cheque_id)
                    cheque.layout = layout
                    cheque.save()
                    updated_count += 1
                except Exception as e:
                    self.logger.warning(f"Error asignando cheque {cheque_id}: {e}")
            
            # Actualizar el monto total del layout
            total_monto = Cheque.select(fn.SUM(Cheque.monto)).where(Cheque.layout == layout).scalar() or 0
            layout.monto = total_monto
            layout.save()
            
            self.logger.info(f"Asignados {updated_count} cheques al layout {layout_id}")
            return updated_count > 0
            
        except Exception as e:
            self.logger.error(f"Error asignando cheques al layout: {e}")
            return False
    
    def remove_cheques_from_layout(self, cheque_ids: List[int]) -> bool:
        """
        Remueve cheques de su layout asignado
        
        Args:
            cheque_ids: Lista de IDs de cheques
            
        Returns:
            True si la remoción fue exitosa
        """
        if not self.db_available:
            self.logger.warning("Base de datos no disponible para remover cheques")
            return False
        
        try:
            updated_count = 0
            for cheque_id in cheque_ids:
                try:
                    cheque = Cheque.get_by_id(cheque_id)
                    old_layout = cheque.layout
                    cheque.layout = None
                    cheque.save()
                    
                    # Actualizar el monto del layout anterior si existe
                    if old_layout:
                        total_monto = Cheque.select(fn.SUM(Cheque.monto)).where(Cheque.layout == old_layout).scalar() or 0
                        old_layout.monto = total_monto
                        old_layout.save()
                    
                    updated_count += 1
                except Exception as e:
                    self.logger.warning(f"Error removiendo cheque {cheque_id}: {e}")
            
            self.logger.info(f"Removidos {updated_count} cheques de sus layouts")
            return updated_count > 0
            
        except Exception as e:
            self.logger.error(f"Error removiendo cheques de layouts: {e}")
            return False

    def get_layout_by_id(self, layout_id: int) -> Optional[Any]:
        """
        Obtiene un layout por su ID
        
        Args:
            layout_id: ID del layout a buscar
            
        Returns:
            Objeto Layout si se encuentra, None en caso contrario
        """
        if not self.db_available:
            self.logger.warning("Base de datos no disponible")
            return None
            
        try:
            layout = Layout.get_by_id(layout_id)
            self.logger.info(f"Layout {layout_id} encontrado: {layout.nombre}")
            return layout
            
        except Layout.DoesNotExist:
            self.logger.warning(f"Layout con ID {layout_id} no encontrado")
            return None
        except Exception as e:
            self.logger.error(f"Error obteniendo layout {layout_id}: {e}")
            return None

    def delete_layout(self, layout_id: int) -> bool:
        """
        Elimina un layout y desasocia todos los cheques de ese layout
        
        Args:
            layout_id: ID del layout a eliminar
            
        Returns:
            True si se eliminó exitosamente, False en caso contrario
        """
        if not self.db_available:
            self.logger.warning("Base de datos no disponible")
            return False
            
        try:
            # Primero verificar que el layout existe
            layout = Layout.get_by_id(layout_id)
            layout_nombre = layout.nombre
            
            # Desasociar todos los cheques de este layout
            cheques_count = Cheque.update(layout=None).where(Cheque.layout == layout_id).execute()
            self.logger.info(f"Desasociados {cheques_count} cheques del layout {layout_id}")
            
            # Eliminar el layout
            layout.delete_instance()
            
            self.logger.info(f"Layout '{layout_nombre}' (ID: {layout_id}) eliminado exitosamente")
            return True
            
        except Layout.DoesNotExist:
            self.logger.warning(f"Layout con ID {layout_id} no encontrado")
            return False
        except Exception as e:
            self.logger.error(f"Error eliminando layout {layout_id}: {e}")
            return False

    def update_layout_name(self, layout_id: int, nuevo_nombre: str) -> bool:
        """
        Actualiza el nombre de un layout
        
        Args:
            layout_id: ID del layout a actualizar
            nuevo_nombre: Nuevo nombre para el layout
            
        Returns:
            True si se actualizó exitosamente, False en caso contrario
        """
        if not self.db_available:
            self.logger.warning("Base de datos no disponible")
            return False
            
        if not nuevo_nombre or not nuevo_nombre.strip():
            self.logger.warning("El nuevo nombre no puede estar vacío")
            return False
            
        try:
            # Verificar que el layout existe
            layout = Layout.get_by_id(layout_id)
            nombre_anterior = layout.nombre
            
            # Actualizar el nombre
            layout.nombre = nuevo_nombre.strip()
            layout.save()
            
            self.logger.info(f"Layout ID {layout_id}: nombre actualizado de '{nombre_anterior}' a '{nuevo_nombre.strip()}'")
            return True
            
        except Layout.DoesNotExist:
            self.logger.warning(f"Layout con ID {layout_id} no encontrado")
            return False
        except Exception as e:
            self.logger.error(f"Error actualizando nombre del layout {layout_id}: {e}")
            return False
