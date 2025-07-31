"""
Prueba para verificar que ambas facturas (primera y segunda) tienen los valores divididos correctamente.
"""

def test_division_ambas_facturas():
    """
    Simula la nueva lógica de división para verificar que ambas facturas tengan valores divididos.
    """
    print("=== PRUEBA: División de Valores en Ambas Facturas ===\n")
    
    # Valores originales simulados
    valores_originales = {
        "totales": {
            "Subtotal": "1000.00",
            "IVA": "160.00", 
            "Ret": "10.00",
            "TOTAL": "1150.00"
        },
        "conceptos": [
            {"cantidad": "2", "descripcion": "Producto A", "precio_unitario": "300.00", "total": "600.00"},
            {"cantidad": "1", "descripcion": "Producto B", "precio_unitario": "400.00", "total": "400.00"}
        ]
    }
    
    # Estado inicial de la aplicación
    estado = {
        "valores_ya_divididos": False,
        "dividir_marcado": True,
        "dividir_habilitado": True,
        "factura_tipo": "SC"
    }
    
    print("VALORES ORIGINALES:")
    print("-" * 40)
    print("Totales:")
    for k, v in valores_originales["totales"].items():
        print(f"  {k}: ${v}")
    print("\nConceptos:")
    for i, concepto in enumerate(valores_originales["conceptos"], 1):
        print(f"  {i}. Cant: {concepto['cantidad']}, Desc: {concepto['descripcion']}, "
              f"P.Unit: ${concepto['precio_unitario']}, Total: ${concepto['total']}")
    
    # PASO 1: Generar primera factura (SC)
    print(f"\nPASO 1: Generar Primera Factura (SC)")
    print("-" * 50)
    
    print(f"Estado antes de primera factura:")
    print(f"  - valores_ya_divididos: {estado['valores_ya_divididos']}")
    print(f"  - dividir_marcado: {estado['dividir_marcado']}")
    print(f"  - dividir_habilitado: {estado['dividir_habilitado']}")
    
    # Lógica: dividir solo si dividir_marcado Y NO valores_ya_divididos
    debe_dividir = estado["dividir_marcado"] and not estado["valores_ya_divididos"]
    print(f"  - ¿Debe dividir?: {debe_dividir}")
    
    if debe_dividir:
        print("\n✅ DIVIDIENDO VALORES (Primera factura)")
        
        # Dividir totales
        totales_divididos = {}
        for k, v in valores_originales["totales"].items():
            valor_original = float(v)
            valor_dividido = valor_original / 2
            totales_divididos[k] = f"{valor_dividido:.2f}"
            print(f"  Total {k}: ${v} → ${totales_divididos[k]}")
        
        # Dividir conceptos
        conceptos_divididos = []
        for concepto in valores_originales["conceptos"]:
            precio_original = float(concepto["precio_unitario"])
            total_original = float(concepto["total"])
            precio_dividido = precio_original / 2
            total_dividido = total_original / 2
            
            concepto_dividido = {
                "cantidad": concepto["cantidad"],  # Igual
                "descripcion": concepto["descripcion"],  # Igual
                "precio_unitario": f"{precio_dividido:.2f}",
                "total": f"{total_dividido:.2f}"
            }
            conceptos_divididos.append(concepto_dividido)
            
            print(f"  Concepto '{concepto['descripcion']}': P.Unit ${concepto['precio_unitario']} → ${concepto_dividido['precio_unitario']}, "
                  f"Total ${concepto['total']} → ${concepto_dividido['total']}")
        
        # Marcar como divididos
        estado["valores_ya_divididos"] = True
        print(f"\n✅ valores_ya_divididos = {estado['valores_ya_divididos']}")
        
        # Usar valores divididos
        valores_primera_factura = {
            "totales": totales_divididos,
            "conceptos": conceptos_divididos
        }
    else:
        print("\n❌ NO dividir (valores ya divididos)")
        valores_primera_factura = valores_originales
    
    # Cambiar estado para segunda factura
    estado["dividir_habilitado"] = False
    estado["factura_tipo"] = "VC"
    
    print(f"\nPrimera factura generada con valores:")
    for k, v in valores_primera_factura["totales"].items():
        print(f"  {k}: ${v}")
    
    # PASO 2: Generar segunda factura (VC)
    print(f"\nPASO 2: Generar Segunda Factura (VC)")
    print("-" * 50)
    
    print(f"Estado antes de segunda factura:")
    print(f"  - valores_ya_divididos: {estado['valores_ya_divididos']}")
    print(f"  - dividir_marcado: {estado['dividir_marcado']}")
    print(f"  - dividir_habilitado: {estado['dividir_habilitado']}")
    
    # Lógica: dividir solo si dividir_marcado Y NO valores_ya_divididos
    debe_dividir_segunda = estado["dividir_marcado"] and not estado["valores_ya_divididos"]
    print(f"  - ¿Debe dividir?: {debe_dividir_segunda}")
    
    if debe_dividir_segunda:
        print("\n❌ ERROR: No debería dividir de nuevo!")
        # Esto no debería pasar con la nueva lógica
        valores_segunda_factura = "ERROR - DIVIDIENDO DOBLE VEZ"
    else:
        print("\n✅ NO dividir (valores ya divididos correctamente)")
        # Usar los mismos valores divididos que la primera factura
        valores_segunda_factura = valores_primera_factura
    
    print(f"\nSegunda factura generada con valores:")
    if isinstance(valores_segunda_factura, dict):
        for k, v in valores_segunda_factura["totales"].items():
            print(f"  {k}: ${v}")
    else:
        print(f"  {valores_segunda_factura}")
    
    # Completar proceso de división
    print(f"\nPASO 3: Completar Proceso de División")
    print("-" * 50)
    estado["valores_ya_divididos"] = False  # Resetear para próxima vez
    estado["dividir_marcado"] = False
    estado["dividir_habilitado"] = True
    
    print(f"Estado final reseteado:")
    print(f"  - valores_ya_divididos: {estado['valores_ya_divididos']}")
    print(f"  - dividir_marcado: {estado['dividir_marcado']}")
    print(f"  - dividir_habilitado: {estado['dividir_habilitado']}")
    
    # VERIFICACIÓN FINAL
    print(f"\n{'='*70}")
    print("VERIFICACIÓN FINAL:")
    print("="*70)
    
    if isinstance(valores_primera_factura, dict) and isinstance(valores_segunda_factura, dict):
        primera_total = float(valores_primera_factura["totales"]["TOTAL"])
        segunda_total = float(valores_segunda_factura["totales"]["TOTAL"])
        original_total = float(valores_originales["totales"]["TOTAL"])
        
        print(f"Total original: ${original_total}")
        print(f"Primera factura: ${primera_total}")
        print(f"Segunda factura: ${segunda_total}")
        print(f"Suma de ambas: ${primera_total + segunda_total}")
        
        if abs((primera_total + segunda_total) - original_total) < 0.01:
            print("✅ CORRECTO: Las dos facturas suman el total original")
        else:
            print("❌ ERROR: Las facturas no suman correctamente")
            
        if abs(primera_total - segunda_total) < 0.01:
            print("✅ CORRECTO: Ambas facturas tienen el mismo total (dividido)")
        else:
            print("❌ ERROR: Las facturas tienen totales diferentes")
    else:
        print("❌ ERROR: No se pudieron generar ambas facturas correctamente")
    
    print("\n✅ NUEVA LÓGICA IMPLEMENTADA:")
    print("  - Solo se divide una vez (en la primera generación)")
    print("  - La segunda factura usa los valores ya divididos")
    print("  - Se evita la doble división")
    print("  - Ambas facturas tienen valores idénticos (divididos)")

if __name__ == "__main__":
    test_division_ambas_facturas()
