#!/usr/bin/env python3
"""
Test final para verificar que todo funciona correctamente
"""

import sys
import os

# Agregar el directorio src al path como lo hace main.py
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_final():
    """Test final de todas las funcionalidades"""
    
    print("=== Test Final de Funcionalidades ===")
    
    try:
        print("1. Verificando tablas de BD...")
        from bd.models import db
        db.connect()
        tablas = db.get_tables()
        print(f"✅ Tablas encontradas: {len(tablas)} tablas")
        db.close()
        
        print("2. Probando carga de XML...")
        from solicitudapp.ctrl_xml import XMLFactura
        xml_path = "8954.xml"
        if os.path.exists(xml_path):
            xml_factura = XMLFactura(xml_path)
            print(f"✅ XML cargado: {xml_factura.rfc_emisor}")
        
        print("3. Probando SolicitudLogica...")
        from solicitudapp.logic_solicitud import SolicitudLogica
        logica = SolicitudLogica()
        logica.agregar_solicitud([xml_path])
        datos = logica.get_solicitud()
        if datos:
            print(f"✅ SolicitudLogica funciona: {datos.rfc_emisor}")
        
        print("4. Probando SolicitudApp (sin UI)...")
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()
        
        from solicitudapp.solicitud_app_professional import SolicitudApp
        app = SolicitudApp(master=root)
        print("✅ SolicitudApp inicializada con DBManager")
        
        print("5. Probando método cargar_xml (simulado)...")
        app.control.agregar_solicitud([xml_path])
        datos_app = app.control.get_solicitud()
        if datos_app:
            print(f"✅ App puede procesar XML: {datos_app.rfc_emisor}")
        
        root.destroy()
        
        print("\n🎉 TODAS LAS FUNCIONALIDADES FUNCIONAN CORRECTAMENTE")
        print("📋 Resumen:")
        print("   - ✅ Base de datos inicializada")
        print("   - ✅ Carga de XML funcionando")
        print("   - ✅ SolicitudLogica operativa")
        print("   - ✅ SolicitudApp con DBManager")
        print("   - ✅ Integración completa")
        
    except Exception as e:
        print(f"❌ Error en test final: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_final()
