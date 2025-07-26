"""
Test que simula exactamente la creación como en BuscarAppRefactored
"""
import sys
import os
import logging

# Configurar logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Agregar paths
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(current_dir, 'src'))

def test_exact_creation():
    """Test que simula la creación exacta de BuscarAppRefactored"""
    import ttkbootstrap as ttk
    
    root = ttk.Window("DEBUG - Simulación Exacta de BuscarApp", themename="litera")
    root.geometry("1000x700")
    
    try:
        print("🔍 SIMULANDO CREACIÓN EXACTA DE BUSCARAPP")
        print("=" * 50)
        
        # Simular la estructura exacta de BuscarAppRefactored
        # 1. Frame principal (como BuscarAppRefactored hereda de ttk.Frame)
        app_frame = ttk.Frame(root, padding=10)
        app_frame.pack(fill="both", expand=True)
        
        # 2. Main container
        main_container = ttk.Frame(app_frame, padding=10)
        main_container.pack(fill="both", expand=True)
        
        print("📦 Contenedores creados")
        
        # 3. Callbacks exactos
        def _on_search(filters_dict):
            print(f"🔍 SEARCH CALLBACK: {filters_dict}")
            
        def _on_clear_search():
            print("🧹 CLEAR CALLBACK")
        
        # 4. Crear SearchFrame exactamente igual
        print("🏗️ Creando SearchFrame...")
        from buscarapp.views.search_frame import SearchFrame
        
        search_frame = SearchFrame(
            main_container,
            on_search_callback=_on_search,
            on_clear_callback=_on_clear_search
        )
        
        print("✅ SearchFrame creado")
        
        # 5. Verificar jerarquía de widgets
        print("\n📋 Jerarquía de widgets:")
        def print_widget_tree(widget, level=0):
            indent = "  " * level
            try:
                widget_info = f"{widget.winfo_class()} - {widget}"
                if hasattr(widget, 'cget'):
                    try:
                        text = widget.cget('text')
                        if text:
                            widget_info += f" (text: '{text}')"
                    except:
                        pass
                print(f"{indent}{widget_info}")
                
                for child in widget.winfo_children():
                    print_widget_tree(child, level + 1)
            except Exception as e:
                print(f"{indent}Error: {e}")
        
        print("\n🌳 Árbol de widgets de search_frame:")
        if hasattr(search_frame, 'main_frame'):
            print_widget_tree(search_frame.main_frame)
        
        # 6. Verificar empaquetado
        print(f"\n📦 Info de empaquetado:")
        print(f"   main_container: {main_container.winfo_manager()}")
        if hasattr(search_frame, 'main_frame'):
            print(f"   search_frame.main_frame: {search_frame.main_frame.winfo_manager()}")
        
        # 7. Label de confirmación
        status_label = ttk.Label(root, text="🧪 Si ves los botones de búsqueda arriba, todo funciona correctamente", 
                               font=("Arial", 10), bootstyle="success")
        status_label.pack(side="bottom", pady=10)
        
        print("\n🎯 Ventana lista - busca los controles de búsqueda")
        print("   Si no ves botones, hay un problema de visibilidad")
        
        root.mainloop()
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_exact_creation()
