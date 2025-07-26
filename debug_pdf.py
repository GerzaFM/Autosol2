#!/usr/bin/env python3
"""
Script para revisar el texto completo de un PDF y encontrar la descripción
"""

import sys
import os
from pathlib import Path

# Agregar el directorio src al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from buscarapp.autocarga.extractor import PDFDataExtractor

def debug_pdf_text():
    """
    Muestra el texto completo de un PDF para encontrar dónde está la descripción.
    """
    print("🔍 DEPURACIÓN DEL TEXTO PDF")
    print("=" * 60)
    
    # Inicializar extractor
    extractor = PDFDataExtractor()
    
    # Usar el primer archivo de vale
    archivo = Path("Pruebas/8927 SERVICIO NAVA MEDRANO.pdf")
    
    if not archivo.exists():
        print("❌ Archivo no encontrado")
        return
    
    print(f"📄 Analizando: {archivo.name}")
    print("-" * 60)
    
    try:
        # Extraer texto completo
        texto = extractor.extract_text_from_pdf(str(archivo))
        
        print("📝 TEXTO COMPLETO:")
        print("=" * 60)
        print(texto)
        print("=" * 60)
        
        # Buscar líneas que contengan palabras relacionadas con descripción
        print("\n🔍 LÍNEAS QUE CONTIENEN 'DESCRIPCI' O TÉRMINOS SIMILARES:")
        print("-" * 60)
        
        lines = texto.split('\n')
        for i, line in enumerate(lines):
            line_lower = line.lower()
            if any(word in line_lower for word in ['descripci', 'concepto', 'detalle', 'servicio']):
                print(f"Línea {i:2d}: {line}")
        
        print("\n🔍 TODAS LAS LÍNEAS NUMERADAS:")
        print("-" * 60)
        for i, line in enumerate(lines):
            if line.strip():  # Solo líneas no vacías
                print(f"{i:2d}: {line}")
                
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_pdf_text()
