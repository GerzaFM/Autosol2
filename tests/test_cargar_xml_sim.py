#!/usr/bin/env python3
"""
Script para simular el botón Cargar XML con logging detallado
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox

# Agregar el directorio src al path como lo hace main.py
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def simular_cargar_xml():
    """Simula exactamente lo que hace el botón Cargar XML"""
    
    print("=== Simulación Cargar XML ===")
    
    try:
        print("1. Importando módulos...")
        from solicitudapp.solicitud_app_professional import SolicitudApp
        from bd.models import Factura, Proveedor
        print("✅ Módulos importados")
        
        print("2. Creando aplicación...")
        root = tk.Tk()
        root.withdraw()
        app = SolicitudApp(master=root)
        print("✅ Aplicación creada")
        
        print("3. Preparando ruta del XML...")
        xml_path = "8954.xml"
        if not os.path.exists(xml_path):
            print(f"❌ Archivo XML no encontrado: {xml_path}")
            return
        
        rutas = [xml_path]
        print(f"✅ Ruta del XML: {rutas}")
        
        print("4. Limpiando todo...")
        app.limpiar_todo()
        print("✅ Aplicación limpiada")
        
        print("5. Agregando solicitud...")
        app.control.agregar_solicitud(rutas)
        print("✅ Solicitud agregada")
        
        print("6. Actualizando solicitudes restantes...")
        app.actualizar_solicitudes_restantes()
        print("✅ Solicitudes restantes actualizadas")
        
        print("7. Obteniendo datos del XML...")
        datos = app.control.get_solicitud()
        if not datos:
            print("❌ No se obtuvieron datos del XML")
            return
        print(f"✅ Datos obtenidos: RFC={datos.rfc_emisor}, Serie={datos.serie}, Folio={datos.folio}")
        
        print("8. Verificando duplicados en BD...")
        proveedor_rfc = getattr(datos, "rfc_emisor", "")
        serie = getattr(datos, "serie", "")
        folio = getattr(datos, "folio", "")
        
        print(f"   Buscando proveedor con RFC: {proveedor_rfc}")
        proveedor = Proveedor.get_or_none(Proveedor.rfc == proveedor_rfc)
        if proveedor:
            print(f"   Proveedor encontrado: {proveedor.nombre}")
            existe = Factura.select().where(
                (Factura.proveedor == proveedor) &
                (Factura.serie == serie) &
                (Factura.folio == folio)
            ).exists()
            if existe:
                print("⚠️ Factura duplicada encontrada")
                return
            else:
                print("✅ Factura no duplicada")
        else:
            print("✅ Proveedor no encontrado en BD (no hay duplicados)")
        
        print("9. Rellenando campos...")
        app.rellenar_campos()
        print("✅ Campos rellenados")
        
        print("10. Verificando campos rellenados...")
        # Verificar algunos campos específicos
        if hasattr(app, 'proveedor_frame') and app.proveedor_frame:
            if hasattr(app.proveedor_frame, 'entry_nombre') and app.proveedor_frame.entry_nombre:
                valor_nombre = app.proveedor_frame.entry_nombre.get()
                print(f"   Nombre proveedor: '{valor_nombre}'")
        
        print("✅ Test de cargar XML completado exitosamente")
        
        root.destroy()
        
    except Exception as e:
        print(f"❌ Error en simulación: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    simular_cargar_xml()
