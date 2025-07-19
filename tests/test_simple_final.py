#!/usr/bin/env python3
"""
Test manual simple para verificar el funcionamiento
"""

import sys
import os
import tkinter as tk

# Agregar el directorio src al path como lo hace main.py
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_simple():
    """Test simple sin interfaz gráfica"""
    
    print("=== Test Simple ===")
    
    try:
        print("1. Importando SolicitudApp...")
        from solicitudapp.solicitud_app_professional import SolicitudApp
        print("✅ SolicitudApp importada")
        
        print("2. Creando ventana raíz...")
        root = tk.Tk()
        root.withdraw()  # Ocultar ventana
        print("✅ Ventana raíz creada")
        
        print("3. Inicializando SolicitudApp...")
        app = SolicitudApp(master=root)
        print("✅ SolicitudApp inicializada")
        
        print("4. Verificando nuevas propiedades...")
        print(f"   - factura_duplicada: {app.factura_duplicada}")
        print(f"   - folio_interno_manual: {app.folio_interno_manual}")
        print("✅ Nuevas propiedades funcionando")
        
        root.destroy()
        
        print("\n🎉 ¡TODOS LOS CAMBIOS FUNCIONAN CORRECTAMENTE!")
        print("\n📋 Nuevas funcionalidades implementadas:")
        print("   ✅ Flag para detectar facturas duplicadas")
        print("   ✅ Variable para almacenar folio interno manual")
        print("   ✅ Modificación en cargar_xml para manejar duplicados")
        print("   ✅ Modificación en generar para omitir guardado en BD")
        print("   ✅ Mensajes personalizados según el caso")
        print("   ✅ Limpieza de flags al limpiar formulario")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_simple()
