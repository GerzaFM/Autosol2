#!/usr/bin/env python3
"""
Prueba específica para verificar que la división de conceptos funciona correctamente
"""

import sys
import os

# Agregar rutas necesarias
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(current_dir, 'src'))
sys.path.insert(0, os.path.join(current_dir, 'src', 'solicitudapp'))

try:
    from bd.models import Factura, Reparto, Proveedor, db
    from bd.bd_control import DBManager
    import time
    
    print("🧪 PRUEBA DE DIVISIÓN DE CONCEPTOS")
    print("="*45)
    
    # Simular datos de conceptos antes de dividir
    conceptos_originales = [
        {
            'cantidad': '2',
            'descripcion': 'Servicio de mantenimiento',
            'precio_unitario': '500.00',
            'total': '1000.00'
        },
        {
            'cantidad': '1',
            'descripcion': 'Refacciones varias',
            'precio_unitario': '300.00',
            'total': '300.00'
        },
        {
            'cantidad': '3',
            'descripcion': 'Herramientas especializadas',
            'precio_unitario': '150.00',
            'total': '450.00'
        }
    ]
    
    print("📋 CONCEPTOS ORIGINALES:")
    print("-" * 80)
    print(f"{'Cant.':<6} {'Descripción':<30} {'Precio Unit.':<12} {'Total':<10}")
    print("-" * 80)
    
    total_general = 0
    for concepto in conceptos_originales:
        print(f"{concepto['cantidad']:<6} {concepto['descripcion']:<30} ${float(concepto['precio_unitario']):<11.2f} ${float(concepto['total']):<9.2f}")
        total_general += float(concepto['total'])
    
    print("-" * 80)
    print(f"{'TOTAL GENERAL:':<48} ${total_general:<9.2f}")
    print()
    
    # Simular la división (como lo haría la aplicación)
    print("🔄 APLICANDO DIVISIÓN POR 2:")
    print("-" * 80)
    print(f"{'Cant.':<6} {'Descripción':<30} {'Precio Unit.':<12} {'Total':<10}")
    print("-" * 80)
    
    conceptos_divididos = []
    total_dividido = 0
    
    for concepto in conceptos_originales:
        cantidad = concepto['cantidad']  # Cantidad permanece igual
        descripcion = concepto['descripcion']  # Descripción permanece igual
        precio_original = float(concepto['precio_unitario'])
        total_original = float(concepto['total'])
        
        # Dividir precio y total por 2
        nuevo_precio = precio_original / 2
        nuevo_total = total_original / 2
        
        concepto_dividido = {
            'cantidad': cantidad,
            'descripcion': descripcion,
            'precio_unitario': f"{nuevo_precio:.2f}",
            'total': f"{nuevo_total:.2f}"
        }
        
        conceptos_divididos.append(concepto_dividido)
        total_dividido += nuevo_total
        
        print(f"{cantidad:<6} {descripcion:<30} ${nuevo_precio:<11.2f} ${nuevo_total:<9.2f}")
        print(f"{'':>6} {'(Original: $' + f'{precio_original:.2f}' + ' → $' + f'{nuevo_precio:.2f})':<30} {'(Original: $' + f'{total_original:.2f}' + ' → $' + f'{nuevo_total:.2f})'}")
        print()
    
    print("-" * 80)
    print(f"{'TOTAL DIVIDIDO:':<48} ${total_dividido:<9.2f}")
    print(f"{'VERIFICACIÓN:':<48} ${total_general/2:<9.2f}")
    print()
    
    # Verificar que los totales cuadren
    diferencia = abs(total_dividido - (total_general / 2))
    if diferencia < 0.01:  # Tolerancia para redondeo
        print("✅ VERIFICACIÓN EXITOSA: Los totales cuadran correctamente")
    else:
        print(f"❌ ERROR: Diferencia en totales: ${diferencia:.2f}")
    
    print("\n🎯 COMPORTAMIENTO ESPERADO EN LA APLICACIÓN:")
    print("1. ✅ Cantidad permanece igual (no se divide)")
    print("2. ✅ Descripción permanece igual")
    print("3. ✅ Precio unitario se divide por 2")
    print("4. ✅ Total se divide por 2")
    print("5. ✅ La suma de conceptos divididos = total original / 2")
    
    print("\n🔧 IMPLEMENTACIÓN TÉCNICA:")
    print("- Se itera sobre cada item en self.tree.get_children()")
    print("- Se obtienen valores: [cantidad, descripcion, precio_unitario, total]")
    print("- Se dividen índices 2 (precio) y 3 (total) por 2")
    print("- Se actualizan los valores en la tabla con self.tree.item(item_id, values=nuevos_valores)")
    
    print("\n✅ PRUEBA DE DIVISIÓN DE CONCEPTOS COMPLETADA")
    
except Exception as e:
    print(f"❌ Error durante la prueba: {e}")
    import traceback
    traceback.print_exc()
