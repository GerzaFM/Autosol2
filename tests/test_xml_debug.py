#!/usr/bin/env python3
"""
Script para probar específicamente la carga de XML desde la aplicación
"""

import sys
import os
import tkinter as tk

# Agregar el directorio src al path como lo hace main.py
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_carga_xml_completa():
    """Prueba completa de la funcionalidad de carga XML"""
    
    print("=== Test Completo de Carga XML ===")
    
    try:
        print("1. Importando SolicitudApp...")
        from solicitudapp.solicitud_app_professional import SolicitudApp
        print("✅ SolicitudApp importada correctamente")
        
        print("2. Creando ventana raíz...")
        root = tk.Tk()
        root.withdraw()  # Ocultar ventana principal
        print("✅ Ventana raíz creada")
        
        print("3. Inicializando SolicitudApp...")
        app = SolicitudApp(master=root)
        print("✅ SolicitudApp inicializada")
        
        print("4. Probando XMLFactura directamente...")
        from solicitudapp.ctrl_xml import XMLFactura
        xml_path = "8954.xml"
        if os.path.exists(xml_path):
            xml_factura = XMLFactura(xml_path)
            print(f"✅ XMLFactura cargada: {xml_factura.rfc_emisor}")
        else:
            print(f"❌ Archivo XML no encontrado: {xml_path}")
        
        print("5. Probando SolicitudLogica...")
        from solicitudapp.logic_solicitud import SolicitudLogica
        logica = SolicitudLogica()
        print("✅ SolicitudLogica inicializada")
        
        if os.path.exists(xml_path):
            print("6. Agregando solicitud a través de SolicitudLogica...")
            logica.agregar_solicitud([xml_path])
            datos = logica.get_solicitud()
            if datos:
                print(f"✅ Datos obtenidos: RFC={datos.rfc_emisor}, Total={datos.total}")
            else:
                print("❌ No se obtuvieron datos de SolicitudLogica")
        
        print("7. Probando método cargar_xml de la aplicación...")
        # Simular la carga directa usando el controlador de la app
        try:
            app.control.agregar_solicitud([xml_path])
            datos_app = app.control.get_solicitud()
            if datos_app:
                print(f"✅ App.control funciona: RFC={datos_app.rfc_emisor}")
            else:
                print("❌ App.control no devolvió datos")
        except Exception as e:
            print(f"❌ Error en app.control: {e}")
        
        print("8. Limpiando...")
        root.destroy()
        print("✅ Test completado")
        
    except Exception as e:
        print(f"❌ Error en test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_carga_xml_completa()
