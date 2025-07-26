#!/usr/bin/env python3
"""
Script enfocado en PyPDF2 para extraer texto con espacios preservados
"""

import sys
import os
sys.path.append('src')

import PyPDF2

def main():
    print("🔍 ANÁLISIS DETALLADO CON PyPDF2")
    print("=" * 60)
    
    archivos = [
        r"C:\QuiterWeb\cache\15gerzahin.flores_QRSVCMX_V152885_182280_CD.pdf",  # Impresora
        r"C:\QuiterWeb\cache\15gerzahin.flores_QRSVCMX_V153597_183460_CD.pdf"   # Herramientas
    ]
    
    for archivo in archivos:
        if not os.path.exists(archivo):
            print(f"❌ No se encontró: {os.path.basename(archivo)}")
            continue
            
        print(f"\n📄 Archivo: {os.path.basename(archivo)}")
        print("-" * 60)
        
        try:
            with open(archivo, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                page = pdf_reader.pages[0]
                text = page.extract_text()
                
                # Dividir en líneas
                lines = text.split('\n')
                
                print(f"📝 {len(lines)} líneas extraídas:")
                print()
                
                # Buscar líneas relevantes
                for i, line in enumerate(lines, 1):
                    # Buscar nombres de proveedores
                    if any(keyword in line.upper() for keyword in ['NOMBRE:', 'CYBERPUERTA', 'ELIAMARIA', 'PROVEEDOR:']):
                        print(f"Línea {i:2d}: {repr(line)}")
                    
                    # Buscar descripciones
                    if any(keyword in line.upper() for keyword in ['DESCRIPCIÓN:', 'IMPRESORA', 'HERRAMIENTAS']):
                        print(f"Línea {i:2d}: {repr(line)}")
                    
                    # Buscar referencias
                    if 'Referencia:' in line or any(ref in line for ref in ['8158095', '8194826']):
                        print(f"Línea {i:2d}: {repr(line)}")
                        
        except Exception as e:
            print(f"❌ Error al procesar {archivo}: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main()
