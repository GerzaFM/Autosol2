"""
Utilidades para la interfaz de usuario y validación de componentes.
"""
import re
import logging
from typing import Tuple, Optional
from app.utils.logger import get_logger

logger = get_logger(__name__)

def validate_geometry_string(geometry: str) -> bool:
    """
    Valida que un string de geometría tenga el formato correcto.
    
    Args:
        geometry: String de geometría (ej: "600x280", "1200x900+100+50")
        
    Returns:
        True si el formato es válido, False en caso contrario
    """
    # Patrón para validar geometría: WIDTHxHEIGHT[+X+Y] o WIDTHxHEIGHT[-X-Y]
    pattern = r'^\d+x\d+([+-]\d+[+-]\d+)?$'
    
    if not isinstance(geometry, str):
        logger.warning(f"Geometría no es string: {type(geometry)}")
        return False
    
    if not re.match(pattern, geometry):
        logger.warning(f"Geometría inválida: '{geometry}'")
        return False
    
    return True

def parse_geometry_string(geometry: str) -> Optional[Tuple[int, int, Optional[int], Optional[int]]]:
    """
    Parsea un string de geometría y extrae sus componentes.
    
    Args:
        geometry: String de geometría
        
    Returns:
        Tupla (width, height, x, y) o None si el formato es inválido
    """
    if not validate_geometry_string(geometry):
        return None
    
    try:
        # Separar dimensiones y posición
        if '+' in geometry or '-' in geometry:
            # Tiene posición
            size_part = geometry.split('+')[0].split('-')[0]
            pos_part = geometry[len(size_part):]
            
            # Parsear dimensiones
            width, height = map(int, size_part.split('x'))
            
            # Parsear posición (más complejo por los signos)
            x_match = re.search(r'([+-]\d+)', pos_part)
            y_match = re.search(r'([+-]\d+)', pos_part[x_match.end():])
            
            x = int(x_match.group(1)) if x_match else None
            y = int(y_match.group(1)) if y_match else None
            
        else:
            # Solo dimensiones
            width, height = map(int, geometry.split('x'))
            x, y = None, None
        
        return (width, height, x, y)
        
    except (ValueError, AttributeError) as e:
        logger.error(f"Error al parsear geometría '{geometry}': {e}")
        return None

def safe_set_geometry(widget, geometry: str, fallback: str = "400x300") -> bool:
    """
    Establece la geometría de un widget de forma segura.
    
    Args:
        widget: Widget de tkinter/ttkbootstrap
        geometry: String de geometría deseada
        fallback: Geometría de respaldo si la principal falla
        
    Returns:
        True si se estableció correctamente, False si se usó el fallback
    """
    try:
        if validate_geometry_string(geometry):
            widget.geometry(geometry)
            logger.debug(f"Geometría establecida: {geometry}")
            return True
        else:
            logger.warning(f"Geometría inválida '{geometry}', usando fallback '{fallback}'")
            widget.geometry(fallback)
            return False
            
    except Exception as e:
        logger.error(f"Error al establecer geometría: {e}")
        try:
            widget.geometry(fallback)
            logger.info(f"Usando geometría de fallback: {fallback}")
        except Exception as fallback_error:
            logger.error(f"Error incluso con geometría de fallback: {fallback_error}")
        return False

def center_window_on_parent(child_widget, parent_widget, offset_x: int = 0, offset_y: int = 0):
    """
    Centra una ventana hijo sobre su ventana padre.
    
    Args:
        child_widget: Ventana hijo (popup, dialog, etc.)
        parent_widget: Ventana padre
        offset_x: Desplazamiento horizontal adicional
        offset_y: Desplazamiento vertical adicional
    """
    try:
        # Actualizar para obtener dimensiones correctas
        child_widget.update_idletasks()
        parent_widget.update_idletasks()
        
        # Obtener dimensiones de ambas ventanas
        child_width = child_widget.winfo_reqwidth()
        child_height = child_widget.winfo_reqheight()
        
        parent_x = parent_widget.winfo_rootx()
        parent_y = parent_widget.winfo_rooty()
        parent_width = parent_widget.winfo_width()
        parent_height = parent_widget.winfo_height()
        
        # Calcular posición centrada
        center_x = parent_x + (parent_width // 2) - (child_width // 2) + offset_x
        center_y = parent_y + (parent_height // 2) - (child_height // 2) + offset_y
        
        # Establecer posición
        position_geometry = f"+{center_x}+{center_y}"
        child_widget.geometry(position_geometry)
        
        logger.debug(f"Ventana centrada en posición: {position_geometry}")
        
    except Exception as e:
        logger.error(f"Error al centrar ventana: {e}")

def get_safe_window_size(size_key: str) -> str:
    """
    Obtiene un tamaño de ventana seguro desde la configuración.
    
    Args:
        size_key: Clave del tamaño en WINDOW_SIZES
        
    Returns:
        String de geometría válido
    """
    from config.settings import WINDOW_SIZES
    
    try:
        geometry = WINDOW_SIZES.get(size_key, "400x300")
        if validate_geometry_string(geometry):
            return geometry
        else:
            logger.warning(f"Geometría inválida en configuración para '{size_key}': {geometry}")
            return "400x300"
    except Exception as e:
        logger.error(f"Error al obtener tamaño de ventana para '{size_key}': {e}")
        return "400x300"
