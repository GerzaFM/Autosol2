#!/usr/bin/env python3
"""
Análisis detallado de un vale específico para mostrar el mapeo de datos.
"""

import sys
import os

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.buscarapp.autocarga.extractor import PDFDataExtractor

def analizar_vale_detallado():
    print("🔍 ANÁLISIS DETALLADO DE VALE")
    print("=" * 60)
    
    # Vale específico para analizar
    vale_path = "C:/QuiterWeb/cache/15gerzahin.flores_QRSVCMX_V152266_180646_CD.pdf"
    
    print(f"📄 Analizando: {os.path.basename(vale_path)}")
    print("-" * 60)
    
    extractor = PDFDataExtractor()
    
    # Extraer datos con debug activado
    data = extractor.extract_all_data(vale_path, debug=True)
    
    print("\n" + "=" * 60)
    print("🏷️  MAPEO DE DATOS EXTRAÍDOS")
    print("=" * 60)
    
    # Mostrar cada campo extraído con su nombre interno y valor
    for campo_interno, valor in data.items():
        print(f"📋 Campo: '{campo_interno}'")
        print(f"   📝 Valor: {valor if valor else '[No encontrado]'}")
        print(f"   🔗 Mapeo BD: {mapeo_a_bd(campo_interno)}")
        print()
    
    return data

def mapeo_a_bd(campo_extractor):
    """
    Mapea los nombres del extractor a los campos de la base de datos.
    """
    mapeo = {
        'Numero': 'noVale (PRIMARY KEY)',
        'Nombre': 'proveedor',
        'Total': 'total', 
        'Descripcion': 'descripcion',
        'Referencia': 'referencia',
        'Fecha': 'fechaVale',
        'Departamento': 'departameto',  # Nota: tiene typo en BD
        'Sucursal': 'sucursal',
        'Marca': 'marca',
        'Responsable': 'responsable',
        'Tipo De Vale': 'tipo',
        'No Documento': 'noDocumento'
    }
    
    return mapeo.get(campo_extractor, f"⚠️  Campo no mapeado: {campo_extractor}")

if __name__ == "__main__":
    analizar_vale_detallado()
