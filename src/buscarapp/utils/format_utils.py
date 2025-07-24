"""
Utilidades para formateo de datos
"""
from typing import Optional


def format_folio(serie: Optional[str], folio: Optional[str]) -> str:
    """
    Formatea el folio con serie y número, usando espacio como separador.
    
    Args:
        serie: Serie de la factura (puede ser None o vacía)
        folio: Folio de la factura (puede ser None o vacía)
        
    Returns:
        str: Folio formateado
    """
    if serie and serie.strip():
        return f"{serie.strip()} {folio or ''}".strip()
    else:
        return folio or ""


def format_currency(amount: float) -> str:
    """
    Formatea un número como moneda.
    
    Args:
        amount: Cantidad a formatear
        
    Returns:
        str: Cantidad formateada como ${amount:,.2f}
    """
    if amount is None:
        return "$0.00"
    return f"${amount:,.2f}"


def format_comentario_factura(serie: Optional[str], folio: Optional[str]) -> str:
    """
    Construye el comentario de la factura con serie y folio.
    
    Args:
        serie: Serie de la factura
        folio: Folio de la factura
        
    Returns:
        str: Comentario formateado como "Factura: SERIE FOLIO"
    """
    serie_str = serie or ""
    folio_str = folio or ""
    
    # Construir el comentario evitando espacios dobles
    if serie_str and folio_str:
        return f"Factura: {serie_str} {folio_str}"
    elif serie_str:
        return f"Factura: {serie_str}"
    elif folio_str:
        return f"Factura: {folio_str}"
    else:
        return "Factura:"


def format_tipo_vale(tipo: str) -> str:
    """
    Formatea el tipo de vale al formato "CLAVE - DESCRIPCIÓN".
    
    Args:
        tipo: Código del tipo de vale
        
    Returns:
        str: Tipo formateado con descripción
    """
    if not tipo:
        return ""
        
    try:
        from solicitudapp.config.app_config import AppConfig
        if hasattr(AppConfig, 'TIPO_VALE') and tipo in AppConfig.TIPO_VALE:
            return f"{tipo} - {AppConfig.TIPO_VALE[tipo]}"
        else:
            return tipo
    except ImportError:
        return tipo
