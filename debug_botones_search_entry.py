"""
Test específico para los botones 🔍 de SearchEntry
"""
import sys
import os
import logging

# Configurar logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Agregar paths
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(current_dir, 'src'))

def test_search_entry_buttons():
    """Test específico para botones de SearchEntry"""
    import ttkbootstrap as ttk
    
    root = ttk.Window("DEBUG - Botones SearchEntry 🔍", themename="litera")
    root.geometry("800x600")
    
    try:
        print("🔍 TESTING BOTONES DE SEARCHENTRY")
        print("=" * 50)
        
        from buscarapp.search_components import SearchEntry
        
        # Datos de ejemplo para proveedor
        proveedores_data = [
            {'id': 1, 'nombre': 'PROVEEDOR TEST 1', 'rfc': 'RFC001', 'telefono': '123456789', 'email': 'test1@example.com'},
            {'id': 2, 'nombre': 'PROVEEDOR TEST 2', 'rfc': 'RFC002', 'telefono': '987654321', 'email': 'test2@example.com'},
            {'id': 3, 'nombre': 'SERVICIOS GLOBALES ELYT SADECV', 'rfc': 'SGE123456', 'telefono': '555000123', 'email': 'elyt@example.com'}
        ]
        
        # Datos de ejemplo para tipos
        tipos_data = [
            {'value': 'VCV', 'text': 'Vale de Caja Chica'},
            {'value': 'VOM', 'text': 'Vale de Orden de Compra'},
            {'value': 'FAC', 'text': 'Factura'}
        ]
        
        main_frame = ttk.Frame(root, padding=20)
        main_frame.pack(fill="both", expand=True)
        
        # Test 1: SearchEntry para proveedores
        ttk.Label(main_frame, text="TEST 1: Búsqueda de Proveedor", font=("Arial", 12, "bold")).pack(pady=(0, 10))
        
        proveedor_frame = ttk.Frame(main_frame)
        proveedor_frame.pack(fill="x", pady=10)
        
        ttk.Label(proveedor_frame, text="Proveedor:", font=("Segoe UI", 10)).pack(side="left", padx=(0, 5))
        
        proveedor_search = SearchEntry(
            parent=proveedor_frame,
            items=proveedores_data,
            search_fields=['nombre', 'rfc'],
            display_columns=[
                {'name': 'nombre', 'text': 'Nombre', 'width': 200},
                {'name': 'rfc', 'text': 'RFC', 'width': 120},
                {'name': 'telefono', 'text': 'Teléfono', 'width': 100},
                {'name': 'email', 'text': 'Email', 'width': 150}
            ],
            entity_type="Proveedor",
            placeholder_text="Seleccionar proveedor...",
            width=25
        )
        proveedor_search.pack(side="left", padx=(0, 15), fill="x", expand=False)
        
        # Test 2: SearchEntry para tipos
        ttk.Label(main_frame, text="TEST 2: Búsqueda de Tipo de Vale", font=("Arial", 12, "bold")).pack(pady=(20, 10))
        
        tipo_frame = ttk.Frame(main_frame)
        tipo_frame.pack(fill="x", pady=10)
        
        ttk.Label(tipo_frame, text="Tipo:", font=("Segoe UI", 10)).pack(side="left", padx=(0, 5))
        
        tipo_search = SearchEntry(
            parent=tipo_frame,
            items=tipos_data,
            search_fields=['text', 'value'],
            display_columns=[
                {'name': 'value', 'text': 'Código', 'width': 80},
                {'name': 'text', 'text': 'Descripción', 'width': 200}
            ],
            entity_type="Tipo de Vale",
            placeholder_text="Seleccionar tipo...",
            width=25
        )
        tipo_search.pack(side="left", padx=(0, 15), fill="x", expand=False)
        
        # Verificar que los botones existen
        print("\n📋 Verificando botones...")
        if hasattr(proveedor_search, 'search_button'):
            print(f"✅ Botón proveedor: {proveedor_search.search_button}")
            print(f"   📋 Comando: {proveedor_search.search_button['command']}")
        else:
            print("❌ Botón proveedor NO encontrado")
            
        if hasattr(tipo_search, 'search_button'):
            print(f"✅ Botón tipo: {tipo_search.search_button}")
            print(f"   📋 Comando: {tipo_search.search_button['command']}")
        else:
            print("❌ Botón tipo NO encontrado")
        
        # Función para testear selecciones
        def test_selections():
            print("\n🧪 TESTING SELECCIONES:")
            
            proveedor_sel = proveedor_search.get_selected_item()
            print(f"   Proveedor seleccionado: {proveedor_sel}")
            
            tipo_sel = tipo_search.get_selected_item()
            print(f"   Tipo seleccionado: {tipo_sel}")
        
        # Botón para testear selecciones
        test_btn = ttk.Button(main_frame, text="Mostrar Selecciones", command=test_selections)
        test_btn.pack(pady=20)
        
        # Instrucciones
        instructions = ttk.Frame(main_frame, bootstyle="info")
        instructions.pack(fill="x", pady=20)
        
        ttk.Label(instructions, 
                 text="🎯 INSTRUCCIONES:", 
                 font=("Arial", 11, "bold"),
                 bootstyle="info").pack(anchor="w")
        
        ttk.Label(instructions, 
                 text="1. Presiona los botones 🔍 para abrir los diálogos de búsqueda", 
                 font=("Arial", 10),
                 bootstyle="info").pack(anchor="w", padx=10)
        
        ttk.Label(instructions, 
                 text="2. Selecciona un elemento en los diálogos", 
                 font=("Arial", 10),
                 bootstyle="info").pack(anchor="w", padx=10)
        
        ttk.Label(instructions, 
                 text="3. Presiona 'Mostrar Selecciones' para ver los resultados", 
                 font=("Arial", 10),
                 bootstyle="info").pack(anchor="w", padx=10)
        
        print("\n🎯 Ventana lista - prueba los botones 🔍")
        print("   Si no se abren diálogos, hay un problema en _open_search_dialog")
        
        root.mainloop()
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_search_entry_buttons()
