"""
Script de prueba para verificar los componentes de búsqueda
"""
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import sys
import os

# Agregar paths necesarios
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    from search_components import SearchEntry, SearchDialog
    print("✅ SearchEntry y SearchDialog importados correctamente")
    
    # Datos de prueba
    proveedores_test = [
        {'nombre': 'Proveedor A', 'rfc': 'RFC001', 'telefono': '555-1234', 'email': 'test@email.com'},
        {'nombre': 'Proveedor B', 'rfc': 'RFC002', 'telefono': '555-5678', 'email': 'test2@email.com'},
        {'nombre': 'Empresa XYZ', 'rfc': 'XYZ123', 'telefono': '555-9999', 'email': 'xyz@email.com'}
    ]
    
    tipos_test = [
        {'clave': 'SC', 'descripcion': 'Servicios Comerciales', 'display': 'SC - Servicios Comerciales'},
        {'clave': 'VC', 'descripcion': 'Vale de Caja', 'display': 'VC - Vale de Caja'},
        {'clave': 'GG', 'descripcion': 'Gastos Generales', 'display': 'GG - Gastos Generales'}
    ]
    
    # Crear ventana de prueba
    root = ttk.Window(themename="cosmo")
    root.title("Prueba de Componentes de Búsqueda")
    root.geometry("600x400")
    
    main_frame = ttk.Frame(root, padding=20)
    main_frame.pack(fill="both", expand=True)
    
    # Título
    ttk.Label(main_frame, text="Prueba de Componentes de Búsqueda", 
              font=("Segoe UI", 16, "bold")).pack(pady=(0, 20))
    
    # SearchEntry para proveedores
    ttk.Label(main_frame, text="Proveedor:").pack(anchor="w", pady=(0, 5))
    proveedor_search = SearchEntry(
        parent=main_frame,
        items=proveedores_test,
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
    proveedor_search.pack(fill="x", pady=(0, 20))
    
    # SearchEntry para tipos
    ttk.Label(main_frame, text="Tipo de Vale:").pack(anchor="w", pady=(0, 5))
    tipo_search = SearchEntry(
        parent=main_frame,
        items=tipos_test,
        search_fields=["clave", "descripcion"],
        display_columns=[
            {"name": "clave", "text": "Clave", "width": 80},
            {"name": "descripcion", "text": "Descripción", "width": 200}
        ],
        entity_type="Tipo de Vale",
        placeholder_text="Seleccionar tipo...",
        width=25
    )
    tipo_search.pack(fill="x", pady=(0, 20))
    
    # Botón para probar selecciones
    def mostrar_selecciones():
        proveedor_sel = proveedor_search.get_selected_item()
        tipo_sel = tipo_search.get_selected_item()
        
        mensaje = "Selecciones actuales:\n\n"
        
        if proveedor_sel:
            mensaje += f"Proveedor: {proveedor_sel.get('nombre', 'N/A')} ({proveedor_sel.get('rfc', 'N/A')})\n"
        else:
            mensaje += "Proveedor: No seleccionado\n"
            
        if tipo_sel:
            mensaje += f"Tipo: {tipo_sel.get('clave', 'N/A')} - {tipo_sel.get('descripcion', 'N/A')}\n"
        else:
            mensaje += "Tipo: No seleccionado\n"
            
        ttk.dialogs.Messagebox.show_info("Selecciones", mensaje)
    
    ttk.Button(main_frame, text="Mostrar Selecciones", 
               bootstyle="primary", command=mostrar_selecciones).pack(pady=10)
    
    # Botón para limpiar
    def limpiar_selecciones():
        proveedor_search.clear_selection()
        tipo_search.clear_selection()
    
    ttk.Button(main_frame, text="Limpiar Selecciones", 
               bootstyle="secondary", command=limpiar_selecciones).pack(pady=5)
    
    # Centrar ventana
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f"{width}x{height}+{x}+{y}")
    
    print("✅ Componentes creados correctamente")
    print("🚀 Ejecutando aplicación de prueba...")
    
    root.mainloop()
    
except ImportError as e:
    print(f"❌ Error importando componentes: {e}")
except Exception as e:
    print(f"❌ Error general: {e}")
    import traceback
    traceback.print_exc()
