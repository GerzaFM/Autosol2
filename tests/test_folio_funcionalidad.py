#!/usr/bin/env python3
"""
Script para probar el diálogo de folio inicial con factura duplicada
"""

import sys
import os

# Agregar rutas para importaciones
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

def main():
    print("🧪 Test del diálogo de folio inicial - Funcionalidad implementada")
    print("=" * 65)
    
    print("✅ Cambios implementados:")
    print("   - El método cargar_xml() ahora obtiene el folio interno de la factura existente")
    print("   - Usa get_or_none() para obtener la factura duplicada completa")
    print("   - Muestra el folio interno existente en el mensaje de información")
    print("   - Usa initialvalue en askstring() con el folio interno de la BD")
    
    print("\n📋 Facturas disponibles para prueba:")
    
    try:
        from src.bd.bd_control import DBManager
        from src.bd.models import Proveedor, Factura
        
        # Inicializar base de datos
        db_manager = DBManager()
        
        # Mostrar facturas existentes
        facturas = Factura.select()
        for i, f in enumerate(facturas, 1):
            proveedor_nombre = f.proveedor.nombre if f.proveedor else 'N/A'
            print(f"   {i}. Serie: {f.serie}, Folio: {f.folio}")
            print(f"      Folio interno: {f.folio_interno}")
            print(f"      Proveedor: {proveedor_nombre}")
            print(f"      Total: ${f.total}")
            print()
            
    except Exception as e:
        print(f"   ❌ Error al consultar facturas: {e}")
    
    print("🧪 Pasos para probar:")
    print("   1. Ejecutar: python main.py")
    print("   2. Hacer clic en 'Nueva' para abrir la aplicación")
    print("   3. Cargar el archivo XML: 'Pruebas/8927.xml'")
    print("   4. Verificar que aparece el diálogo de advertencia")
    print("   5. Verificar que el campo de folio manual tiene el valor '2' (folio interno existente)")
    print("   6. Puede cambiar el valor o dejarlo como está")
    print("   7. Al generar, NO se guardará en la BD pero SÍ se creará el PDF")
    
    print("\n💡 Comportamiento esperado:")
    print("   - Mensaje: 'La factura ya se encuentra en la base de datos'")
    print("   - Diálogo de folio con valor inicial: '2'")
    print("   - Formulario se rellena normalmente")
    print("   - Al generar: PDF creado, BD no modificada")

if __name__ == "__main__":
    main()
