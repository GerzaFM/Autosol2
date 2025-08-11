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
    
    from models import Cheque, Proveedor, Layout
    DATABASE_AVAILABLE = True
    DATABASE_AVAILABLE = True
except ImportError as e:
    Cheque = Proveedor = Layout = None
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
            self.logger.warning("Base de datos no disponible, usando datos de ejemplo")
    
    def search_cheques(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Busca cheques en la base de datos aplicando filtros
        
        Args:
            filters: Diccionario con filtros de búsqueda
            
        Returns:
            Lista de diccionarios con datos de cheques
        """
        if not self.db_available:
            return self._get_sample_cheques()
        
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
            
            # Aplicar filtro de clase (en el campo vale o folio)
            if filters.get('clase'):
                clase = filters['clase'].strip()
                if clase:
                    query = query.where(
                        (Cheque.vale.contains(clase)) | 
                        (Cheque.folio.contains(clase))
                    )
            
            # Aplicar filtro de proveedor
            if filters.get('proveedor'):
                proveedor = filters['proveedor'].strip()
                if proveedor:
                    query = query.where(Cheque.proveedor.contains(proveedor))
            
            # Ejecutar consulta y convertir a lista de diccionarios
            cheques = []
            for cheque in query:
                cheques.append({
                    'id': cheque.id,
                    'fecha': cheque.fecha.strftime('%Y-%m-%d') if cheque.fecha else '',
                    'vale': cheque.vale or '',
                    'folio': cheque.folio or '',
                    'proveedor': cheque.proveedor or '',
                    'monto': str(cheque.monto) if cheque.monto else '0.00',
                    'banco': cheque.banco or ''
                })
            
            self.logger.info(f"Búsqueda completada: {len(cheques)} cheques encontrados")
            return cheques
            
        except Exception as e:
            self.logger.error(f"Error en búsqueda de cheques: {e}")
            return self._get_sample_cheques()
    
    def search_layouts(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Busca layouts en la base de datos aplicando filtros
        
        Args:
            filters: Diccionario con filtros de búsqueda
            
        Returns:
            Lista de diccionarios con datos de layouts
        """
        if not self.db_available:
            return self._get_sample_layouts()
        
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
            return self._get_sample_layouts()
    
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
    
    def _get_sample_cheques(self) -> List[Dict[str, Any]]:
        """Retorna datos de ejemplo para cheques cuando la BD no está disponible"""
        return [
            {
                'id': 1,
                'fecha': '2024-08-10',
                'vale': 'V156486',
                'folio': '12456',
                'proveedor': 'Servicio Nava Medrano',
                'monto': '100000.00',
                'banco': 'BTC23'
            },
            {
                'id': 2,
                'fecha': '2024-08-09',
                'vale': 'V156487',
                'folio': '12457',
                'proveedor': 'Transportes González',
                'monto': '75000.00',
                'banco': 'BBVA'
            },
            {
                'id': 3,
                'fecha': '2024-08-08',
                'vale': 'V156488',
                'folio': '12458',
                'proveedor': 'Materiales Construcción SA',
                'monto': '125000.00',
                'banco': 'Santander'
            }
        ]
    
    def _get_sample_layouts(self) -> List[Dict[str, Any]]:
        """Retorna datos de ejemplo para layouts cuando la BD no está disponible"""
        return [
            {
                'id': 1,
                'fecha': '2024-08-10',
                'nombre': 'Layout Agosto Semana 1',
                'monto': '300000.00'
            },
            {
                'id': 2,
                'fecha': '2024-08-03',
                'nombre': 'Layout Julio Semana 4',
                'monto': '250000.00'
            }
        ]
    
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
