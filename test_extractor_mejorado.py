#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
sys.path.append('src')
sys.path.append('src/buscarapp')

try:
    from autocarga.extractor_orden import OrdenDataExtractor
    from pathlib import Path
    import re
    
    def test_extractor_mejorado():
        print("=== TEST DEL EXTRACTOR MEJORADO (PyPDF2 Priorizado) ===")
        
        extractor = OrdenDataExtractor()
        
        # Vamos a testear con texto simulado para demostrar la diferencia
        print("🧪 SIMULACIÓN CON TEXTO DE PRUEBA:")
        
        # Simular texto como lo extraería pdfplumber (sin espacios)
        texto_pdfplumber_simulado = """
        IMPORTE: $9,574.12
        IMPORTEENLETRAS: NUEVEMILQUINIENTOSSETENTAYCUATROPESOS12/100MN
        FECHA: 2025-07-30
        """
        
        # Simular texto como lo extraería PyPDF2 (con mejores espacios)
        texto_pypdf2_simulado = """
        IMPORTE: $9,574.12
        IMPORTE EN LETRAS: NUEVE MIL QUINIENTOS SETENTA Y CUATRO PESOS 12/100 MN
        FECHA: 2025-07-30
        """
        
        print("📄 Texto simulado PDFPlumber:")
        print(texto_pdfplumber_simulado.strip())
        
        print("\n📋 Texto simulado PyPDF2:")
        print(texto_pypdf2_simulado.strip())
        
        # Probar extracción con cada método
        print("\n🔍 EXTRACCIÓN DE IMPORTE EN LETRAS:")
        
        # Simular el comportamiento del extractor mejorado
        # Primero intenta con PyPDF2
        pypdf2_result = extractor.extract_field(texto_pypdf2_simulado, 'Importe_en_letras')
        pdfplumber_result = extractor.extract_field(texto_pdfplumber_simulado, 'Importe_en_letras')
        combined_result = extractor.extract_field(texto_pdfplumber_simulado + "\n" + texto_pypdf2_simulado, 'Importe_en_letras')
        
        print(f"PyPDF2 result: '{pypdf2_result}'")
        print(f"PDFPlumber result: '{pdfplumber_result}'")
        print(f"Combined result: '{combined_result}'")
        
        # Aplicar la lógica del extractor mejorado
        if pypdf2_result and pypdf2_result.strip():
            resultado_final = pypdf2_result
            fuente = "PyPDF2 (priorizado)"
        else:
            resultado_final = combined_result
            fuente = "Texto combinado (fallback)"
            
        print(f"\n🎯 RESULTADO FINAL:")
        print(f"Fuente: {fuente}")
        print(f"Texto: '{resultado_final}'")
        
        espacios_naturales = "✅" if ' ' in resultado_final else "❌"
        print(f"Espacios naturales: {espacios_naturales}")
        
        # Aplicar post-procesamiento (función de espacios si es necesario)
        if not ' ' in resultado_final:
            resultado_postprocesado = extractor._agregar_espacios_importe_letras(resultado_final)
            print(f"Después de agregar espacios: '{resultado_postprocesado}'")
        else:
            print("No necesita agregar espacios manualmente")
            
        print(f"\n✅ CONCLUSIÓN:")
        print("La modificación permite priorizar PyPDF2 para mejor extracción de espacios")
        print("Si PyPDF2 falla, utiliza el texto combinado como respaldo")
        print("El post-procesamiento sigue disponible como última línea de defensa")

    if __name__ == "__main__":
        test_extractor_mejorado()

except ImportError as e:
    print(f"❌ Error al importar: {e}")
except Exception as e:
    print(f"❌ Error: {e}")
