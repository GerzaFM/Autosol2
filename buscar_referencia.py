#!/usr/bin/env python3
"""
Buscar el campo Referencia en el PDF de la impresora
"""

import sys
import os
import re
sys.path.append('src')

import pdfplumber

def main():
    print("🔍 BÚSQUEDA DE REFERENCIA: 8158095")
    print("=" * 50)
    
    archivo = r"C:\QuiterWeb\cache\15gerzahin.flores_QRSVCMX_V152885_182280_CD.pdf"
    
    if not os.path.exists(archivo):
        print(f"❌ No se encontró el archivo: {archivo}")
        return
    
    try:
        with pdfplumber.open(archivo) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                text = page.extract_text()
                if not text:
                    continue
                    
                lines = text.split('\n')
                
                print(f"📄 Página {page_num}:")
                print("📝 TEXTO COMPLETO:")
                print("=" * 60)
                for i, line in enumerate(lines, 1):
                    print(f"{i:2d}: {line}")
                
                print("\n🔍 BÚSQUEDA ESPECÍFICA DE '8158095':")
                print("-" * 50)
                
                # Buscar líneas que contengan el número
                for i, line in enumerate(lines, 1):
                    if '8158095' in line:
                        print(f"✅ ENCONTRADO en línea {i}: {line}")
                        
                        # Mostrar contexto
                        start = max(0, i-3)
                        end = min(len(lines), i+3)
                        print("   📋 Contexto:")
                        for j in range(start, end):
                            marker = '>>> ' if j == i-1 else '    '
                            print(f"{marker}{j+1:2d}: {lines[j]}")
                        print()
                
                # Buscar también palabras relacionadas
                print("🔍 BÚSQUEDA DE PALABRAS CLAVE:")
                print("-" * 40)
                palabras_clave = ['Referencia', 'referencia', 'Ref:', 'REF:', 'Número', 'V152885']
                
                for palabra in palabras_clave:
                    for i, line in enumerate(lines, 1):
                        if palabra in line:
                            print(f"📌 '{palabra}' en línea {i}: {line}")
                
    except Exception as e:
        print(f"❌ Error al procesar el PDF: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
