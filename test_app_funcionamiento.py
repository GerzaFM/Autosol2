#!/usr/bin/env python3
"""
Script de prueba para verificar que la aplicación se puede importar y funcionar correctamente.
"""

def test_import_app():
    """Prueba importar la aplicación sin errores."""
    try:
        import sys
        import os
        sys.path.append('src')
        
        from solicitudapp.solicitud_app_professional import SolicitudApp
        print("✅ Importación exitosa de SolicitudApp")
        return True
    except Exception as e:
        print(f"❌ Error al importar SolicitudApp: {e}")
        return False

def test_app_creation():
    """Prueba crear una instancia de la aplicación."""
    try:
        import sys
        import os
        import tkinter as tk
        import ttkbootstrap as tb
        sys.path.append('src')
        
        from solicitudapp.solicitud_app_professional import SolicitudApp
        
        # Crear ventana root para la prueba
        root = tb.Window(themename="darkly")
        root.withdraw()  # Ocultar ventana para la prueba
        
        # Crear instancia de la aplicación
        app = SolicitudApp(root)
        print("✅ Creación exitosa de instancia SolicitudApp")
        
        # Verificar que tiene el método obtener_proximo_folio_interno
        if hasattr(app, 'obtener_proximo_folio_interno'):
            print("✅ Método obtener_proximo_folio_interno disponible")
        else:
            print("❌ Método obtener_proximo_folio_interno no encontrado")
        
        root.destroy()
        return True
    except Exception as e:
        print(f"❌ Error al crear instancia de SolicitudApp: {e}")
        return False

def main():
    """Ejecuta todas las pruebas."""
    print("=== PRUEBAS DE CORRECCIÓN DE APLICACIÓN ===\n")
    
    print("1. Prueba de importación:")
    import_ok = test_import_app()
    print()
    
    print("2. Prueba de creación de instancia:")
    creation_ok = test_app_creation()
    print()
    
    if import_ok and creation_ok:
        print("✅ TODAS LAS PRUEBAS PASARON - La aplicación debería funcionar correctamente")
    else:
        print("❌ ALGUNAS PRUEBAS FALLARON - Revisar errores arriba")

if __name__ == "__main__":
    main()
