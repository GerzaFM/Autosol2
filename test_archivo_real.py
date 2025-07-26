#!/usr/bin/env python3
"""
Script de prueba con archivo real de vale QRSVCMX
"""

import sys
import os
from pathlib import Path

# Agregar el directorio src al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from buscarapp.autocarga.extractor import PDFDataExtractor

def test_archivo_real():
    """
    Prueba la extracción con el archivo real de vale.
    """
    print("🧪 PRUEBA CON ARCHIVO REAL DE VALE")
    print("=" * 60)
    
    # Archivo real de vale
    archivo_vale = r"C:\QuiterWeb\cache\15gerzahin.flores_QRSVCMX_V153597_183460_CD.pdf"
    
    if not Path(archivo_vale).exists():
        print(f"❌ Archivo no encontrado: {archivo_vale}")
        return
    
    print(f"📄 Procesando: {Path(archivo_vale).name}")
    print("-" * 60)
    
    # Inicializar extractor
    extractor = PDFDataExtractor()
    
    try:
        # Extraer todos los datos incluyendo descripción
        datos = extractor.extract_all_data(archivo_vale)
        
        if datos:
            print("✅ Datos extraídos:")
            for campo, valor in datos.items():
                if valor:
                    print(f"   ✅ {campo}: {valor}")
                else:
                    print(f"   ❌ {campo}: (No encontrado)")
            
            # Destacar la descripción
            descripcion = datos.get('Descripcion', '')
            if descripcion:
                print(f"\n🎯 DESCRIPCIÓN ENCONTRADA:")
                print(f"   📝 {descripcion}")
            else:
                print("\n⚠️  DESCRIPCIÓN NO ENCONTRADA")
                
                # Mostrar texto bruto para depuración
                print("\n🔍 TEXTO BRUTO PARA DEPURACIÓN:")
                texto = extractor.extract_text_from_pdf(archivo_vale)
                lines = texto.split('\n')
                for i, line in enumerate(lines):
                    if 'descripci' in line.lower() or 'concepto' in line.lower():
                        print(f"   Línea {i}: {line}")
                        if i + 1 < len(lines):
                            print(f"   Línea {i+1}: {lines[i+1]}")
        else:
            print("❌ No se pudieron extraer datos")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("🏁 PRUEBA COMPLETADA")

if __name__ == "__main__":
    test_archivo_real()
