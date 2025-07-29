#!/usr/bin/env python3
"""
Script de prueba para verificar la extracción de datos del PDF de OLEKSEI
"""
import sys
import os

# Agregar src al path
src_path = os.path.join(os.path.dirname(__file__), 'src')
sys.path.insert(0, src_path)

from buscarapp.autocarga.extractor import PDFDataExtractor

def test_oleksei_extraction():
    """Prueba la extracción del PDF de OLEKSEI"""
    
    pdf_path = r'C:\QuiterWeb\cache\15gerzahin.flores_QRSVCMX_V153924_184455_CD.pdf'
    
    if not os.path.exists(pdf_path):
        print(f"❌ No se encontró el archivo: {pdf_path}")
        return
    
    print("🔍 PROBANDO EXTRACCIÓN DE DATOS DEL PDF DE OLEKSEI")
    print("="*60)
    print(f"📁 Archivo: {pdf_path}")
    print()
    
    extractor = PDFDataExtractor()
    
    # Extraer texto completo primero
    print("📋 EXTRAYENDO TEXTO COMPLETO...")
    text = extractor.extract_text_from_pdf(pdf_path)
    print(f"Longitud del texto: {len(text)} caracteres")
    print()
    print("📄 PRIMEROS 1000 CARACTERES DEL TEXTO:")
    print("-" * 40)
    print(text[:1000])
    print("-" * 40)
    print()
    
    # Buscar patrones específicos en el texto
    print("🔍 BUSCANDO PATRONES ESPECÍFICOS...")
    
    # Buscar nombre del proveedor
    import re
    patrones_nombre = [
        r'([A-Z]+\-[A-Z]+(?:\s+[A-Z\s]+)*(?:SA|S\.A\.|DE\s*CV|SADECV)?)',
        r'(OLEKSEI[^\n]*)',
        r'(MX[^\n]*SADECV)',
        r'([A-Z][A-Z\-\s&]+(?:SA\s+DE\s+CV|S\.A\.|DE\s*CV|SADECV))',
    ]
    
    print("\n📝 BÚSQUEDA DE NOMBRES:")
    for i, patron in enumerate(patrones_nombre, 1):
        matches = re.findall(patron, text, re.IGNORECASE)
        print(f"   Patrón {i}: {patron}")
        print(f"   Coincidencias: {matches}")
    
    # Buscar descripción
    patrones_descripcion = [
        r'(SERVICIOS[^\n]*)',
        r'(DEPUBLICIDAD[^\n]*)',
        r'(MARKETING[^\n]*)',
    ]
    
    print("\n📝 BÚSQUEDA DE DESCRIPCIONES:")
    for i, patron in enumerate(patrones_descripcion, 1):
        matches = re.findall(patron, text, re.IGNORECASE)
        print(f"   Patrón {i}: {patron}")
        print(f"   Coincidencias: {matches}")
    
    print("\n" + "="*60)
    print("🔧 EXTRAYENDO DATOS CON EL EXTRACTOR MEJORADO...")
    print()
    
    # Extraer datos con el extractor
    try:
        data = extractor.extract_all_data(pdf_path)
        
        print("📊 DATOS EXTRAÍDOS:")
        print("-" * 40)
        for key, value in data.items():
            status = "✅" if value else "❌"
            print(f"{status} {key:20}: {value}")
        
        # Verificar específicamente nombre y descripción
        print("\n🎯 VERIFICACIÓN ESPECÍFICA:")
        print("-" * 40)
        
        nombre = data.get('Nombre')
        if nombre:
            if 'OLEKSEI' in nombre.upper():
                print("✅ Nombre contiene 'OLEKSEI'")
            if 'MX' in nombre.upper():
                print("✅ Nombre contiene 'MX'")
            if 'SA DE CV' in nombre.upper():
                print("✅ Nombre contiene 'SA DE CV'")
            if nombre == 'MX SADECV':
                print("⚠️  Nombre extraído como 'MX SADECV' (necesita corrección)")
        
        descripcion = data.get('Descripcion')
        if descripcion:
            if 'DE PUBLICIDAD' in descripcion:
                print("✅ Descripción contiene 'DE PUBLICIDAD' (con espacio)")
            elif 'DEPUBLICIDAD' in descripcion:
                print("❌ Descripción contiene 'DEPUBLICIDAD' (sin espacio)")
            
            if 'Y MARKETING' in descripcion:
                print("✅ Descripción contiene 'Y MARKETING' (con espacio)")
            elif 'YMARKETING' in descripcion:
                print("❌ Descripción contiene 'YMARKETING' (sin espacio)")
        
    except Exception as e:
        print(f"❌ Error extrayendo datos: {e}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    test_oleksei_extraction()
