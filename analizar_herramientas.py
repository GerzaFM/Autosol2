#!/usr/bin/env python3
"""
Script para analizar el texto del PDF específico con "HERRAMIENTAS DE TRABAJO"
"""

import sys
import os
from pathlib import Path

# Agregar el directorio src al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from buscarapp.autocarga.extractor import PDFDataExtractor

def analizar_pdf_herramientas():
    """
    Analiza el PDF específico que contiene "HERRAMIENTAS DE TRABAJO".
    """
    print("🔍 ANÁLISIS DE PDF CON HERRAMIENTAS DE TRABAJO")
    print("=" * 70)
    
    # El archivo que mencionaste
    archivo = r"C:\QuiterWeb\cache\15gerzahin.flores_QRSVCMX_V153597_183460_CD.pdf"
    
    if not Path(archivo).exists():
        print(f"❌ Archivo no encontrado: {archivo}")
        return
    
    print(f"📄 Analizando: {Path(archivo).name}")
    print("-" * 70)
    
    extractor = PDFDataExtractor()
    
    try:
        # Extraer texto completo
        texto = extractor.extract_text_from_pdf(archivo)
        
        print("📝 TEXTO COMPLETO DEL PDF:")
        print("=" * 70)
        print(texto)
        print("=" * 70)
        
        # Buscar específicamente "HERRAMIENTAS" y "DESCRIPCIÓN"
        print("\n🔍 BÚSQUEDA DE PATRONES ESPECÍFICOS:")
        print("-" * 70)
        
        lines = texto.split('\n')
        for i, line in enumerate(lines):
            line_lower = line.lower()
            if any(word in line_lower for word in ['herramientas', 'descripci', 'trabajo']):
                print(f"Línea {i:2d}: {line}")
                # Mostrar 2 líneas antes y 2 después para contexto
                for j in range(max(0, i-2), min(len(lines), i+3)):
                    if j != i:
                        print(f"      {j:2d}: {lines[j]}")
                print("-" * 40)
        
        # Probar patrones específicos
        print("\n🧪 PRUEBA DE PATRONES DE DESCRIPCIÓN:")
        print("-" * 70)
        
        import re
        
        # Patrones a probar (los nuevos)
        patrones_test = [
            r'Descripción:\s*.*?\n(?:.*?\n)*(HERRAMIENTASDETRABAJO|HERRAMIENTAS\s*DE\s*TRABAJO)',
            r'Descripción:\s*.*?\n(?:.*?\n)*([A-Z]*HERRAMIENTAS[A-Z]*)',
            r'Descripción:\s*.*?\n(?:.*?\n)*([A-Z]+(?:DE)?[A-Z]+)\s+[A-Z]+',
            r'Descripción:\s*\n(?:\s*\n)*(?:[0-9-]+\s+[A-Z]+\s+[0-9%.\s]+\n)*([A-Z]+(?:DE)?[A-Z]+)',
        ]
        
        for i, patron in enumerate(patrones_test, 1):
            match = re.search(patron, texto, re.MULTILINE | re.DOTALL)
            if match:
                print(f"✅ Patrón {i}: ENCONTRADO - '{match.group(1)}'")
            else:
                print(f"❌ Patrón {i}: No encontrado")
                
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    analizar_pdf_herramientas()
