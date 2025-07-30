"""
Modelos para el estado de búsqueda y filtros
"""
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime


@dataclass
class SearchFilters:
    """Modelo que encapsula todos los filtros de búsqueda"""
    fecha_inicial: Optional[str] = None
    fecha_final: Optional[str] = None
    tipo_filtro: Optional[str] = None
    proveedor_filtro: Optional[str] = None
    no_vale_filtro: Optional[str] = None
    solo_cargado: bool = False
    solo_pagado: bool = False
    texto_busqueda: Optional[str] = None
    
    def has_active_filters(self) -> bool:
        """Verifica si hay al menos un filtro activo"""
        return any([
            self.fecha_inicial, self.fecha_final, self.tipo_filtro,
            self.proveedor_filtro, self.no_vale_filtro,
            self.solo_cargado, self.solo_pagado, self.texto_busqueda
        ])
    
    def clear(self) -> None:
        """Limpia todos los filtros"""
        self.fecha_inicial = None
        self.fecha_final = None
        self.tipo_filtro = None
        self.proveedor_filtro = None
        self.no_vale_filtro = None
        self.solo_cargado = False
        self.solo_pagado = False
        self.texto_busqueda = None


@dataclass
class SearchState:
    """Modelo que encapsula el estado completo de la búsqueda"""
    all_facturas: List[Dict[str, Any]] = field(default_factory=list)
    filtered_facturas: List[Dict[str, Any]] = field(default_factory=list)
    proveedores_data: List[Dict[str, Any]] = field(default_factory=list)
    using_sample_data: bool = False
    database_available: bool = False
    
    def get_results_count(self) -> int:
        """Obtiene el número de resultados filtrados"""
        return len(self.filtered_facturas)
    
    def get_total_count(self) -> int:
        """Obtiene el número total de facturas"""
        return len(self.all_facturas)
    
    def clear_results(self) -> None:
        """Limpia los resultados filtrados"""
        self.filtered_facturas.clear()
    
    def set_filtered_results(self, results: List[Dict[str, Any]]) -> None:
        """Establece los resultados filtrados"""
        self.filtered_facturas = results.copy()


@dataclass
class FacturaData:
    """Modelo para datos de una factura"""
    folio_interno: str
    tipo: Optional[str] = None
    no_vale: Optional[str] = None
    fecha: Optional[str] = None
    folio_xml: Optional[str] = None
    serie: Optional[str] = None
    folio: Optional[str] = None
    nombre_emisor: Optional[str] = None
    rfc_emisor: Optional[str] = None
    conceptos: Optional[str] = None
    total: Optional[float] = None
    subtotal: Optional[float] = None
    iva_trasladado: Optional[float] = None
    ret_iva: Optional[float] = None
    ret_isr: Optional[float] = None
    clase: Optional[str] = None
    cargada: bool = False
    pagada: bool = False
    comentario: Optional[str] = None
    
    @property
    def serie_folio(self) -> str:
        """Obtiene el folio formateado con serie"""
        try:
            from utils.format_utils import format_folio
        except ImportError:
            from buscarapp.utils.format_utils import format_folio
        return format_folio(self.serie, self.folio)
    
    @property
    def cargada_text(self) -> str:
        """Obtiene el texto de estado cargada"""
        return "Sí" if self.cargada else "No"
    
    @property
    def pagada_text(self) -> str:
        """Obtiene el texto de estado pagada"""
        return "Sí" if self.pagada else "No"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte la factura a diccionario para la tabla"""
        return {
            "folio_interno": self.folio_interno,
            "tipo": self.tipo or "",
            "no_vale": self.no_vale or "",
            "fecha": self.fecha or "",
            "folio_xml": self.folio_xml or "",
            "serie_folio": self.serie_folio,
            "serie": self.serie or "",  # AGREGADO: Campo serie para asociación
            "folio": self.folio or "",  # AGREGADO: Campo folio para asociación
            "nombre_emisor": self.nombre_emisor or "",
            "conceptos": self.conceptos or "",
            "total": self.total or 0,
            "clase": self.clase or "",
            "cargada": self.cargada_text,
            "pagada": self.pagada_text,
            "cargada_bool": self.cargada,
            "pagada_bool": self.pagada
        }
