#!/usr/bin/env python3
"""
Script para reproducir el error de carga XML desde main.py
"""

import sys
import os

# Simular la importación desde main.py
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_xml_desde_main():
    """Probar carga XML como se haría desde main.py"""
    
    print("=== Test XML desde Main.py ===")
    
    try:
        from solicitudapp.solicitud_app_professional import SolicitudApp
        print("✅ Importación SolicitudApp exitosa")
        
        # Crear instancia (sin mostrar ventana)
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()  # Ocultar ventana
        
        app = SolicitudApp(master=root)
        print("✅ SolicitudApp inicializada correctamente")
        
        # Probar importación directa de XMLFactura
        from solicitudapp.ctrl_xml import XMLFactura
        print("✅ Importación XMLFactura exitosa")
        
        # Probar cargar XML
        xml_path = os.path.join(os.path.dirname(__file__), "8954.xml")
        if os.path.exists(xml_path):
            xml_factura = XMLFactura(xml_path)
            print(f"✅ XML cargado correctamente: {xml_factura.rfc_emisor}")
        else:
            print(f"❌ Archivo XML no encontrado: {xml_path}")
        
        # Probar lógica de solicitud
        from solicitudapp.logic_solicitud import SolicitudLogica
        logica = SolicitudLogica()
        print("✅ SolicitudLogica inicializada correctamente")
        
        # Simular cargar XML a través de la lógica
        if os.path.exists(xml_path):
            logica.agregar_solicitud([xml_path])
            datos = logica.get_solicitud()
            if datos:
                print(f"✅ XML procesado por SolicitudLogica: {datos.rfc_emisor}")
            else:
                print("❌ No se obtuvieron datos de SolicitudLogica")
        
        root.destroy()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_xml_desde_main()
