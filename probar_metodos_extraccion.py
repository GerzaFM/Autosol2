#!/usr/bin/env python3
"""
Script para probar diferentes métodos de extracción de texto del PDF
para preservar espacios originales
"""

import sys
import os
sys.path.append('src')

import pdfplumber
import PyPDF2
from io import StringIO

def main():
    print("🔍 PRUEBA DE DIFERENTES MÉTODOS DE EXTRACCIÓN")
    print("=" * 70)
    
    archivo = r"C:\QuiterWeb\cache\15gerzahin.flores_QRSVCMX_V152885_182280_CD.pdf"
    
    if not os.path.exists(archivo):
        print(f"❌ No se encontró: {archivo}")
        return
    
    print(f"📄 Analizando: {os.path.basename(archivo)}")
    print("=" * 70)
    
    # MÉTODO 1: pdfplumber con configuración básica
    print("🔧 MÉTODO 1: pdfplumber básico")
    print("-" * 50)
    try:
        with pdfplumber.open(archivo) as pdf:
            page = pdf.pages[0]
            text1 = page.extract_text()
            lines1 = text1.split('\n')
            
            # Mostrar solo las líneas relevantes
            for i, line in enumerate(lines1, 1):
                if 'Nombre:' in line or 'CYBERPUERTAS' in line or 'ELIAMARIA' in line:
                    print(f"Línea {i:2d}: {repr(line)}")
    except Exception as e:
        print(f"Error: {e}")
    
    # MÉTODO 2: pdfplumber con diferentes parámetros
    print("\n🔧 MÉTODO 2: pdfplumber con layout preservado")
    print("-" * 50)
    try:
        with pdfplumber.open(archivo) as pdf:
            page = pdf.pages[0]
            # Preservar más el layout original
            text2 = page.extract_text(layout=True)
            lines2 = text2.split('\n')
            
            for i, line in enumerate(lines2, 1):
                if 'Nombre:' in line or 'CYBERPUERTAS' in line or 'ELIAMARIA' in line:
                    print(f"Línea {i:2d}: {repr(line)}")
    except Exception as e:
        print(f"Error: {e}")
    
    # MÉTODO 3: pdfplumber con x_tolerance más alto
    print("\n🔧 MÉTODO 3: pdfplumber con x_tolerance ajustado")
    print("-" * 50)
    try:
        with pdfplumber.open(archivo) as pdf:
            page = pdf.pages[0]
            # Ajustar tolerancia para espacios
            text3 = page.extract_text(x_tolerance=3, y_tolerance=3)
            lines3 = text3.split('\n')
            
            for i, line in enumerate(lines3, 1):
                if 'Nombre:' in line or 'CYBERPUERTAS' in line or 'ELIAMARIA' in line:
                    print(f"Línea {i:2d}: {repr(line)}")
    except Exception as e:
        print(f"Error: {e}")
    
    # MÉTODO 4: PyPDF2
    print("\n🔧 MÉTODO 4: PyPDF2")
    print("-" * 50)
    try:
        with open(archivo, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            page = pdf_reader.pages[0]
            text4 = page.extract_text()
            lines4 = text4.split('\n')
            
            for i, line in enumerate(lines4, 1):
                if 'Nombre:' in line or 'CYBERPUERTAS' in line or 'ELIAMARIA' in line:
                    print(f"Línea {i:2d}: {repr(line)}")
    except Exception as e:
        print(f"Error: {e}")
    
    # MÉTODO 5: pdfplumber analizando caracteres individuales
    print("\n🔧 MÉTODO 5: pdfplumber análisis de caracteres")
    print("-" * 50)
    try:
        with pdfplumber.open(archivo) as pdf:
            page = pdf.pages[0]
            chars = page.chars
            
            # Buscar la línea del nombre
            nombre_chars = []
            for char in chars:
                if char['y0'] > 620 and char['y0'] < 650:  # Ajustar coordenadas según sea necesario
                    nombre_chars.append(char)
            
            # Ordenar por posición x
            nombre_chars.sort(key=lambda x: x['x0'])
            
            # Reconstruir el texto con espacios basados en posición
            resultado = ""
            last_x = 0
            for char in nombre_chars:
                if char['x0'] - last_x > 10:  # Si hay un salto significativo, agregar espacio
                    resultado += " "
                resultado += char['text']
                last_x = char['x1']
            
            print(f"Caracteres: {repr(resultado)}")
            
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    main()
