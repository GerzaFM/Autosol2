"""
Script de prueba para verificar los componentes de búsqueda en solicitud_app_professional.
"""
import sys
import os

# Agregar paths necesarios
current_dir = os.path.dirname(__file__)
src_dir = os.path.dirname(current_dir)
project_root = os.path.dirname(src_dir)

sys.path.extend([current_dir, src_dir, project_root])

try:
    from solicitud_app_professional import SolicitudApp
    import ttkbootstrap as tb
    from solicitudapp.config.app_config import AppConfig
    
    def test_solicitud_app():
        """Prueba la aplicación con componentes de búsqueda."""
        print("🧪 Iniciando prueba de SolicitudApp con componentes de búsqueda...")
        
        # Crear ventana principal
        app = tb.Window(themename=AppConfig.THEME)
        app.title("Solicitud de Compra - Con Búsqueda Avanzada")
        app.geometry(AppConfig.WINDOW_SIZE)
        
        # Crear la aplicación
        frame = SolicitudApp(app)
        frame.pack(fill="both", expand=True)
        
        print("✅ Aplicación creada exitosamente")
        print("🔍 Verifica que:")
        print("   - El frame de proveedor tenga un campo de búsqueda con botón 🔍")
        print("   - El frame de solicitud tenga búsqueda para tipo de vale")
        print("   - Al seleccionar un proveedor se rellenen automáticamente los campos")
        print("   - Al seleccionar un tipo de vale se muestre correctamente")
        
        # Iniciar aplicación
        app.mainloop()
        
        print("🏁 Prueba completada")
    
    if __name__ == "__main__":
        test_solicitud_app()
        
except ImportError as e:
    print(f"❌ Error importando componentes: {e}")
    import traceback
    traceback.print_exc()
except Exception as e:
    print(f"❌ Error ejecutando prueba: {e}")
    import traceback
    traceback.print_exc()
