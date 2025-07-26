"""
Controlador para la lógica de búsqueda y filtros
"""
import sys
import os
from typing import List, Dict, Any, Optional
import logging
import traceback

# Agregar path para imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

try:
    from ..models.search_models import SearchFilters, SearchState, FacturaData
    from bd.models import Factura, Proveedor, Vale
except ImportError:
    from models.search_models import SearchFilters, SearchState, FacturaData
    # Fallback import para Vale
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'src'))
    from bd.models import Factura, Proveedor, Vale


class SearchController:
    """Controlador que maneja la lógica de búsqueda y filtros"""
    
    def __init__(self, bd_control=None):
        self.bd_control = bd_control
        self.state = SearchState()
        self.logger = logging.getLogger(__name__)
    
    def load_facturas(self) -> bool:
        """
        Carga todas las facturas desde la base de datos
        
        Returns:
            bool: True si se cargaron correctamente
        """
        try:
            self.logger.info("Cargando facturas desde la base de datos...")
            
            if not self.bd_control:
                self.logger.warning("Base de datos no disponible")
                self.state.database_available = False
                self.state.using_sample_data = False
                self.state.all_facturas.clear()
                return False
            
            # Verificar si hay facturas en la base de datos
            facturas_count = Factura.select().count()
            if facturas_count == 0:
                self.logger.info("No hay facturas en la base de datos")
                self.state.database_available = True
                self.state.using_sample_data = False
                self.state.all_facturas.clear()
                return True
            
            # Consultar todas las facturas con información del proveedor
            facturas_query = (Factura
                            .select()
                            .join(Proveedor, on=(Factura.proveedor == Proveedor.id))
                            .order_by(Factura.fecha.desc()))
            
            facturas_data = []
            for factura in facturas_query:
                # Obtener el vale asociado si existe
                vale_asociado = None
                try:
                    # Buscar vale por factura_id usando el modelo correcto
                    vale_asociado = Vale.get(Vale.factura_id == factura.folio_interno)
                except Vale.DoesNotExist:
                    vale_asociado = None
                except Exception as e:
                    self.logger.debug(f"Error buscando vale para factura {factura.folio_interno}: {e}")
                    vale_asociado = None
                
                factura_data = FacturaData(
                    folio_interno=str(factura.folio_interno),
                    tipo=factura.tipo,
                    no_vale=str(vale_asociado.noVale) if vale_asociado else "",
                    fecha=self._format_date_for_display(factura.fecha),
                    folio_xml=f"{factura.serie or ''} {factura.folio or ''}".strip(),
                    serie=factura.serie,
                    folio=factura.folio,
                    nombre_emisor=factura.nombre_emisor,
                    rfc_emisor=factura.rfc_emisor,
                    conceptos=self._format_conceptos(factura.conceptos),
                    total=float(factura.total) if factura.total else 0.0,
                    subtotal=float(factura.subtotal) if factura.subtotal else 0.0,
                    iva_trasladado=float(factura.iva_trasladado) if factura.iva_trasladado else 0.0,
                    ret_iva=float(factura.ret_iva) if factura.ret_iva else 0.0,
                    ret_isr=float(factura.ret_isr) if factura.ret_isr else 0.0,
                    clase=factura.clase,
                    cargada=bool(factura.cargada),
                    pagada=bool(factura.pagada),
                    comentario=factura.comentario
                )
                facturas_data.append(factura_data.to_dict())
            
            self.state.all_facturas = facturas_data
            self.state.database_available = True
            self.state.using_sample_data = False
            self.state.clear_results()  # Iniciar con tabla vacía
            
            self.logger.info(f"Cargadas {len(facturas_data)} facturas correctamente")
            return True
            
        except Exception as e:
            self.logger.error(f"Error al cargar facturas: {e}")
            traceback.print_exc()
            self.state.database_available = False
            self.state.using_sample_data = False
            self.state.all_facturas.clear()
            return False
    
    def load_proveedores(self) -> bool:
        """
        Carga la lista de proveedores para los filtros
        
        Returns:
            bool: True si se cargaron correctamente
        """
        try:
            if not self.bd_control:
                # Datos de ejemplo
                self.state.proveedores_data = [
                    {'id': 1, 'nombre': 'ABC Proveedores', 'rfc': 'ABC123456789', 
                     'telefono': '555-1234', 'email': 'contacto@abc.com', 'nombre_contacto': 'Juan Pérez'},
                    {'id': 2, 'nombre': 'XYZ Servicios', 'rfc': 'XYZ987654321', 
                     'telefono': '555-5678', 'email': 'info@xyz.com', 'nombre_contacto': 'María González'},
                    {'id': 3, 'nombre': 'Proveedores Varios', 'rfc': 'VAR456789123', 
                     'telefono': '555-9012', 'email': 'ventas@varios.com', 'nombre_contacto': 'Carlos López'}
                ]
                return True
            
            from bd.models import Proveedor
            
            proveedores = list(Proveedor.select().order_by(Proveedor.nombre))
            
            self.state.proveedores_data = []
            for p in proveedores:
                proveedor_data = {
                    'id': p.id,
                    'nombre': p.nombre,
                    'rfc': p.rfc,
                    'telefono': p.telefono or '',
                    'email': p.email or '',
                    'nombre_contacto': p.nombre_contacto or ''
                }
                self.state.proveedores_data.append(proveedor_data)
            
            self.logger.info(f"Cargados {len(self.state.proveedores_data)} proveedores")
            return True
            
        except Exception as e:
            self.logger.error(f"Error cargando proveedores: {e}")
            self.state.proveedores_data = []
            return False
    
    def apply_filters(self, filters: SearchFilters) -> List[Dict[str, Any]]:
        """
        Aplica los filtros a las facturas
        
        Args:
            filters: Filtros a aplicar
            
        Returns:
            List[Dict[str, Any]]: Lista de facturas filtradas
        """
        try:
            if not filters.has_active_filters():
                self.logger.info("No hay filtros activos - mostrando todas las facturas")
                self.state.set_filtered_results(self.state.all_facturas.copy())
                return self.state.filtered_facturas
            
            self.logger.info("Aplicando filtros...")
            filtered_data = []
            
            for i, factura in enumerate(self.state.all_facturas):
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
        # Filtro por fecha inicial
        if filters.fecha_inicial:
            fecha_factura = self._normalize_date(factura.get('fecha', ''))
            fecha_inicial_norm = self._normalize_date(filters.fecha_inicial)
            if fecha_factura < fecha_inicial_norm:
                return False
        
        # Filtro por fecha final
        if filters.fecha_final:
            fecha_factura = self._normalize_date(factura.get('fecha', ''))
            fecha_final_norm = self._normalize_date(filters.fecha_final)
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
            folio = str(factura.get('folio', ''))
            
            if (filters.no_vale_filtro not in no_vale_factura and 
                filters.no_vale_filtro not in folio_interno and 
                filters.no_vale_filtro not in serie_folio and 
                filters.no_vale_filtro not in folio):
                return False
        
        # Filtro Solo Cargado
        if filters.solo_cargado:
            if not factura.get('cargada_bool', False):
                return False
        
        # Filtro Solo Pagado
        if filters.solo_pagado:
            if not factura.get('pagada_bool', False):
                return False
        
        # Filtro de búsqueda de texto
        if filters.texto_busqueda:
            searchable_text = ' '.join([
                str(factura.get("folio_interno", "")),
                str(factura.get("serie_folio", "")),
                str(factura.get("tipo", "")),
                str(factura.get("nombre_emisor", "")),
                str(factura.get("conceptos", "")),
                str(factura.get("rfc_emisor", "")),
                str(factura.get("rfc_receptor", ""))
            ]).lower()
            
            if filters.texto_busqueda.lower() not in searchable_text:
                return False
        
        return True
    
    def _format_conceptos(self, conceptos) -> str:
        """Formatea la lista de conceptos para mostrar en la tabla"""
        try:
            if not conceptos:
                return ""
            
            conceptos_list = list(conceptos)
            if not conceptos_list:
                return ""
            
            # Extraer solo las descripciones de todos los conceptos
            descripciones = []
            for concepto in conceptos_list:
                if concepto.descripcion:
                    descripciones.append(concepto.descripcion.strip())
            
            if not descripciones:
                return ""
            
            # Unir conceptos con "/"
            conceptos_str = " / ".join(descripciones)
            
            # Limitar longitud para evitar texto muy largo
            if len(conceptos_str) > 150:  # Limitar a 150 caracteres
                conceptos_str = conceptos_str[:147] + "..."
            
            return conceptos_str
                
        except Exception:
            return ""
    
    def get_state(self) -> SearchState:
        """Obtiene el estado actual de la búsqueda"""
        return self.state
    
    def clear_filters(self) -> None:
        """Limpia los resultados filtrados"""
        self.state.clear_results()
    
    def _normalize_date(self, date_str: str) -> str:
        """
        Normaliza una fecha al formato YYYY-MM-DD para comparación
        
        Args:
            date_str: Fecha como string en cualquier formato
            
        Returns:
            str: Fecha en formato YYYY-MM-DD
        """
        if not date_str:
            return ""
        
        try:
            from datetime import datetime
            
            # Si ya está en formato YYYY-MM-DD, devolverlo tal como está
            if len(date_str) == 10 and date_str.count('-') == 2:
                parts = date_str.split('-')
                if len(parts[0]) == 4:  # Año de 4 dígitos al inicio
                    return date_str
            
            # Intentar parsear diferentes formatos de fecha
            formats_to_try = [
                '%Y-%m-%d',    # 2024-07-24
                '%d/%m/%Y',    # 24/07/2024
                '%m/%d/%Y',    # 07/24/2024
                '%d-%m-%Y',    # 24-07-2024
                '%m-%d-%Y',    # 07-24-2024
                '%Y/%m/%d',    # 2024/07/24
                '%Y.%m.%d',    # 2024.07.24
                '%d.%m.%Y',    # 24.07.2024
            ]
            
            for fmt in formats_to_try:
                try:
                    dt = datetime.strptime(date_str, fmt)
                    return dt.strftime('%Y-%m-%d')
                except ValueError:
                    continue
            
            # Si no se puede parsear, devolver la fecha original
            return date_str
            
        except Exception:
            return date_str
    
    def _format_date_for_display(self, date_value) -> str:
        """
        Formatea una fecha de la base de datos para mostrar en formato YYYY-MM-DD
        
        Args:
            date_value: Valor de fecha de la base de datos (puede ser datetime, date, o string)
            
        Returns:
            str: Fecha en formato YYYY-MM-DD
        """
        if not date_value:
            return ""
        
        try:
            from datetime import datetime, date
            
            # Si es datetime o date, convertir a string
            if hasattr(date_value, 'strftime'):
                return date_value.strftime('%Y-%m-%d')
            
            # Si es string, normalizar
            return self._normalize_date(str(date_value))
            
        except Exception:
            return str(date_value) if date_value else ""
