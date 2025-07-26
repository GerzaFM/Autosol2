#!/usr/bin/env python3
"""
Script para analizar el PDF específico con "IMPRESORA HP LASERJET M111W, CABLES"
"""

import sys
import os
from pathlib import Path

# Agregar el directorio src al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from buscarapp.autocarga.extractor import PDFDataExtractor

def analizar_pdf_impresora():
    """
    Analiza el PDF específico que contiene "IMPRESORA HP LASERJET M111W, CABLES".
    """
    print("🔍 ANÁLISIS DE PDF CON IMPRESORA HP")
    print("=" * 70)
    
    # El archivo que mencionaste
    archivo = r"C:\QuiterWeb\cache\15gerzahin.flores_QRSVCMX_V152885_182280_CD.pdf"
    
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
        
        # Buscar específicamente "IMPRESORA", "LASERJET", "CABLES" y "DESCRIPCIÓN"
        print("\n🔍 BÚSQUEDA DE PATRONES ESPECÍFICOS:")
        print("-" * 70)
        
        lines = texto.split('\n')
        for i, line in enumerate(lines):
            line_lower = line.lower()
            if any(word in line_lower for word in ['impresora', 'laserjet', 'cables', 'descripci', 'hp']):
                print(f"Línea {i:2d}: {line}")
                # Mostrar 2 líneas antes y 2 después para contexto
                for j in range(max(0, i-2), min(len(lines), i+3)):
                    if j != i:
                        print(f"      {j:2d}: {lines[j]}")
                print("-" * 40)
        
        # Probar patrones específicos para impresora
        print("\n🧪 PRUEBA DE PATRONES DE DESCRIPCIÓN:")
        print("-" * 70)
        
        import re
        
        # Patrones a probar específicos para impresora (actualizados)
        patrones_test = [
            r'Descripción:\s*.*?\n(?:.*?\n)*(IMPRESORA[A-Z0-9,]+)\s+MATEHUALA',
            r'Descripción:\s*.*?\n(?:.*?\n)*([A-Z][A-Z0-9,\s]+?)\s+MATEHUALA',
            r'Descripción:\s*.*?\n(?:.*?\n)*(HERRAMIENTASDETRABAJO|HERRAMIENTAS\s*DE\s*TRABAJO)',
            r'Descripción:\s*.*?\n(?:.*?\n)*([A-Z]*HERRAMIENTAS[A-Z]*)',
        ]
        
        for i, patron in enumerate(patrones_test, 1):
            try:
                match = re.search(patron, texto, re.MULTILINE | re.DOTALL)
                if match:
                    print(f"✅ Patrón {i}: ENCONTRADO - '{match.group(1)}'")
                else:
                    print(f"❌ Patrón {i}: No encontrado")
            except Exception as e:
                print(f"❌ Patrón {i}: Error - {e}")
                
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    analizar_pdf_impresora()
