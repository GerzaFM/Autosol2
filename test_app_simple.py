#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test simple de la aplicación para verificar que el GUI funciona correctamente
"""

import sys
import os

# Agregar la ruta específica al principio del path
solicitud_path = os.path.join(os.path.dirname(__file__), 'src', 'solicitudapp')
if solicitud_path not in sys.path:
    sys.path.insert(0, solicitud_path)

try:
    import ttkbootstrap as tb
    from solicitud_app_professional import SolicitudApp
    
    print("🔍 Iniciando test de aplicación...")
    
    # Crear ventana principal que permanezca abierta
    root = tb.Window(themename="pulse")
    root.title("Test - Aplicación de Solicitudes")
    root.geometry("800x600")
    
    # Crear la aplicación
    print("📱 Creando aplicación...")
    app = SolicitudApp(root)
    
    print("✅ Aplicación creada exitosamente!")
    print("🎯 La ventana debería estar visible ahora...")
    print("⚠️  Cierra la ventana para terminar el test")
    
    # Mantener la ventana abierta
    root.mainloop()
    
    print("✅ Test completado correctamente")
    
except Exception as e:
    print(f"❌ Error en el test: {e}")
    import traceback
    traceback.print_exc()
