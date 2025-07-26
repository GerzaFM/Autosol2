"""
Test específico para probar la funcionalidad de búsqueda en la aplicación completa
"""
import sys
import os

# Agregar paths
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(current_dir, 'src'))

def test_buscar_app_search():
    """Test la aplicación completa y su funcionalidad de búsqueda"""
    import ttkbootstrap as ttk
    
    root = ttk.Window("Test BuscarApp - Funcionalidad de Búsqueda", themename="litera")
    root.geometry("1000x700")
    
    try:
        from buscarapp.buscar_app_refactored import BuscarAppRefactored
        
        print("✅ Importando BuscarAppRefactored...")
        app = BuscarAppRefactored(root)
        
        print("✅ Aplicación creada correctamente")
        
        # Verificar si search_frame existe y tiene los botones
        if hasattr(app, 'search_frame'):
            print("✅ search_frame encontrado")
            
            if hasattr(app.search_frame, 'buscar_btn'):
                print("✅ Botón buscar encontrado")
                
                # Verificar el comando del botón
                print(f"📋 Comando del botón buscar: {app.search_frame.buscar_btn['command']}")
            else:
                print("❌ Botón buscar NO encontrado")
                
            if hasattr(app.search_frame, 'limpiar_btn'):
                print("✅ Botón limpiar encontrado")
                print(f"📋 Comando del botón limpiar: {app.search_frame.limpiar_btn['command']}")
            else:
                print("❌ Botón limpiar NO encontrado")
        else:
            print("❌ search_frame NO encontrado")
        
        # Verificar callback
        if hasattr(app, '_on_search'):
            print("✅ Método _on_search encontrado")
        else:
            print("❌ Método _on_search NO encontrado")
        
        # Test manual del callback
        print("\n🧪 Test manual del callback de búsqueda...")
        try:
            test_filters = {
                'fecha_inicial': '',
                'fecha_final': '',
                'tipo_filtro': '',
                'proveedor_filtro': '',
                'no_vale_filtro': '',
                'solo_cargado': False,
                'solo_pagado': False,
                'texto_busqueda': ''
            }
            
            app._on_search(test_filters)
            print("✅ Callback _on_search ejecutado sin errores")
            
        except Exception as e:
            print(f"❌ Error en callback _on_search: {e}")
            import traceback
            traceback.print_exc()
        
        print("\n🎯 La aplicación está lista. Prueba los botones de búsqueda manualmente")
        print("   - Presiona 'Buscar' para probar la funcionalidad")
        print("   - Presiona 'Limpiar Filtros' para probar el limpiar")
        print("   - Cierra la ventana cuando termines")
        
        root.mainloop()
        
    except Exception as e:
        print(f"❌ Error en test de BuscarApp: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🧪 TEST DE FUNCIONALIDAD DE BÚSQUEDA - BUSCAR APP")
    print("=" * 60)
    test_buscar_app_search()
