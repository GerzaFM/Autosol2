#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
sys.path.append('src')
sys.path.append('src/buscarapp')

try:
    from autocarga.extractor_orden import OrdenDataExtractor
    from pathlib import Path
    
    def comparar_extractores():
        print("=== COMPARACIÓN DE EXTRACTORES DE PDF ===")
        
        # Buscar archivos PDF de prueba
        pruebas_dir = Path("Pruebas")
        if not pruebas_dir.exists():
            print("❌ No se encontró el directorio 'Pruebas'")
            return
            
        pdfs = list(pruebas_dir.glob("*.pdf"))
        if not pdfs:
            print("❌ No se encontraron archivos PDF en 'Pruebas'")
            return
            
        extractor = OrdenDataExtractor()
        
        for pdf_path in pdfs[:2]:  # Solo los primeros 2 para no llenar la consola
            print(f"\n🔍 Analizando: {pdf_path.name}")
            print("=" * 60)
            
            try:
                # Extraer con pdfplumber
                text_pdfplumber = extractor.extract_text_with_pdfplumber(str(pdf_path))
                
                # Extraer con PyPDF2
                text_pypdf2 = extractor.extract_text_with_pypdf2(str(pdf_path))
                
                # Buscar patrones de importe en letras en ambos
                importe_pattern = r'(?:IMPORTE EN LETRAS[:\s]*)?([A-Z\s\d/]*(?:PESOS|MN)[^A-Z]*)'
                
                import re
                
                matches_pdfplumber = re.findall(importe_pattern, text_pdfplumber, re.IGNORECASE)
                matches_pypdf2 = re.findall(importe_pattern, text_pypdf2, re.IGNORECASE)
                
                print("📄 PDFPlumber:")
                if matches_pdfplumber:
                    for i, match in enumerate(matches_pdfplumber[:3]):  # Primeros 3 matches
                        espacios = "✅" if ' ' in match.strip() else "❌"
                        print(f"  {i+1}: {match.strip()[:80]}...")
                        print(f"      Espacios: {espacios}")
                else:
                    print("  No se encontraron matches")
                
                print("\n📋 PyPDF2:")
                if matches_pypdf2:
                    for i, match in enumerate(matches_pypdf2[:3]):  # Primeros 3 matches
                        espacios = "✅" if ' ' in match.strip() else "❌"
                        print(f"  {i+1}: {match.strip()[:80]}...")
                        print(f"      Espacios: {espacios}")
                else:
                    print("  No se encontraron matches")
                    
                # Comparar usando el extractor oficial
                print("\n🎯 Resultado del extractor actual:")
                data = extractor.extract_all_data(str(pdf_path))
                if data.get('Importe_en_letras'):
                    espacios = "✅" if ' ' in data['Importe_en_letras'] else "❌"
                    print(f"  Importe extraído: {data['Importe_en_letras'][:80]}...")
                    print(f"  Espacios: {espacios}")
                else:
                    print("  No se extrajo importe en letras")
                    
            except Exception as e:
                print(f"❌ Error procesando {pdf_path.name}: {e}")

    if __name__ == "__main__":
        comparar_extractores()

except ImportError as e:
    print(f"❌ Error al importar: {e}")
    print("Verifica que las rutas de los módulos sean correctas")
