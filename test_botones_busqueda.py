"""
Test para verificar el estado de los botones de búsqueda
"""
import sys
import os

# Agregar paths
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(current_dir, 'src'))

def test_search_components():
    """Test para verificar si SearchEntry está disponible"""
    try:
        from buscarapp.search_components import SearchEntry
        print("✅ SearchEntry importado correctamente")
        return True
    except ImportError as e:
        print(f"❌ Error importando SearchEntry: {e}")
        return False

def test_search_frame():
    """Test para verificar SearchFrame"""
    try:
        from buscarapp.views.search_frame import SearchFrame, SEARCH_ENTRY_AVAILABLE
        print(f"✅ SearchFrame importado. SEARCH_ENTRY_AVAILABLE: {SEARCH_ENTRY_AVAILABLE}")
        return True
    except ImportError as e:
        print(f"❌ Error importando SearchFrame: {e}")
        return False

def test_button_functionality():
    """Test básico de funcionalidad de botones"""
    import ttkbootstrap as ttk
    
    def test_callback(data):
        print(f"🔍 Callback ejecutado con datos: {data}")
    
    def test_clear_callback():
        print("🧹 Callback de limpiar ejecutado")
    
    root = ttk.Window("Test Botones", themename="litera")
    root.geometry("600x400")
    
    try:
        from buscarapp.views.search_frame import SearchFrame
        
        search_frame = SearchFrame(
            root,
            on_search_callback=test_callback,
            on_clear_callback=test_clear_callback
        )
        
        print("✅ SearchFrame creado correctamente")
        
        # Verificar si los botones están creados
        if hasattr(search_frame, 'buscar_btn'):
            print(f"✅ Botón buscar encontrado: {search_frame.buscar_btn}")
        else:
            print("❌ Botón buscar NO encontrado")
            
        if hasattr(search_frame, 'limpiar_btn'):
            print(f"✅ Botón limpiar encontrado: {search_frame.limpiar_btn}")
        else:
            print("❌ Botón limpiar NO encontrado")
        
        # Test de obtener filtros
        try:
            filters = search_frame.get_filters()
            print(f"✅ get_filters() funciona: {filters}")
        except Exception as e:
            print(f"❌ Error en get_filters(): {e}")
        
        print("\n🎯 Presiona los botones para probar funcionalidad")
        print("   Cierra la ventana cuando termines")
        
        root.mainloop()
        
    except Exception as e:
        print(f"❌ Error creando SearchFrame: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🧪 TEST DE BOTONES DE BÚSQUEDA")
    print("=" * 50)
    
    print("\n1. Verificando SearchEntry...")
    test_search_components()
    
    print("\n2. Verificando SearchFrame...")
    test_search_frame()
    
    print("\n3. Test de funcionalidad de botones...")
    test_button_functionality()
