#!/usr/bin/env python3
"""
Script de prueba para verificar la extracción del campo Descripción
"""

import sys
import os
from pathlib import Path

# Agregar el directorio src al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from buscarapp.autocarga.extractor import PDFDataExtractor

def test_descripcion_extraction():
    """
    Prueba la extracción del campo descripción de un PDF de vale.
    """
    print("🧪 PRUEBA DE EXTRACCIÓN DE DESCRIPCIÓN")
    print("=" * 50)
    
    # Inicializar extractor
    extractor = PDFDataExtractor()
    
    # Buscar archivos PDF de vales en la carpeta de pruebas
    carpeta_pruebas = Path("Pruebas")
    
    if not carpeta_pruebas.exists():
        print("❌ No se encontró la carpeta 'Pruebas'")
        return
    
    # Buscar archivos que contengan "SERVICIO" (que son vales)
    archivos_vales = list(carpeta_pruebas.glob("*SERVICIO*.pdf"))
    
    if not archivos_vales:
        print("❌ No se encontraron archivos de vales en la carpeta Pruebas")
        return
    
    print(f"📁 Archivos encontrados: {len(archivos_vales)}")
    print("-" * 50)
    
    for archivo in archivos_vales[:2]:  # Probar solo los primeros 2
        print(f"\n📄 Procesando: {archivo.name}")
        print("-" * 30)
        
        try:
            # Extraer todos los datos incluyendo descripción
            datos = extractor.extract_all_data(str(archivo))
            
            if datos:
                print("✅ Datos extraídos:")
                for campo, valor in datos.items():
                    if valor:
                        print(f"   {campo}: {valor}")
                    else:
                        print(f"   {campo}: (No encontrado)")
                
                # Destacar la descripción
                descripcion = datos.get('Descripcion', '')
                if descripcion:
                    print(f"\n🎯 DESCRIPCIÓN ENCONTRADA:")
                    print(f"   📝 {descripcion}")
                else:
                    print("\n⚠️  DESCRIPCIÓN NO ENCONTRADA")
                    
                    # Mostrar texto bruto para depuración
                    print("\n🔍 TEXTO BRUTO PARA DEPURACIÓN:")
                    texto = extractor.extract_text_from_pdf(str(archivo))
                    lines = texto.split('\n')
                    for i, line in enumerate(lines):
                        if 'descripci' in line.lower():
                            print(f"   Línea {i}: {line}")
                            if i + 1 < len(lines):
                                print(f"   Línea {i+1}: {lines[i+1]}")
            else:
                print("❌ No se pudieron extraer datos")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 PRUEBA COMPLETADA")

if __name__ == "__main__":
    test_descripcion_extraction()
