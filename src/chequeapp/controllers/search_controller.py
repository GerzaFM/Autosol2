"""
Controlador de búsqueda para la aplicación de Cheques
Adaptado de buscar_app_refactored
"""
import logging
from typing import List, Dict, Any, Optional
from datetime import date, datetime
import traceback

# Importar modelos de base de datos
try:
    import sys
    import os
    bd_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'bd')
    sys.path.insert(0, bd_path)
    from models import Factura, Proveedor, Vale
    from bd_control import DBManager
    DB_AVAILABLE = True
except ImportError as e:
    Factura = Proveedor = Vale = DBManager = None
    DB_AVAILABLE = False

# Importar configuración
try:
    solicitudapp_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'solicitudapp')
    sys.path.insert(0, solicitudapp_path)
    from config.app_config import AppConfig
    CONFIG_AVAILABLE = True
except ImportError:
    AppConfig = None
    CONFIG_AVAILABLE = False


class SearchFilters:
    """Clase para encapsular filtros de búsqueda"""
    
    def __init__(self, fecha_inicial: str = '', fecha_final: str = '', tipo_filtro: str = '',
                 proveedor_filtro: str = '', no_vale_filtro: str = '', clase_filtro: str = '',
                 solo_cargado: bool = False, solo_pagado: bool = False, texto_busqueda: str = ''):
        self.fecha_inicial = fecha_inicial
        self.fecha_final = fecha_final
        self.tipo_filtro = tipo_filtro
        self.proveedor_filtro = proveedor_filtro
        self.no_vale_filtro = no_vale_filtro
        self.clase_filtro = clase_filtro
        self.solo_cargado = solo_cargado
        self.solo_pagado = solo_pagado
        self.texto_busqueda = texto_busqueda
    
    def has_active_filters(self) -> bool:
        """Verifica si hay filtros activos"""
        return bool(
            self.fecha_inicial or self.fecha_final or self.tipo_filtro or
            self.proveedor_filtro or self.no_vale_filtro or self.clase_filtro or
            self.solo_cargado or self.solo_pagado or self.texto_busqueda
        )


class SearchState:
    """Estado de búsqueda y datos cargados"""
    
    def __init__(self):
        self.tipos_data = []
        self.proveedores_data = []
        self.all_facturas = []
        self.filtered_facturas = []
    
    def set_filtered_results(self, results: List[Dict[str, Any]]):
        """Establece los resultados filtrados"""
        self.filtered_facturas = results


class SearchController:
    """Controlador para búsqueda de facturas en la aplicación de cheques"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.state = SearchState()
        
        if DB_AVAILABLE:
            self.db_manager = DBManager()
        else:
            self.db_manager = None
            self.logger.warning("Base de datos no disponible")
    
    def load_initial_data(self):
        """Carga los datos iniciales necesarios"""
        try:
            self.load_tipos_vale()
            self.load_proveedores()
            self.logger.info("Datos iniciales cargados correctamente")
        except Exception as e:
            self.logger.error(f"Error cargando datos iniciales: {e}")
    
    def load_tipos_vale(self):
        """Carga los tipos de vale desde la configuración"""
        try:
            if CONFIG_AVAILABLE and hasattr(AppConfig, 'TIPO_VALE'):
                self.state.tipos_data = []
                for clave, descripcion in AppConfig.TIPO_VALE.items():
                    self.state.tipos_data.append({
                        'clave': clave,
                        'descripcion': descripcion,
                        'display': f"{clave} - {descripcion}"
                    })
                self.logger.info(f"Tipos de vale cargados: {len(self.state.tipos_data)} tipos")
            else:
                self.logger.warning("Configuración de tipos de vale no disponible")
        except Exception as e:
            self.logger.error(f"Error cargando tipos de vale: {e}")
    
    def load_proveedores(self):
        """Carga los proveedores desde la base de datos"""
        try:
            if not DB_AVAILABLE or not self.db_manager:
                self.logger.warning("Base de datos no disponible para cargar proveedores")
                return
                
            self.state.proveedores_data = []
            proveedores = Proveedor.select()
            
            for proveedor in proveedores:
                self.state.proveedores_data.append({
                    'id': proveedor.id,
                    'nombre': proveedor.nombre or '',
                    'rfc': proveedor.rfc or '',
                    'telefono': proveedor.telefono or '',
                    'email': proveedor.email or '',
                    'contacto': proveedor.nombre_contacto or ''
                })
            
            self.logger.info(f"Proveedores cargados: {len(self.state.proveedores_data)} proveedores")
            
        except Exception as e:
            self.logger.error(f"Error cargando proveedores: {e}")
    
    def load_initial_data(self):
        """Carga los datos iniciales desde la base de datos"""
        try:
            self.logger.info("Cargando datos iniciales...")
            self.load_tipos()
            self.load_proveedores()
            self.load_all_facturas()
            self.logger.info("Datos iniciales cargados exitosamente")
            return True
        except Exception as e:
            self.logger.error(f"Error cargando datos iniciales: {e}")
            return False
    
    def load_all_facturas(self):
        """Carga todas las facturas desde la base de datos"""
        try:
            if not DB_AVAILABLE or not self.db_manager:
                self.logger.warning("Base de datos no disponible para cargar facturas")
                return
            
            self.state.all_facturas = []
            
            # Query para obtener facturas con información relacionada
            query = (Factura
                    .select(Factura, Proveedor.nombre.alias('proveedor_nombre'), 
                           Vale.noVale, Vale.tipo)
                    .join(Proveedor, on=(Factura.proveedor == Proveedor.id))
                    .switch(Factura)
                    .join(Vale, join_type='LEFT OUTER', on=(Factura.id == Vale.factura)))
            
            for factura in query:
                factura_data = {
                    'id': factura.id,
                    'folio_interno': factura.folioInterno or '',
                    'serie_folio': f"{factura.serie or ''}-{factura.folio or ''}".strip('-'),
                    'fecha': factura.fecha.strftime('%Y-%m-%d') if factura.fecha else '',
                    'nombre_emisor': getattr(factura, 'proveedor_nombre', '') or '',
                    'rfc_emisor': factura.rfcEmisor or '',
                    'subtotal': float(factura.subtotal or 0),
                    'descuento': float(factura.descuento or 0),
                    'total': float(factura.total or 0),
                    'moneda': factura.moneda or 'MXN',
                    'tipo_comprobante': factura.tipoDeComprobante or '',
                    'uso_cfdi': factura.usoCFDI or '',
                    'metodo_pago': factura.metodoDePago or '',
                    'forma_pago': factura.formaDePago or '',
                    'cargada': factura.cargada or False,
                    'pagada': factura.pagada or False,
                    'no_vale': getattr(factura, 'noVale', '') if hasattr(factura, 'noVale') else '',
                    'tipo': getattr(factura, 'tipo', '') if hasattr(factura, 'tipo') else '',
                    'clase': factura.clase or '',
                    'proveedor_id': factura.proveedor.id if factura.proveedor else None
                }
                self.state.all_facturas.append(factura_data)
            
            self.logger.info(f"Facturas cargadas: {len(self.state.all_facturas)} facturas")
            
        except Exception as e:
            self.logger.error(f"Error cargando facturas: {e}")
            traceback.print_exc()
    
    def apply_filters(self, filters_dict: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Aplica los filtros a las facturas
        
        Args:
            filters_dict: Diccionario con los filtros
            
        Returns:
            Lista de facturas filtradas
        """
        try:
            # Convertir diccionario a objeto SearchFilters
            filters = SearchFilters(
                fecha_inicial=filters_dict.get('fecha_inicio', ''),
                fecha_final=filters_dict.get('fecha_fin', ''),
                tipo_filtro=filters_dict.get('tipo_filtro', ''),
                proveedor_filtro=filters_dict.get('proveedor_filtro', ''),
                no_vale_filtro=filters_dict.get('no_vale_filtro', ''),
                clase_filtro=filters_dict.get('clase_filtro', ''),
                solo_cargado=filters_dict.get('solo_cargadas', False),
                solo_pagado=filters_dict.get('solo_pagadas', False),
                texto_busqueda=filters_dict.get('texto_busqueda', '')
            )
            
            if not filters.has_active_filters():
                self.logger.info("No hay filtros activos - mostrando todas las facturas")
                self.state.set_filtered_results(self.state.all_facturas.copy())
                return self.state.filtered_facturas
            
            self.logger.info("Aplicando filtros...")
            filtered_data = []
            
            for factura in self.state.all_facturas:
                if self._factura_matches_filters(factura, filters):
                    filtered_data.append(factura)
            
            self.state.set_filtered_results(filtered_data)
            self.logger.info(f"Filtros aplicados - {len(filtered_data)} resultados de {len(self.state.all_facturas)} totales")
            
            return self.state.filtered_facturas
            
        except Exception as e:
            self.logger.error(f"Error aplicando filtros: {e}")
            traceback.print_exc()
            return []
    
    def _factura_matches_filters(self, factura: Dict[str, Any], filters: SearchFilters) -> bool:
        """
        Verifica si una factura cumple con los filtros
        
        Args:
            factura: Datos de la factura
            filters: Filtros a verificar
            
        Returns:
            bool: True si la factura cumple con los filtros
        """
        try:
            # Filtro por fecha inicial
            if filters.fecha_inicial:
                fecha_factura = self._normalize_date(factura.get('fecha', ''))
                if isinstance(filters.fecha_inicial, date):
                    fecha_inicial_norm = filters.fecha_inicial
                else:
                    fecha_inicial_norm = self._normalize_date(str(filters.fecha_inicial))
                if fecha_factura < fecha_inicial_norm:
                    return False
            
            # Filtro por fecha final
            if filters.fecha_final:
                fecha_factura = self._normalize_date(factura.get('fecha', ''))
                if isinstance(filters.fecha_final, date):
                    fecha_final_norm = filters.fecha_final
                else:
                    fecha_final_norm = self._normalize_date(str(filters.fecha_final))
                if fecha_factura > fecha_final_norm:
                    return False
            
            # Filtro por tipo
            if filters.tipo_filtro:
                tipo_codigo = filters.tipo_filtro.split(' - ')[0] if ' - ' in filters.tipo_filtro else filters.tipo_filtro
                if factura.get('tipo', '') != tipo_codigo:
                    return False
            
            # Filtro por proveedor
            if filters.proveedor_filtro:
                emisor = factura.get('nombre_emisor', '').lower()
                if filters.proveedor_filtro.lower() not in emisor:
                    return False
            
            # Filtro por número de vale
            if filters.no_vale_filtro:
                no_vale_factura = str(factura.get('no_vale', ''))
                folio_interno = str(factura.get('folio_interno', ''))
                serie_folio = str(factura.get('serie_folio', ''))
                
                if (filters.no_vale_filtro not in no_vale_factura and 
                    filters.no_vale_filtro not in folio_interno and 
                    filters.no_vale_filtro not in serie_folio):
                    return False
            
            # Filtro por clase
            if filters.clase_filtro:
                clase_factura = factura.get('clase', '').lower()
                if filters.clase_filtro.lower() not in clase_factura:
                    return False
            
            # Filtro solo cargadas
            if filters.solo_cargado:
                if not factura.get('cargada', False):
                    return False
            
            # Filtro solo pagadas
            if filters.solo_pagado:
                if not factura.get('pagada', False):
                    return False
            
            # Filtro de búsqueda de texto
            if filters.texto_busqueda:
                texto_busqueda = filters.texto_busqueda.lower()
                campos_busqueda = [
                    str(factura.get('folio_interno', '')),
                    str(factura.get('serie_folio', '')),
                    str(factura.get('nombre_emisor', '')),
                    str(factura.get('rfc_emisor', '')),
                    str(factura.get('no_vale', '')),
                    str(factura.get('clase', '')),
                    str(factura.get('tipo', ''))
                ]
                
                texto_completo = ' '.join(campos_busqueda).lower()
                if texto_busqueda not in texto_completo:
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error verificando filtros para factura {factura.get('id', 'N/A')}: {e}")
            return False
    
    def _normalize_date(self, date_str: str) -> date:
        """
        Normaliza una fecha desde string a objeto date
        
        Args:
            date_str: Fecha en formato string
            
        Returns:
            date: Objeto date normalizado
        """
        try:
            if isinstance(date_str, date):
                return date_str
            
            if not date_str:
                return date.min
                
            # Intentar varios formatos de fecha
            formats = ['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y', '%Y/%m/%d']
            
            for fmt in formats:
                try:
                    return datetime.strptime(date_str, fmt).date()
                except ValueError:
                    continue
            
            # Si no se puede parsear, retornar fecha mínima
            return date.min
            
        except Exception as e:
            self.logger.error(f"Error normalizando fecha '{date_str}': {e}")
            return date.min
    
    def clear_filters(self):
        """Limpia todos los filtros y resetea los resultados"""
        try:
            self.state.set_filtered_results(self.state.all_facturas.copy())
            self.logger.info("Filtros limpiados")
        except Exception as e:
            self.logger.error(f"Error limpiando filtros: {e}")
    
    def get_state(self) -> SearchState:
        """Retorna el estado actual de búsqueda"""
        return self.state
