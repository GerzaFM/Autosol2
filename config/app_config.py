"""
Configuración de la aplicación.
"""
from typing import Dict, List


class AppConfig:
    """Configuración centralizada de la aplicación."""
    
    # Opciones para comboboxes
    TIPOS_SOLICITUD: List[str] = ["Compra", "Servicio"]
    DEPARTAMENTOS: List[str] = ["Administracion", "Ventas", "Servicio", "Refacciones", "HyP"]
    
    # Categorías
    CATEGORIAS: List[str] = ["Comer", "Fleet", "Semis", "Refa", "Serv", "HyP", "Admin"]
    
    # Configuración de UI
    WINDOW_SIZE: str = "1024x850"
    THEME: str = "darkly"
    
    # Límites
    MAX_CONCEPTOS_RECOMENDADOS: int = 8
    
    # Anchos de columnas en el TreeView
    COLUMN_WIDTHS: Dict[str, int] = {
        "Cantidad": 80,
        "Descripción": 400,
        "Precio": 80,
        "Total": 80
    }
    
    # Anchos de entrada para popup de conceptos
    POPUP_ENTRY_WIDTHS: Dict[str, int] = {
        "Cantidad": 8,
        "Descripción": 70,
        "Precio": 12,
        "Total": 12
    }
    
    # Mensajes de error
    ERROR_MESSAGES: Dict[str, str] = {
        "campos_obligatorios": "Todos los campos son obligatorios.",
        "numeros_invalidos": "Los campos Cantidad, Precio y Total deben ser números válidos.",
        "no_datos": "No hay datos de solicitud disponibles.",
        "demasiados_conceptos": "La lista de conceptos es demasiado larga.\n¿Prefiere usar un concepto general?",
        "proveedor_incompleto": "Los datos del proveedor están incompletos.",
        "sin_conceptos": "Debe agregar al menos un concepto."
    }
    
    # Valores por defecto
    DEFAULT_VALUES: Dict[str, str] = {
        "departamento": "Administracion",
        "tipo_solicitud": "Compra"
    }

    RUTA_CHEQUE = "FormatosSolicitud/Cheque.pdf"