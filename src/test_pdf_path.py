#!/usr/bin/env python3
"""
Script para verificar que la ruta del PDF funciona correctamente
"""

import sys
import os

# Añadir el directorio de la aplicación al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'solicitudapp'))

def test_pdf_path():
    """Probar que la ruta del PDF se encuentra correctamente"""
    
    print("=== Test de Ruta PDF ===")
    
    try:
        from solicitudapp.conf import form_solicitud_interna
        print(f"✅ Ruta configurada: {form_solicitud_interna}")
        
        if os.path.exists(form_solicitud_interna):
            print(f"✅ Archivo PDF encontrado: {os.path.abspath(form_solicitud_interna)}")
        else:
            print(f"❌ Archivo PDF NO encontrado en: {os.path.abspath(form_solicitud_interna)}")
            
        # Probar que FormPDF puede inicializarse
        from solicitudapp.form_control import FormPDF
        form = FormPDF()
        print("✅ FormPDF inicializado correctamente")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_pdf_path()
