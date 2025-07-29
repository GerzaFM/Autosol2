#!/usr/bin/env python3
"""
Script de prueba para verificar la corrección del código del proveedor
"""
import sys
import os

# Agregar src al path
src_path = os.path.join(os.path.dirname(__file__), 'src')
sys.path.insert(0, src_path)

from buscarapp.autocarga.extractor import PDFDataExtractor
from buscarapp.utils.procesar_datos_vale import procesar_datos_vale

def test_codigo_proveedor():
    """Prueba que el código del proveedor se extraiga correctamente desde el campo cuenta"""
    
    pdf_path = r'C:\QuiterWeb\cache\15gerzahin.flores_QRSVCMX_V153924_184455_CD.pdf'
    
    if not os.path.exists(pdf_path):
        print(f"❌ No se encontró el archivo: {pdf_path}")
        return
    
    print("🔍 PROBANDO CORRECCIÓN DEL CÓDIGO DEL PROVEEDOR")
    print("="*60)
    print(f"📁 Archivo: {pdf_path}")
    print()
    
    extractor = PDFDataExtractor()
    
    # Extraer datos con el extractor
    print("📋 PASO 1: Extrayendo datos del PDF...")
    datos_extraidos = extractor.extract_all_data(pdf_path)
    
    print("📊 DATOS EXTRAÍDOS:")
    for key, value in datos_extraidos.items():
        print(f"   {key:15}: {value}")
    print()
    
    # Procesar datos con la nueva lógica
    print("🔧 PASO 2: Procesando datos con nueva lógica...")
    datos_procesados = procesar_datos_vale(datos_extraidos)
    
    print("📊 DATOS PROCESADOS:")
    for key, value in datos_procesados.items():
        print(f"   {key:15}: {value}")
    print()
    
    # Verificar la corrección específica
    print("🎯 VERIFICACIÓN ESPECÍFICA:")
    print("-" * 40)
    
    cuenta_extraida = datos_extraidos.get('Cuenta')
    codigo_procesado = datos_procesados.get('codigo')
    
    print(f"✅ Campo 'Cuenta' extraído del PDF: {cuenta_extraida}")
    print(f"✅ Campo 'codigo' procesado para BD: {codigo_procesado}")
    
    if cuenta_extraida == codigo_procesado:
        print("✅ ¡CORRECCIÓN EXITOSA! El código del proveedor ahora viene del campo cuenta")
    else:
        print("❌ La corrección no funcionó correctamente")
    
    print()
    print("📋 RESUMEN:")
    print(f"   Proveedor: {datos_procesados.get('proveedor')}")
    print(f"   Código para actualizar: {datos_procesados.get('codigo')}")
    print(f"   Cuenta para BD: {datos_procesados.get('cuenta')}")

if __name__ == "__main__":
    test_codigo_proveedor()
