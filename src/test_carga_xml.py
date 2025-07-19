#!/usr/bin/env python3
"""
Script de prueba para verificar que la carga de XML funcione correctamente.
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

try:
    from solicitudapp.logic_solicitud import SolicitudLogica
    from solicitudapp.ctrl_xml import XMLFactura
    
    print("✅ Importaciones exitosas")
    
    # Probar cargar el XML de ejemplo
    xml_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "8954.xml")
    if os.path.exists(xml_path):
        print(f"✅ Archivo XML encontrado: {xml_path}")
        
        # Probar XMLFactura directamente
        try:
            xml_factura = XMLFactura(xml_path)
            print(f"✅ XML cargado exitosamente")
            print(f"   - RFC Emisor: {getattr(xml_factura, 'rfc_emisor', 'N/A')}")
            print(f"   - Nombre Emisor: {getattr(xml_factura, 'nombre_emisor', 'N/A')}")
            print(f"   - Total: {getattr(xml_factura, 'total', 'N/A')}")
        except Exception as e:
            print(f"❌ Error al cargar XML con XMLFactura: {e}")
        
        # Probar SolicitudLogica
        try:
            logica = SolicitudLogica()
            logica.agregar_solicitud([xml_path])
            datos = logica.get_solicitud()
            if datos:
                print("✅ SolicitudLogica funciona correctamente")
                print(f"   - Datos obtenidos: {type(datos)}")
            else:
                print("⚠️  SolicitudLogica no devolvió datos")
        except Exception as e:
            print(f"❌ Error con SolicitudLogica: {e}")
            
    else:
        print(f"❌ Archivo XML no encontrado: {xml_path}")
        
except ImportError as e:
    print(f"❌ Error de importación: {e}")
except Exception as e:
    print(f"❌ Error general: {e}")
