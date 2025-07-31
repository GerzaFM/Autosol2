#!/usr/bin/env python3
"""
Script para verificar la estructura del campo Tipo en SolicitudFrame
"""

import sys
import os

# Agregar rutas necesarias
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(current_dir, 'src'))
sys.path.insert(0, os.path.join(current_dir, 'src', 'solicitudapp'))

try:
    # Intentar importar las clases necesarias
    from views.components import SolicitudFrame
    from config.app_config import AppConfig
    import tkinter as tk
    import ttkbootstrap as tb
    
    print("✅ Importaciones exitosas")
    
    # Crear una ventana temporal para probar el componente
    root = tk.Tk()
    root.withdraw()  # Ocultar la ventana principal
    
    # Crear un frame temporal
    temp_frame = tk.Frame(root)
    
    # Crear el SolicitudFrame
    solicitud_frame = SolicitudFrame(temp_frame)
    
    print(f"📋 INFORMACIÓN DEL SOLICITUDFRAME:")
    print(f"   Tipo de objeto: {type(solicitud_frame)}")
    
    # Verificar si tiene tipo_search
    if hasattr(solicitud_frame, 'tipo_search'):
        print(f"✅ Tiene tipo_search: {type(solicitud_frame.tipo_search)}")
        if solicitud_frame.tipo_search and hasattr(solicitud_frame.tipo_search, 'items'):
            print(f"   Items disponibles: {len(solicitud_frame.tipo_search.items)}")
            for i, item in enumerate(solicitud_frame.tipo_search.items[:5]):  # Mostrar primeros 5
                print(f"   {i+1}. {item}")
            if len(solicitud_frame.tipo_search.items) > 5:
                print(f"   ... y {len(solicitud_frame.tipo_search.items) - 5} más")
        else:
            print("   tipo_search no tiene items")
    else:
        print("❌ No tiene tipo_search")
    
    # Verificar si tiene entries["Tipo"]
    if hasattr(solicitud_frame, 'entries'):
        print(f"✅ Tiene entries: {type(solicitud_frame.entries)}")
        if 'Tipo' in solicitud_frame.entries:
            tipo_widget = solicitud_frame.entries['Tipo']
            print(f"   entries['Tipo']: {type(tipo_widget)}")
            print(f"   Métodos disponibles: {[m for m in dir(tipo_widget) if not m.startswith('_')][:10]}")
        else:
            print("❌ No tiene entries['Tipo']")
            print(f"   Claves disponibles: {list(solicitud_frame.entries.keys())}")
    else:
        print("❌ No tiene entries")
    
    # Verificar AppConfig para tipos disponibles
    if hasattr(AppConfig, 'TIPO_VALE'):
        print(f"\n📋 TIPOS DE VALE DISPONIBLES:")
        for clave, descripcion in AppConfig.TIPO_VALE.items():
            print(f"   {clave}: {descripcion}")
            if clave == 'VC':
                print(f"   ➡️  VC encontrado: {descripcion}")
    
    root.destroy()
    print("\n✅ Verificación completada")
    
except ImportError as e:
    print(f"❌ Error de importación: {e}")
    print("Las clases necesarias no están disponibles")
except Exception as e:
    print(f"❌ Error durante la verificación: {e}")
    import traceback
    traceback.print_exc()
