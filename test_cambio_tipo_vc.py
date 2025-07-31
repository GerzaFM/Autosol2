#!/usr/bin/env python3
"""
Prueba específica para verificar que el cambio de tipo a VC funciona en el SolicitudFrame
"""

import sys
import os

# Agregar rutas necesarias
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(current_dir, 'src'))
sys.path.insert(0, os.path.join(current_dir, 'src', 'solicitudapp'))

try:
    from views.components import SolicitudFrame
    from config.app_config import AppConfig
    import tkinter as tk
    import ttkbootstrap as tb
    
    print("🧪 PRUEBA DE CAMBIO DE TIPO A VC")
    print("="*40)
    
    # Crear una ventana temporal para probar el componente
    root = tk.Tk()
    root.withdraw()  # Ocultar la ventana principal
    
    # Crear un frame temporal
    temp_frame = tk.Frame(root)
    
    # Crear el SolicitudFrame
    solicitud_frame = SolicitudFrame(temp_frame)
    
    print("✅ SolicitudFrame creado")
    
    # Verificar estado inicial
    if hasattr(solicitud_frame, 'tipo_search') and solicitud_frame.tipo_search:
        initial_selection = solicitud_frame.tipo_search.get_selected_item()
        print(f"📋 Selección inicial: {initial_selection}")
        
        # Buscar el item VC específicamente
        print(f"\n🔍 Buscando item con clave 'VC'...")
        vc_item = None
        for item in solicitud_frame.tipo_search.items:
            if item.get('clave') == 'VC':
                vc_item = item
                break
        
        if vc_item:
            print(f"✅ Item VC encontrado: {vc_item}")
            
            # Intentar seleccionar el item VC
            try:
                solicitud_frame.tipo_search.set_selection(vc_item)
                print("✅ set_selection(vc_item) ejecutado")
                
                # Verificar si la selección cambió
                new_selection = solicitud_frame.tipo_search.get_selected_item()
                print(f"📋 Nueva selección: {new_selection}")
                
                if new_selection and new_selection.get('clave') == 'VC':
                    print("🎉 ¡ÉXITO! El tipo se cambió correctamente a VC")
                else:
                    print("❌ FALLO: La selección no cambió a VC")
                    
            except Exception as e:
                print(f"❌ Error al cambiar selección: {e}")
        else:
            print("❌ No se encontró item con clave 'VC'")
            print("Items disponibles con 'VC' en el nombre:")
            for item in solicitud_frame.tipo_search.items:
                if 'VC' in str(item) or 'VALE' in str(item):
                    print(f"   - {item}")
    else:
        print("❌ No se puede acceder a tipo_search")
    
    # Probar también el método get_data para ver cómo se reporta
    try:
        data = solicitud_frame.get_data()
        print(f"\n📊 Datos del formulario:")
        for key, value in data.items():
            if 'tipo' in key.lower():
                print(f"   {key}: {value}")
    except Exception as e:
        print(f"❌ Error obteniendo datos: {e}")
    
    root.destroy()
    print("\n✅ Prueba completada")
    
except ImportError as e:
    print(f"❌ Error de importación: {e}")
except Exception as e:
    print(f"❌ Error durante la prueba: {e}")
    import traceback
    traceback.print_exc()
