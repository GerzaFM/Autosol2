"""
Test completo de la funcionalidad de búsqueda avanzada.
Verifica que todos los componentes SearchEntry funcionen correctamente.
"""
import os
import sys

# Agregar el directorio padre al path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from search_components import SearchEntry, SearchDialog
    import ttkbootstrap as tb
    from ttkbootstrap.constants import *
    
    def test_search_components():
        """Prueba los componentes de búsqueda."""
        print("🧪 Iniciando pruebas de componentes de búsqueda...")
        
        # Crear ventana principal
        root = tb.Window(title="Test SearchEntry", themename="superhero")
        root.geometry("800x600")
        
        # Datos de prueba para proveedores
        proveedores_data = [
            {"nombre": "SOCIEDAD CONSTRUCTORA DUBLEX", "rfc": "SCO030101AAA", "telefono": "555-1234", "email": "contacto@dublex.com"},
            {"nombre": "MATERIALES DE OFICINA S.A.", "rfc": "MOO030101BBB", "telefono": "555-5678", "email": "ventas@materialesoficina.com"},
            {"nombre": "CONSTRUCTORES UNIDOS S.A.", "rfc": "CUU030101CCC", "telefono": "555-9012", "email": "info@constructores.com"}
        ]
        
        # Datos de prueba para tipos de vale
        tipos_data = [
            {"value": "I", "descripcion": "Ingreso"},
            {"value": "E", "descripcion": "Egreso"},
            {"value": "T", "descripcion": "Traslado"},
            {"value": "P", "descripcion": "Pago"},
            {"value": "N", "descripcion": "Nómina"}
        ]
        
        # Frame principal
        main_frame = tb.Frame(root)
        main_frame.pack(fill=BOTH, expand=True, padx=20, pady=20)
        
        # Título
        tb.Label(main_frame, text="Test de Componentes SearchEntry", 
                font=("Arial", 16, "bold")).pack(pady=(0, 20))
        
        # Test 1: SearchEntry para proveedores
        tb.Label(main_frame, text="1. Búsqueda de Proveedores:", 
                font=("Arial", 12, "bold")).pack(anchor=W, pady=(10, 5))
        
        proveedor_search = SearchEntry(
            parent=main_frame,
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
            width=40
        )
        proveedor_search.pack(fill=X, pady=(0, 10))
        
        # Test 2: SearchEntry para tipos de vale
        tb.Label(main_frame, text="2. Búsqueda de Tipos de Vale:", 
                font=("Arial", 12, "bold")).pack(anchor=W, pady=(10, 5))
        
        tipo_search = SearchEntry(
            parent=main_frame,
            items=tipos_data,
            search_fields=['value', 'descripcion'],
            display_columns=[
                {'name': 'value', 'text': 'Tipo', 'width': 80},
                {'name': 'descripcion', 'text': 'Descripción', 'width': 200}
            ],
            entity_type="Tipo de Vale",
            placeholder_text="Seleccionar tipo...",
            width=30
        )
        tipo_search.pack(fill=X, pady=(0, 20))
        
        # Función para mostrar selecciones
        def mostrar_selecciones():
            print("\n📊 Selecciones actuales:")
            
            prov_item = proveedor_search.get_selected_item()
            if prov_item:
                print(f"   Proveedor: {prov_item['nombre']} ({prov_item['rfc']})")
            else:
                print("   Proveedor: Ninguno seleccionado")
            
            tipo_item = tipo_search.get_selected_item()
            if tipo_item:
                print(f"   Tipo: {tipo_item['value']} - {tipo_item['descripcion']}")
            else:
                print("   Tipo: Ninguno seleccionado")
        
        # Función para limpiar selecciones
        def limpiar_selecciones():
            proveedor_search.clear_selection()
            tipo_search.clear_selection()
            print("\n🧹 Selecciones limpiadas")
        
        # Botones de control
        button_frame = tb.Frame(main_frame)
        button_frame.pack(fill=X, pady=10)
        
        tb.Button(button_frame, text="Mostrar Selecciones", 
                 bootstyle="info", command=mostrar_selecciones).pack(side=LEFT, padx=(0, 10))
        
        tb.Button(button_frame, text="Limpiar Selecciones", 
                 bootstyle="warning", command=limpiar_selecciones).pack(side=LEFT, padx=(0, 10))
        
        tb.Button(button_frame, text="Cerrar", 
                 bootstyle="danger", command=root.quit).pack(side=RIGHT)
        
        # Instrucciones
        instructions = tb.Text(main_frame, height=8, width=80)
        instructions.pack(fill=BOTH, expand=True, pady=(20, 0))
        
        instructions.insert("1.0", """
INSTRUCCIONES DE PRUEBA:

1. Haz clic en el botón 🔍 junto a "Seleccionar proveedor..."
   - Se abrirá un cuadro de diálogo con la lista de proveedores
   - Puedes filtrar escribiendo en el campo "Buscar"
   - Selecciona un proveedor y haz clic en "Seleccionar"

2. Haz clic en el botón 🔍 junto a "Seleccionar tipo..."
   - Se abrirá un cuadro de diálogo con los tipos de vale
   - Filtra por código (I, E, T, P, N) o descripción
   - Selecciona un tipo y confirma

3. Usa "Mostrar Selecciones" para ver qué has seleccionado
4. Usa "Limpiar Selecciones" para borrar todo

✅ Si puedes seleccionar elementos y verlos reflejados correctamente,
   los componentes SearchEntry están funcionando bien.
        """)
        
        instructions.config(state="disabled")
        
        print("✅ Componentes creados exitosamente")
        print("🔍 Interfaz de prueba lista - interactúa con los componentes")
        
        # Iniciar aplicación
        root.mainloop()
        
        print("🏁 Prueba completada")
    
    if __name__ == "__main__":
        test_search_components()
        
except ImportError as e:
    print(f"❌ Error importando componentes: {e}")
    print("Asegúrate de que search_components.py esté en el directorio actual")
except Exception as e:
    print(f"❌ Error ejecutando prueba: {e}")
    import traceback
    traceback.print_exc()
