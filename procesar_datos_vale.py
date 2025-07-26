#!/usr/bin/env python3
"""
Función para procesar y limpiar datos extraídos del PDF antes de guardar en BD.
"""

import re
from datetime import datetime
from typing import Dict, Optional, Any

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
    datos_procesados['tipo'] = datos_extraidos.get('Tipo De Vale', '')
    datos_procesados['noDocumento'] = datos_extraidos.get('No Documento', '')
    datos_procesados['descripcion'] = datos_extraidos.get('Descripcion', '')
    datos_procesados['total'] = datos_extraidos.get('Total', '')
    datos_procesados['proveedor'] = datos_extraidos.get('Nombre', '')
    
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

def mostrar_procesamiento_ejemplo():
    """
    Muestra un ejemplo de cómo se procesan los datos.
    """
    # Datos de ejemplo como los extrae el PDFDataExtractor
    datos_raw = {
        'Numero': 'V152266',
        'Nombre': 'SERVICIOS GLOBALES ELYT SADECV',
        'Total': '12,837.49',
        'Descripcion': 'MARKETING DE EXPERIENCIA (INCLUYE EMBAJADORES DE EXPERIENCIA MAS AMENIDADES) DE ACUERDO A CONTRATO C-23',
        'Referencia': '8122661',
        'Fecha': '18/07/2025',
        'Cuenta': '3221',
        'Departamento': '6 ADMINISTRACION',
        'Sucursal': '15 NISSAN MATEHUALA',
        'Marca': '2 - NISSAN',
        'Responsable': '294379',
        'Tipo De Vale': 'VCV',
        'No Documento': '10455'
    }
    
    print("🔄 PROCESAMIENTO DE DATOS PARA BD")
    print("=" * 60)
    
    datos_procesados = procesar_datos_vale(datos_raw)
    
    print("📥 DATOS ORIGINALES (del extractor):")
    for key, value in datos_raw.items():
        print(f"   {key:15}: {value}")
    
    print("\n📤 DATOS PROCESADOS (para BD):")
    for key, value in datos_procesados.items():
        tipo = type(value).__name__
        print(f"   {key:15}: {value} ({tipo})")
    
    return datos_procesados

if __name__ == "__main__":
    mostrar_procesamiento_ejemplo()
