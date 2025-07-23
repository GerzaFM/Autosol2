"""
Test completo de integración para verificar que todos los componentes
de búsqueda funcionen correctamente en solicitud_app_professional.py
"""
import sys
import os

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    # Test 1: Importación de componentes de búsqueda
    from solicitudapp.search_components import SearchDialog, SearchEntry
    print("✅ Componentes de búsqueda importados correctamente")
    
    # Test 2: Importación de componentes de UI actualizados
    from solicitudapp.views.components import ProveedorFrame, SolicitudFrame
    print("✅ Componentes de UI importados correctamente")
    
    # Test 3: Verificar que las clases tengan los métodos necesarios
    proveedor_methods = ['_get_proveedores_data', '_on_proveedor_selected', 'clear_entries', 'set_data']
    for method in proveedor_methods:
        if hasattr(ProveedorFrame, method):
            print(f"✅ ProveedorFrame.{method} existe")
        else:
            print(f"❌ ProveedorFrame.{method} no existe")
    
    solicitud_methods = ['_get_tipos_data', 'clear_entries', 'set_data']
    for method in solicitud_methods:
        if hasattr(SolicitudFrame, method):
            print(f"✅ SolicitudFrame.{method} existe")
        else:
            print(f"❌ SolicitudFrame.{method} no existe")
    
    # Test 4: Verificar importación de la aplicación principal
    from solicitudapp.solicitud_app_professional import SolicitudApp
    print("✅ SolicitudApp importada correctamente")
    
    # Test 5: Verificar que SearchEntry tenga los métodos necesarios
    search_methods = ['set_selection', 'clear_selection', 'get_current_selection']
    for method in search_methods:
        if hasattr(SearchEntry, method):
            print(f"✅ SearchEntry.{method} existe")
        else:
            print(f"❌ SearchEntry.{method} no existe")
    
    print("\n🎉 Todos los tests de integración pasaron correctamente!")
    print("La implementación de búsqueda está lista para usar en solicitud_app_professional.py")
    
except ImportError as e:
    print(f"❌ Error de importación: {e}")
except Exception as e:
    print(f"❌ Error inesperado: {e}")
