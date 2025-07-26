#!/usr/bin/env python3
"""
Analizar el texto crudo del nuevo vale para ajustar patrones
"""

import sys
import os
sys.path.append('src')

import pdfplumber
import PyPDF2

def main():
    print("🔍 ANÁLISIS CRUDO - NUEVO VALE SERVICIOS GLOBALES ELYT")
    print("=" * 70)
    
    archivo = r"C:\QuiterWeb\cache\15gerzahin.flores_QRSVCMX_V152266_180646_CD.pdf"
    
    if not os.path.exists(archivo):
        print(f"❌ No se encontró el archivo: {archivo}")
        return
    
    # Método 1: pdfplumber
    print("🔧 MÉTODO 1: pdfplumber")
    print("-" * 50)
    try:
        with pdfplumber.open(archivo) as pdf:
            page = pdf.pages[0]
            text = page.extract_text()
            lines = text.split('\n')
            
            for i, line in enumerate(lines, 1):
                print(f"{i:2d}: {repr(line)}")
                
    except Exception as e:
        print(f"Error con pdfplumber: {e}")
    
    # Método 2: PyPDF2
    print(f"\n🔧 MÉTODO 2: PyPDF2")
    print("-" * 50)
    try:
        with open(archivo, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            page = pdf_reader.pages[0]
            text = page.extract_text()
            lines = text.split('\n')
            
            for i, line in enumerate(lines, 1):
                print(f"{i:2d}: {repr(line)}")
                
    except Exception as e:
        print(f"Error con PyPDF2: {e}")

if __name__ == "__main__":
    main()
