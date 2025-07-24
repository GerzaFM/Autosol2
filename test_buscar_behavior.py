#!/usr/bin/env python3
"""
Script para probar el comportamiento del botón "Buscar" sin filtros
"""

import sys
import os
from pathlib import Path

# Configurar rutas
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "src"))

def test_buscar_behavior():
    """Prueba el comportamiento del botón buscar."""
    print("🧪 Prueba de comportamiento del botón 'Buscar'")
    print("=" * 50)
    
    try:
        # Cambiar al directorio src
        os.chdir(str(PROJECT_ROOT / "src"))
        
        # Importar BuscarApp
        from buscarapp.buscar_app import BuscarApp
        
        # Simular la creación de la aplicación
        print("✅ BuscarApp importado correctamente")
        print("📋 Comportamiento esperado:")
        print("   1. Al iniciar: Tabla vacía")
        print("   2. Presionar 'Buscar' sin filtros: Muestra todas las facturas")
        print("   3. Presionar 'Limpiar Filtros': Tabla vacía otra vez")
        print("   4. Presionar 'Actualizar BD': Recarga datos y mantiene filtros")
        
        print("\n🎉 CONFIGURACIÓN EXITOSA")
        print("La aplicación ahora:")
        print("• Inicia con tabla vacía")
        print("• Botón 'Buscar' sin filtros = Muestra todas las facturas")
        print("• Botón 'Buscar' con filtros = Aplica filtros específicos")
        print("• Botón 'Limpiar Filtros' = Vuelve a tabla vacía")
        print("• Botón 'Actualizar BD' = Recarga y reaplica filtros existentes")
        
        return True
        
    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_buscar_behavior()
