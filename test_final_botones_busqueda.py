"""
Test final para verificar que los botones 🔍 funcionan con datos de configuración
"""
import sys
import os

# Agregar paths
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(current_dir, 'src'))

def test_final_search_buttons():
    """Test final de botones de búsqueda con datos reales"""
    import ttkbootstrap as ttk
    
    root = ttk.Window("TEST FINAL - Botones de Búsqueda 🔍", themename="litera")
    root.geometry("1200x800")
    
    try:
        print("🎯 TEST FINAL DE BOTONES DE BÚSQUEDA")
        print("=" * 60)
        
        # Importar configuración
        try:
            from solicitudapp.config.app_config import AppConfig
            print(f"✅ Configuración cargada - {len(AppConfig.TIPO_VALE)} tipos de vale disponibles")
        except ImportError:
            print("❌ No se pudo cargar la configuración")
            AppConfig = None
        
        # Simular la creación exacta como en BuscarAppRefactored
        from buscarapp.views.search_frame import SearchFrame
        
        # Datos de proveedores simulados (como los reales)
        proveedores_data = [
            {'id': 1, 'nombre': 'SERVICIOS GLOBALES ELYT SADECV', 'rfc': 'SGE123456', 'telefono': '555000123', 'email': 'elyt@example.com'},
            {'id': 2, 'nombre': 'CORPORATIVO INDUSTRIAL TAKATA', 'rfc': 'CIT789012', 'telefono': '555000456', 'email': 'takata@example.com'},
            {'id': 3, 'nombre': 'TRANSPORTES UNIDOS DEL NORTE', 'rfc': 'TUN345678', 'telefono': '555000789', 'email': 'transporte@example.com'}
        ]
        
        # Datos de tipos desde configuración
        if AppConfig:
            tipos_data = [
                {'value': clave, 'text': f"{clave} - {descripcion}"}
                for clave, descripcion in AppConfig.TIPO_VALE.items()
            ]
        else:
            tipos_data = [
                {'value': 'VCV', 'text': 'VCV - Vale de Caja Chica'},
                {'value': 'VOM', 'text': 'VOM - Vale de Orden de Compra'}
            ]
        
        print(f"📋 Datos preparados:")
        print(f"   Proveedores: {len(proveedores_data)}")
        print(f"   Tipos de vale: {len(tipos_data)}")
        
        # Callbacks
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
        
        # Pasar los datos exactamente como lo hace BuscarAppRefactored
        search_frame.set_proveedores_data(proveedores_data)
        search_frame.set_tipos_data(tipos_data)
        
        print("✅ SearchFrame creado y configurado con datos")
        
        # Panel de instrucciones
        instructions_frame = ttk.LabelFrame(root, text="🎯 INSTRUCCIONES DE PRUEBA", padding=10)
        instructions_frame.pack(side="bottom", fill="x", padx=10, pady=10)
        
        instructions = [
            "1. Presiona el botón 🔍 junto a 'Proveedor' para ver la lista de proveedores",
            "2. Presiona el botón 🔍 junto a 'Tipo' para ver todos los tipos de vale de la configuración", 
            "3. Selecciona elementos en los diálogos y ve cómo se actualizan los campos",
            "4. Presiona 'Buscar' para ejecutar la búsqueda con los filtros seleccionados",
            "5. Presiona 'Limpiar Filtros' para resetear todos los campos"
        ]
        
        for i, instruction in enumerate(instructions, 1):
            ttk.Label(instructions_frame, text=instruction, font=("Segoe UI", 9)).pack(anchor="w", padx=10)
        
        # Info sobre tipos de vale
        if AppConfig:
            info_text = f"📊 {len(tipos_data)} tipos de vale cargados desde AppConfig.TIPO_VALE"
            # Mostrar algunos ejemplos
            ejemplos = list(tipos_data)[:5]
            ejemplos_text = ", ".join([t['value'] for t in ejemplos])
            info_text += f"\n📝 Ejemplos: {ejemplos_text}..."
        else:
            info_text = "⚠️ Usando tipos de vale por defecto (configuración no disponible)"
        
        ttk.Label(instructions_frame, text=info_text, font=("Segoe UI", 8), foreground="blue").pack(anchor="w", padx=10, pady=(5, 0))
        
        print("\n🎯 APLICACIÓN LISTA")
        print("   Prueba los botones 🔍 para verificar que funcionan correctamente")
        print("   Mira la consola para ver los resultados de las búsquedas")
        
        root.mainloop()
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_final_search_buttons()
