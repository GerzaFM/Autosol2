"""
Test específico para debuggear la creación de widgets en SearchFrame
"""
import sys
import os
import logging

# Configurar logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Agregar paths
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(current_dir, 'src'))

def test_search_frame_creation():
    """Test detallado de la creación del SearchFrame"""
    import ttkbootstrap as ttk
    
    root = ttk.Window("DEBUG - SearchFrame Creation", themename="litera")
    root.geometry("800x600")
    
    try:
        print("🔍 INICIANDO DEBUG DE SEARCHFRAME")
        print("=" * 50)
        
        # Verificar imports
        print("1. Verificando imports...")
        from buscarapp.views.search_frame import SearchFrame, SEARCH_ENTRY_AVAILABLE
        print(f"   ✅ SearchFrame importado")
        print(f"   📋 SEARCH_ENTRY_AVAILABLE: {SEARCH_ENTRY_AVAILABLE}")
        
        # Callbacks de test
        def test_search_callback(filters):
            print(f"🔍 BÚSQUEDA EJECUTADA: {filters}")
        
        def test_clear_callback():
            print("🧹 LIMPIAR EJECUTADO")
        
        print("\n2. Creando SearchFrame...")
        search_frame = SearchFrame(
            root,
            on_search_callback=test_search_callback,
            on_clear_callback=test_clear_callback
        )
        print("   ✅ SearchFrame creado sin errores")
        
        # Verificar widgets específicos
        print("\n3. Verificando widgets...")
        widgets_to_check = [
            'main_frame', 'fecha_inicial_entry', 'fecha_final_entry',
            'no_vale_entry', 'buscar_btn', 'limpiar_btn'
        ]
        
        for widget_name in widgets_to_check:
            if hasattr(search_frame, widget_name):
                widget = getattr(search_frame, widget_name)
                print(f"   ✅ {widget_name}: {widget}")
            else:
                print(f"   ❌ {widget_name}: NO ENCONTRADO")
        
        # Verificar si el frame principal está empaquetado
        if hasattr(search_frame, 'main_frame'):
            print(f"\n4. Frame principal info:")
            print(f"   📦 Packed: {search_frame.main_frame.winfo_manager()}")
            print(f"   📐 Geometry: {search_frame.main_frame.winfo_geometry()}")
        
        # Añadir un label de test para verificar que algo aparece
        test_label = ttk.Label(root, text="🧪 TEST LABEL - Si ves esto, la ventana funciona", 
                              font=("Arial", 12), background="yellow")
        test_label.pack(pady=20)
        
        print("\n5. ¡Ventana lista!")
        print("   🎯 Busca los widgets de búsqueda en la ventana")
        print("   🎯 Si no ves botones, hay un problema en la creación")
        
        root.mainloop()
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_search_frame_creation()
