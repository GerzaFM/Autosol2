"""
Modelos para la tabla de facturas
"""
from typing import Dict, List, Any, Tuple


class TableModel:
    """Modelo para manejar los datos de la tabla de facturas"""
    
    # Configuración de columnas
    COLUMNS = (
        "folio_interno", "tipo", "no_vale", "fecha", "folio_xml", 
        "nombre_emisor", "conceptos", "total", "clase", "cargada", "pagada"
    )
    
    COLUMN_WIDTHS = {
        "folio_interno": 80, 
        "tipo": 60,
        "no_vale": 80,
        "fecha": 100,
        "folio_xml": 100,
        "nombre_emisor": 160, 
        "conceptos": 300, 
        "total": 100,
        "clase": 120,
        "cargada": 80,
        "pagada": 80
    }
    
    COLUMN_NAMES = {
        "folio_interno": "ID",
        "tipo": "Tipo",
        "no_vale": "No Vale",
        "fecha": "Fecha",
        "folio_xml": "Folio",
        "nombre_emisor": "Emisor",
        "conceptos": "Conceptos",
        "total": "Total",
        "clase": "Clase",
        "cargada": "Cargada",
        "pagada": "Pagada"
    }
    
    def __init__(self):
        self.data: List[Dict[str, Any]] = []
    
    def set_data(self, facturas: List[Dict[str, Any]]) -> None:
        """Establece los datos de la tabla"""
        self.data = facturas.copy()
    
    def get_data(self) -> List[Dict[str, Any]]:
        """Obtiene los datos de la tabla"""
        return self.data
    
    def get_row_data(self, index: int) -> Dict[str, Any]:
        """Obtiene los datos de una fila específica"""
        if 0 <= index < len(self.data):
            return self.data[index]
        return {}
    
    def find_by_folio_interno(self, folio_interno: str) -> Dict[str, Any]:
        """Busca una factura por su folio interno"""
        for factura in self.data:
            if str(factura.get("folio_interno")) == str(folio_interno):
                return factura
        return {}
    
    def get_table_values(self, factura: Dict[str, Any]) -> Tuple:
        """Convierte una factura a tupla de valores para la tabla"""
        return (
            factura.get("folio_interno", ""),
            factura.get("tipo", ""),
            factura.get("no_vale", ""),
            factura.get("fecha", ""),
            factura.get("folio_xml", ""),
            factura.get("nombre_emisor", ""),
            factura.get("conceptos", ""),
            factura.get("total", ""),
            factura.get("clase", ""),
            factura.get("cargada", ""),
            factura.get("pagada", "")
        )
    
    def get_all_table_values(self) -> List[Tuple]:
        """Obtiene todos los valores para la tabla"""
        return [self.get_table_values(factura) for factura in self.data]
    
    def update_factura_status(self, folio_interno: str, field: str, value: Any) -> bool:
        """
        Actualiza el estado de una factura
        
        Args:
            folio_interno: ID de la factura
            field: Campo a actualizar
            value: Nuevo valor
            
        Returns:
            bool: True si se actualizó correctamente
        """
        for factura in self.data:
            if str(factura.get("folio_interno")) == str(folio_interno):
                factura[field] = value
                if field in ["cargada_bool", "pagada_bool"]:
                    # También actualizar la versión de texto
                    text_field = field.replace("_bool", "")
                    factura[text_field] = "Sí" if value else "No"
                return True
        return False
    
    def clear(self) -> None:
        """Limpia todos los datos"""
        self.data.clear()
    
    def count(self) -> int:
        """Obtiene el número de facturas"""
        return len(self.data)
