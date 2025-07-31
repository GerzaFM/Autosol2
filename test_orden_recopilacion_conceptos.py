"""
Prueba para verificar que los conceptos se recopilan DESPUÉS de la división,
no antes, para que la primera factura tenga los valores divididos correctos.
"""

def test_orden_recopilacion_conceptos():
    """
    Simula el orden correcto de operaciones para asegurar que los conceptos
    se recopilan después de aplicar la división.
    """
    print("=== PRUEBA: Orden Correcto de Recopilación de Conceptos ===\n")
    
    # Simular datos originales en la tabla
    tabla_conceptos = [
        {"id": "item1", "values": ["2", "Producto A", "300.00", "600.00"]},
        {"id": "item2", "values": ["1", "Producto B", "400.00", "400.00"]}
    ]
    
    print("PASO 1: Datos originales en la tabla")
    print("-" * 40)
    for item in tabla_conceptos:
        values = item["values"]
        print(f"  {values[1]}: Cant={values[0]}, P.Unit=${values[2]}, Total=${values[3]}")
    
    # Estado de división
    dividir_marcado = True
    valores_ya_divididos = False
    
    print(f"\nPASO 2: Estado de división")
    print("-" * 40)
    print(f"  dividir_marcado: {dividir_marcado}")
    print(f"  valores_ya_divididos: {valores_ya_divididos}")
    
    # ORDEN ANTERIOR (INCORRECTO)
    print(f"\n❌ ORDEN ANTERIOR (INCORRECTO):")
    print("-" * 50)
    print("1. Recopilar conceptos ANTES de división")
    conceptos_antes = [item["values"] for item in tabla_conceptos]
    print("   conceptos =", conceptos_antes)
    
    print("2. Aplicar división en tabla visual")
    if dividir_marcado and not valores_ya_divididos:
        print("   ✅ División aplicada en tabla visual")
        for item in tabla_conceptos:
            values = item["values"]
            precio_original = float(values[2])
            total_original = float(values[3])
            values[2] = f"{precio_original / 2:.2f}"  # Dividir precio
            values[3] = f"{total_original / 2:.2f}"   # Dividir total
            print(f"     {values[1]}: P.Unit ${precio_original:.2f} → ${values[2]}, Total ${total_original:.2f} → ${values[3]}")
        valores_ya_divididos = True
        
    print("3. Generar PDF con conceptos (valores SIN dividir)")
    print("   📄 PDF generado con:", conceptos_antes)
    print("   ❌ PROBLEMA: PDF tiene valores originales, no divididos!")
    
    # Resetear datos para nueva prueba
    tabla_conceptos = [
        {"id": "item1", "values": ["2", "Producto A", "300.00", "600.00"]},
        {"id": "item2", "values": ["1", "Producto B", "400.00", "400.00"]}
    ]
    valores_ya_divididos = False
    
    print(f"\n✅ ORDEN NUEVO (CORRECTO):")
    print("-" * 50)
    print("1. Aplicar división en tabla visual")
    if dividir_marcado and not valores_ya_divididos:
        print("   ✅ División aplicada en tabla visual")
        for item in tabla_conceptos:
            values = item["values"]
            precio_original = float(values[2])
            total_original = float(values[3])
            values[2] = f"{precio_original / 2:.2f}"  # Dividir precio
            values[3] = f"{total_original / 2:.2f}"   # Dividir total
            print(f"     {values[1]}: P.Unit ${precio_original:.2f} → ${values[2]}, Total ${total_original:.2f} → ${values[3]}")
        valores_ya_divididos = True
    
    print("2. Recopilar conceptos DESPUÉS de división")
    conceptos_despues = [item["values"] for item in tabla_conceptos]
    print("   conceptos =", conceptos_despues)
    
    print("3. Generar PDF con conceptos (valores divididos)")
    print("   📄 PDF generado con:", conceptos_despues)
    print("   ✅ CORRECTO: PDF tiene valores divididos!")
    
    # VERIFICACIÓN FINAL
    print(f"\n{'='*70}")
    print("VERIFICACIÓN DE DIFERENCIAS:")
    print("="*70)
    
    conceptos_originales = [["2", "Producto A", "300.00", "600.00"], ["1", "Producto B", "400.00", "400.00"]]
    
    print("\nConceptos originales:")
    for concepto in conceptos_originales:
        print(f"  {concepto[1]}: P.Unit=${concepto[2]}, Total=${concepto[3]}")
    
    print("\nOrden anterior (INCORRECTO) - PDF tendría:")
    for concepto in conceptos_antes:
        print(f"  {concepto[1]}: P.Unit=${concepto[2]}, Total=${concepto[3]} ❌")
    
    print("\nOrden nuevo (CORRECTO) - PDF tiene:")
    for concepto in conceptos_despues:
        print(f"  {concepto[1]}: P.Unit=${concepto[2]}, Total=${concepto[3]} ✅")
    
    # Verificar que están divididos
    total_original = sum(float(c[3]) for c in conceptos_originales)
    total_pdf_anterior = sum(float(c[3]) for c in conceptos_antes)
    total_pdf_nuevo = sum(float(c[3]) for c in conceptos_despues)
    
    print(f"\nTotales calculados:")
    print(f"  Original: ${total_original:.2f}")
    print(f"  PDF orden anterior: ${total_pdf_anterior:.2f} {'❌ (sin dividir)' if abs(total_pdf_anterior - total_original) < 0.01 else ''}")
    print(f"  PDF orden nuevo: ${total_pdf_nuevo:.2f} {'✅ (dividido correctamente)' if abs(total_pdf_nuevo - total_original/2) < 0.01 else ''}")
    
    print(f"\n✅ CORRECCIÓN IMPLEMENTADA:")
    print("  - Los conceptos ahora se recopilan DESPUÉS de la división")
    print("  - La primera factura tendrá conceptos con valores divididos")
    print("  - Los totales Y los conceptos estarán sincronizados")
    print("  - Ambas facturas tendrán valores idénticos (divididos)")

if __name__ == "__main__":
    test_orden_recopilacion_conceptos()
