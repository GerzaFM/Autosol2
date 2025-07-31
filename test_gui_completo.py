#!/usr/bin/env python3
"""
Script de prueba completo para verificar que la ventana de la aplicación se muestra correctamente.
"""
import sys
import os
import tkinter as tk
import ttkbootstrap as tb

def test_gui_basico():
    """Prueba básica de GUI para verificar que ttkbootstrap funciona."""
    try:
        print("Probando GUI básico...")
        root = tb.Window(themename="darkly", title="Prueba GUI Básico")
        root.geometry("400x300")
        
        # Agregar un label simple
        label = tb.Label(root, text="Si ves esta ventana, ttkbootstrap funciona", font=("Arial", 12))
        label.pack(pady=50)
        
        # Botón para cerrar
        btn_cerrar = tb.Button(root, text="Cerrar", command=root.destroy)
        btn_cerrar.pack(pady=20)
        
        print("✅ GUI básico creado exitosamente")
        print("La ventana debería aparecer ahora...")
        
        root.mainloop()
        return True
    except Exception as e:
        print(f"❌ Error en GUI básico: {e}")
        return False

def test_importacion_app():
    """Prueba importar y mostrar la aplicación real."""
    try:
        print("\nProbando importación de SolicitudApp...")
        
        # Agregar paths necesarios
        sys.path.append('src')
        sys.path.append(os.path.join(os.path.dirname(__file__)))
        
        from solicitudapp.solicitud_app_professional import SolicitudApp
        
        print("✅ Importación exitosa")
        
        # Crear ventana principal
        root = tb.Window(themename="darkly", title="TCM Matehuala - Prueba")
        root.geometry("1200x800")
        
        # Crear la aplicación
        app = SolicitudApp(root)
        app.pack(fill="both", expand=True)
        
        print("✅ SolicitudApp creada y empaquetada")
        print("La ventana principal debería aparecer ahora...")
        
        root.mainloop()
        return True
        
    except Exception as e:
        print(f"❌ Error al crear SolicitudApp: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Ejecuta las pruebas de GUI."""
    print("=== PRUEBAS DE GUI Y VISUALIZACIÓN ===\n")
    
    respuesta = input("¿Quieres probar primero el GUI básico? (s/n): ").lower().strip()
    
    if respuesta == 's':
        print("\n1. Probando GUI básico de ttkbootstrap:")
        if not test_gui_basico():
            print("❌ El GUI básico no funciona. Verifica la instalación de ttkbootstrap.")
            return
    
    print("\n2. Probando aplicación completa:")
    test_importacion_app()

if __name__ == "__main__":
    main()
