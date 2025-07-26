"""
Test con la estructura corregida de datos para tipos de vale
"""
import sys
import os

# Agregar paths
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(current_dir, 'src'))

def test_search_corrected():
    """Test con la estructura de datos corregida"""
    import ttkbootstrap as ttk
    
    root = ttk.Window("TEST - Búsqueda Corregida", themename="litera")
    root.geometry("1200x800")
    
    try:
        print("🔧 TEST CON ESTRUCTURA DE DATOS CORREGIDA")
        print("=" * 60)
        
        # Importar configuración
        try:
            from solicitudapp.config.app_config import AppConfig
            print(f"✅ Configuración cargada - {len(AppConfig.TIPO_VALE)} tipos de vale disponibles")
        except ImportError:
            print("❌ No se pudo cargar la configuración")
            AppConfig = None
        
        from buscarapp.views.search_frame import SearchFrame
        
        # Datos de proveedores (formato correcto)
        proveedores_data = [
            {'id': 1, 'nombre': 'SERVICIOS GLOBALES ELYT SADECV', 'rfc': 'SGE123456', 'telefono': '555000123', 'email': 'elyt@example.com'},
            {'id': 2, 'nombre': 'CORPORATIVO INDUSTRIAL TAKATA', 'rfc': 'CIT789012', 'telefono': '555000456', 'email': 'takata@example.com'},
            {'id': 3, 'nombre': 'TRANSPORTES UNIDOS DEL NORTE', 'rfc': 'TUN345678', 'telefono': '555000789', 'email': 'transporte@example.com'}
        ]
        
        # Datos de tipos con estructura corregida (como en solicitud_app)
        if AppConfig:
            tipos_data = []
            for clave, descripcion in AppConfig.TIPO_VALE.items():
                tipos_data.append({
                    'clave': clave,
                    'descripcion': descripcion,
                    'display': f"{clave} - {descripcion}"
                })
        else:
            tipos_data = [
                {'clave': 'VCV', 'descripcion': 'Vale de Caja Chica', 'display': 'VCV - Vale de Caja Chica'},
                {'clave': 'VOM', 'descripcion': 'Vale de Orden de Compra', 'display': 'VOM - Vale de Orden de Compra'}
            ]
        
        print(f"📋 Datos preparados:")
        print(f"   Proveedores: {len(proveedores_data)}")
        print(f"   Tipos de vale: {len(tipos_data)}")
        print(f"   Primeros 3 tipos: {[t['display'] for t in tipos_data[:3]]}")
        
        # Callbacks con logging detallado
        def _on_search(filters_dict):
            print(f"\n🔍 BÚSQUEDA EJECUTADA:")
            for key, value in filters_dict.items():
                if value:  # Solo mostrar filtros con valor
                    print(f"   {key}: {value}")
        
        def _on_clear_search():
            print("\n🧹 FILTROS LIMPIADOS")
        
        # Crear SearchFrame
        main_container = ttk.Frame(root, padding=10)
        main_container.pack(fill="both", expand=True)
        
        search_frame = SearchFrame(
            main_container,
            on_search_callback=_on_search,
            on_clear_callback=_on_clear_search
        )
        
        # Pasar los datos con estructura corregida
        search_frame.set_proveedores_data(proveedores_data)
        search_frame.set_tipos_data(tipos_data)
        
        print("✅ SearchFrame creado y configurado con datos corregidos")
        
        # Función para testear selecciones
        def mostrar_selecciones():
            print("\n🧪 ESTADO ACTUAL DE SELECCIONES:")
            
            # Verificar tipo seleccionado
            if hasattr(search_frame, 'tipo_search') and search_frame.tipo_search:
                tipo_sel = search_frame.tipo_search.get_selected_item()
                print(f"   Tipo seleccionado: {tipo_sel}")
            
            # Verificar proveedor seleccionado
            if hasattr(search_frame, 'proveedor_search_widget') and search_frame.proveedor_search_widget:
                prov_sel = search_frame.proveedor_search_widget.get_selected_item()
                print(f"   Proveedor seleccionado: {prov_sel}")
            
            # Mostrar filtros actuales
            filters = search_frame.get_filters()
            print(f"   Filtros actuales: {filters}")
        
        # Panel de botones de prueba
        test_buttons_frame = ttk.LabelFrame(root, text="🧪 CONTROLES DE PRUEBA", padding=10)
        test_buttons_frame.pack(side="bottom", fill="x", padx=10, pady=10)
        
        ttk.Button(test_buttons_frame, text="Mostrar Selecciones", command=mostrar_selecciones).pack(side="left", padx=5)
        
        # Panel de instrucciones
        instructions_frame = ttk.LabelFrame(root, text="🎯 INSTRUCCIONES MEJORADAS", padding=10)
        instructions_frame.pack(side="bottom", fill="x", padx=10, pady=5)
        
        instructions = [
            "1. 🔍 TIPO: Presiona el botón 🔍 junto a 'Tipo' - ahora debería mostrar formato 'CLAVE - Descripción'",
            "2. 🔍 PROVEEDOR: Presiona el botón 🔍 junto a 'Proveedor' - debería mostrar lista de proveedores",
            "3. ✅ SELECCIONAR: Elige elementos en los diálogos y ve cómo se actualizan",
            "4. 🧪 PROBAR: Usa 'Mostrar Selecciones' para ver qué se está capturando",
            "5. 🔍 BUSCAR: Presiona 'Buscar' para ejecutar la búsqueda con filtros"
        ]
        
        for instruction in instructions:
            ttk.Label(instructions_frame, text=instruction, font=("Segoe UI", 9)).pack(anchor="w", padx=5)
        
        # Info técnica
        info_text = f"🔧 Estructura corregida: search_fields=['clave', 'descripcion'], {len(tipos_data)} tipos disponibles"
        ttk.Label(instructions_frame, text=info_text, font=("Segoe UI", 8), foreground="blue").pack(anchor="w", padx=5, pady=(5, 0))
        
        print("\n🎯 APLICACIÓN LISTA CON ESTRUCTURA CORREGIDA")
        print("   Prueba los botones 🔍 - deberían funcionar igual que en solicitud_app")
        
        root.mainloop()
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_search_corrected()
