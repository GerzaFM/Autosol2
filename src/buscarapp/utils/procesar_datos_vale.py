#!/usr/bin/env python3
"""
Función para procesar y limpiar datos extraídos del PDF antes de guardar en BD.
"""

import re
from datetime import datetime
from typing import Dict, Optional, Any

def corregir_tipo_vale(tipo_extraido: str) -> str:
    """
    Corrige el tipo de vale extraído del PDF para que coincida con TIPO_VALE.
    
    Args:
        tipo_extraido: Tipo de vale tal como se extrae del PDF
        
    Returns:
        Código correcto según TIPO_VALE o el valor original si no hay mapeo
    """
    # Mapeo de tipos extraídos incorrectamente a códigos correctos
    mapeo_tipos = {
        'VCV': 'VC',  # Vale de Control mal extraído
        'GUG': 'GU',  # Gasolina mal extraída
        # Agregar más mapeos según se vayan encontrando
    }
    
    # Normalizar el tipo extraído (quitar espacios y convertir a mayúsculas)
    tipo_normalizado = tipo_extraido.strip().upper()
    
    # Verificar si existe un mapeo para este tipo
    if tipo_normalizado in mapeo_tipos:
        return mapeo_tipos[tipo_normalizado]
    
    # Si no hay mapeo, retornar el tipo original
    return tipo_normalizado

def procesar_datos_vale(datos_extraidos: Dict[str, str]) -> Dict[str, Any]:
    """
    Procesa los datos extraídos del PDF y los convierte al formato correcto para la BD.
    
    Args:
        datos_extraidos: Diccionario con los datos tal como los extrae el PDFDataExtractor
        
    Returns:
        Diccionario con los datos procesados y listos para insertar en BD
    """
    
    datos_procesados = {}
    
    # Procesar cada campo según el tipo requerido en BD
    
    # Campo texto - sin cambios
    datos_procesados['noVale'] = datos_extraidos.get('Numero', '')
    datos_procesados['tipo'] = corregir_tipo_vale(datos_extraidos.get('Tipo De Vale', ''))
    datos_procesados['noDocumento'] = datos_extraidos.get('No Documento', '')
    datos_procesados['descripcion'] = datos_extraidos.get('Descripcion', '')
    datos_procesados['total'] = datos_extraidos.get('Total', '')
    datos_procesados['proveedor'] = datos_extraidos.get('Nombre', '')
    
    # IMPORTANTE: El código del proveedor viene en el campo "cuenta" del PDF
    # Usamos el valor de cuenta como código del proveedor para actualizar BD
    codigo_proveedor = datos_extraidos.get('Cuenta', '')
    datos_procesados['codigo'] = codigo_proveedor if codigo_proveedor else datos_extraidos.get('Codigo', '')
    
    # Campo entero - extraer solo números
    datos_procesados['referencia'] = extraer_numero_entero(datos_extraidos.get('Referencia', ''))
    datos_procesados['cuenta'] = extraer_numero_entero(datos_extraidos.get('Cuenta', ''))
    datos_procesados['departamento'] = extraer_numero_entero(datos_extraidos.get('Departamento', ''))
    datos_procesados['sucursal'] = extraer_numero_entero(datos_extraidos.get('Sucursal', ''))
    datos_procesados['marca'] = extraer_numero_entero(datos_extraidos.get('Marca', ''))
    datos_procesados['responsable'] = extraer_numero_entero(datos_extraidos.get('Responsable', ''))
    
    # Campo fecha - convertir string a date
    datos_procesados['fechaVale'] = procesar_fecha(datos_extraidos.get('Fecha', ''))
    
    return datos_procesados

def extraer_numero_entero(texto: str) -> Optional[int]:
    """
    Extrae solo el número entero de un texto.
    
    Ejemplos:
    - "6 ADMINISTRACION" -> 6
    - "15 NISSAN MATEHUALA" -> 15
    - "2 - NISSAN" -> 2
    - "294379" -> 294379
    """
    if not texto:
        return None
    
    # Buscar el primer número en el texto
    match = re.search(r'\d+', str(texto))
    if match:
        return int(match.group())
    
    return None

def procesar_fecha(texto_fecha: str) -> Optional[datetime.date]:
    """
    Convierte una fecha en formato string a objeto date.
    
    Ejemplos:
    - "18/07/2025" -> date(2025, 7, 18)
    """
    if not texto_fecha:
        return None
    
    try:
        # Formato esperado: DD/MM/YYYY
        if '/' in texto_fecha:
            partes = texto_fecha.split('/')
            if len(partes) == 3:
                dia, mes, año = partes
                return datetime(int(año), int(mes), int(dia)).date()
    except (ValueError, IndexError):
        pass
    
    return None
