#!/usr/bin/env python3
"""
Test completo del sistema de extracción de datos de PDFs.
Prueba múltiples documentos para verificar compatibilidad.
"""

import sys
import os

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.buscarapp.autocarga.extractor import PDFDataExtractor

def main():
    print("🧪 TEST COMPLETO - SISTEMA DE EXTRACCIÓN DE PDF")
    print("=" * 60)
    
    extractor = PDFDataExtractor()
    
    # Lista de documentos de prueba (solo vales reales - QRSVCMX)
    test_files = [
        "C:/QuiterWeb/cache/15gerzahin.flores_QRSVCMX_V152266_180646_CD.pdf",
        "C:/QuiterWeb/cache/15gerzahin.flores_QRSVCMX_V142538_171732_CD.pdf",
        "C:/QuiterWeb/cache/15gerzahin.flores_QRSVCMX_V143873_171730_CD.pdf",
        "C:/QuiterWeb/cache/15gerzahin.flores_QRSVCMX_V143879_171728_CD.pdf"
    ]
    
    successful_extractions = 0
    total_files = 0
    
    for pdf_file in test_files:
        if os.path.exists(pdf_file):
            total_files += 1
            print(f"\n📄 Procesando: {pdf_file}")
            print("-" * 50)
            
            try:
                data = extractor.extract_all_data(pdf_file, debug=False)
                
                # Verificar campos principales
                campos_principales = ['Numero', 'Nombre', 'Total', 'Descripcion', 'Referencia']
                campos_encontrados = 0
                
                for campo in campos_principales:
                    if data.get(campo):
                        campos_encontrados += 1
                        print(f"✅ {campo:12}: {data[campo]}")
                    else:
                        print(f"❌ {campo:12}: [No encontrado]")
                
                if campos_encontrados >= 3:  # Al menos 3 campos principales
                    successful_extractions += 1
                    print(f"✅ Extracción exitosa ({campos_encontrados}/{len(campos_principales)} campos)")
                else:
                    print(f"⚠️  Extracción parcial ({campos_encontrados}/{len(campos_principales)} campos)")
                    
            except Exception as e:
                print(f"❌ Error: {e}")
        else:
            print(f"⚠️  Archivo no encontrado: {pdf_file}")
    
    print("\n" + "=" * 60)
    print(f"📊 RESUMEN DE PRUEBAS")
    print(f"Archivos procesados: {total_files}")
    print(f"Extracciones exitosas: {successful_extractions}")
    print(f"Tasa de éxito: {(successful_extractions/total_files*100) if total_files > 0 else 0:.1f}%")
    print("=" * 60)
    
    if successful_extractions == total_files and total_files > 0:
        print("🎉 ¡TODAS LAS PRUEBAS PASARON EXITOSAMENTE!")
        return True
    else:
        print("⚠️  Algunas pruebas fallaron o no se encontraron archivos.")
        return False

if __name__ == "__main__":
    main()
