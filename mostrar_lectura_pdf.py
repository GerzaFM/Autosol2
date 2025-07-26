#!/usr/bin/env python3
"""
Script para mostrar el resultado crudo de la lectura del PDF
"""

import sys
import os
sys.path.append('src')

import pdfplumber
from buscarapp.autocarga.extractor import PDFDataExtractor

def main():
    print("📄 ANÁLISIS CRUDO DE LECTURA DE PDF")
    print("=" * 60)
    
    # Archivos a analizar
    archivos = [
        r"C:\QuiterWeb\cache\15gerzahin.flores_QRSVCMX_V152885_182280_CD.pdf",  # Impresora
        r"C:\QuiterWeb\cache\15gerzahin.flores_QRSVCMX_V153597_183460_CD.pdf"   # Herramientas
    ]
    
    extractor = PDFDataExtractor()
    
    for i, archivo in enumerate(archivos, 1):
        if not os.path.exists(archivo):
            print(f"❌ No se encontró: {os.path.basename(archivo)}")
            continue
            
        print(f"\n📋 ARCHIVO {i}: {os.path.basename(archivo)}")
        print("=" * 80)
        
        try:
            # Método 1: Usando pdfplumber directamente
            print("🔍 MÉTODO 1: Texto extraído con pdfplumber")
            print("-" * 50)
            
            with pdfplumber.open(archivo) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    text = page.extract_text()
                    if text:
                        lines = text.split('\n')
                        print(f"📄 Página {page_num} - {len(lines)} líneas:")
                        for line_num, line in enumerate(lines, 1):
                            print(f"{line_num:2d}: {repr(line)}")  # repr() muestra espacios y caracteres especiales
            
            print("\n" + "="*80)
            
            # Método 2: Usando el extractor de la clase
            print("🔍 MÉTODO 2: Texto extraído con PDFDataExtractor")
            print("-" * 50)
            
            text_extractor = extractor.extract_text_from_pdf(archivo)
            if text_extractor:
                lines_extractor = text_extractor.split('\n')
                print(f"📝 {len(lines_extractor)} líneas extraídas:")
                for line_num, line in enumerate(lines_extractor, 1):
                    print(f"{line_num:2d}: {repr(line)}")
            
            # Método 3: Mostrar datos extraídos campo por campo
            print("\n" + "="*80)
            print("🔍 MÉTODO 3: Datos extraídos campo por campo")
            print("-" * 50)
            
            datos = extractor.extract_all_data(archivo)
            for campo, valor in datos.items():
                print(f"📌 {campo:15}: {repr(valor)}")  # repr() muestra el valor exacto
                
        except Exception as e:
            print(f"❌ Error al procesar {archivo}: {e}")
            import traceback
            traceback.print_exc()
        
        print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    main()
