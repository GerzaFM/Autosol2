#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
sys.path.append('src')
sys.path.append('src/buscarapp')

try:
    from autocarga.extractor_orden import OrdenDataExtractor
    from pathlib import Path
    import re
    
    def analizar_texto_pdf():
        print("=== ANÁLISIS DETALLADO DE TEXTO PDF ===")
        
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
        
        for pdf_path in pdfs[:1]:  # Solo el primero para análisis detallado
            print(f"\n🔍 Analizando: {pdf_path.name}")
            print("=" * 60)
            
            try:
                # Extraer con pdfplumber
                text_pdfplumber = extractor.extract_text_with_pdfplumber(str(pdf_path))
                
                # Extraer con PyPDF2
                text_pypdf2 = extractor.extract_text_with_pypdf2(str(pdf_path))
                
                print("📄 TEXTO PDFPlumber (primeros 1000 caracteres):")
                print(text_pdfplumber[:1000])
                print("\n" + "="*40)
                
                print("📋 TEXTO PyPDF2 (primeros 1000 caracteres):")
                print(text_pypdf2[:1000])
                print("\n" + "="*40)
                
                # Buscar líneas que contengan palabras relacionadas con importe
                print("🔍 BÚSQUEDA DE PATRONES DE IMPORTE:")
                
                # Patrones a buscar
                patrones_busqueda = [
                    r'.*[Ll][Ee][Tt][Rr][Aa][Ss].*',
                    r'.*[Pp][Ee][Ss][Oo][Ss].*',
                    r'.*MN.*',
                    r'.*100.*',
                    r'.*[A-Z]{20,}.*'  # Líneas con muchas mayúsculas seguidas (posible texto sin espacios)
                ]
                
                for i, patron in enumerate(patrones_busqueda):
                    print(f"\n📌 Patrón {i+1}: {patron}")
                    
                    matches_pdfplumber = re.findall(patron, text_pdfplumber, re.MULTILINE)
                    matches_pypdf2 = re.findall(patron, text_pypdf2, re.MULTILINE)
                    
                    print("  PDFPlumber:")
                    for match in matches_pdfplumber[:3]:  # Primeros 3 matches
                        espacios = "✅" if ' ' in match.strip() else "❌"
                        print(f"    {match.strip()[:100]}...")
                        print(f"    Espacios: {espacios}")
                    
                    print("  PyPDF2:")
                    for match in matches_pypdf2[:3]:  # Primeros 3 matches
                        espacios = "✅" if ' ' in match.strip() else "❌"
                        print(f"    {match.strip()[:100]}...")
                        print(f"    Espacios: {espacios}")
                        
                # Probar el patrón oficial del extractor
                print(f"\n🎯 PATRÓN OFICIAL DEL EXTRACTOR:")
                patterns = extractor.patterns.get('Importe_en_letras', [])
                print(f"Patrones configurados: {len(patterns)}")
                
                for i, pattern in enumerate(patterns):
                    print(f"\nPatrón {i+1}: {pattern}")
                    
                    matches_pdfplumber = re.findall(pattern, text_pdfplumber, re.IGNORECASE | re.DOTALL)
                    matches_pypdf2 = re.findall(pattern, text_pypdf2, re.IGNORECASE | re.DOTALL)
                    
                    print("  PDFPlumber matches:")
                    for match in matches_pdfplumber[:2]:
                        espacios = "✅" if ' ' in str(match).strip() else "❌"
                        print(f"    {str(match).strip()[:100]}...")
                        print(f"    Espacios: {espacios}")
                    
                    print("  PyPDF2 matches:")
                    for match in matches_pypdf2[:2]:
                        espacios = "✅" if ' ' in str(match).strip() else "❌"
                        print(f"    {str(match).strip()[:100]}...")
                        print(f"    Espacios: {espacios}")
                    
            except Exception as e:
                print(f"❌ Error procesando {pdf_path.name}: {e}")

    if __name__ == "__main__":
        analizar_texto_pdf()

except ImportError as e:
    print(f"❌ Error al importar: {e}")
    print("Verifica que las rutas de los módulos sean correctas")
