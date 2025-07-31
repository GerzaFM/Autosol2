#!/usr/bin/env python3
"""
Script para probar y corregir el importe en letras sin espacios
"""
import sys
sys.path.append('src')
sys.path.append('src/buscarapp')

try:
    from autocarga.extractor_orden import OrdenDataExtractor
    from src.bd.models import OrdenCompra
    
    print("=== TESTING FUNCIÓN DE ESPACIOS ===")
    
    # Crear instancia del extractor
    extractor = OrdenDataExtractor()
    
    # Probar con algunos ejemplos de la BD
    ejemplos_sin_espacios = [
        "SEISMILTRESCIENTOSOCHENTAPESOS00/100MN",
        "CUARENTAMILNOVECIENTOSOCHENTAYDOSPESOS83/100MN", 
        "NUEVEMILQUINIENTOSSETENTAYCUATROPESOS12/100MN",
        "DOSMILQUINIENTOSCINCUENTAPESOS00/100MN",
        "OCHOCIENTOSPESOS00/100MN"
    ]
    
    print("=== PRUEBAS DE LA FUNCIÓN ===")
    for ejemplo in ejemplos_sin_espacios:
        resultado = extractor._agregar_espacios_importe_letras(ejemplo)
        print(f"Original: {ejemplo}")
        print(f"Corregido: {resultado}")
        print("---")
    
    print("\n=== CORRECCIÓN DE BD ===")
    # Corregir las órdenes en la base de datos
    ordenes_sin_espacios = OrdenCompra.select().where(
        ~OrdenCompra.importe_en_letras.contains(' '),
        OrdenCompra.importe_en_letras.is_null(False),
        OrdenCompra.importe_en_letras != ''
    )
    
    count = ordenes_sin_espacios.count()
    print(f"Órdenes encontradas sin espacios: {count}")
    
    corregidas = 0
    for orden in ordenes_sin_espacios:
        try:
            original = orden.importe_en_letras
            if original and len(original) > 10 and ' ' not in original:
                corregido = extractor._agregar_espacios_importe_letras(original)
                
                if corregido != original:
                    print(f"\n🔄 Corrigiendo orden ID={orden.id}")
                    print(f"Antes: {original}")
                    print(f"Después: {corregido}")
                    
                    orden.importe_en_letras = corregido
                    orden.save()
                    corregidas += 1
                    print("✅ Guardado")
                
        except Exception as e:
            print(f"❌ Error corrigiendo orden {orden.id}: {e}")
    
    print(f"\n=== RESUMEN ===")
    print(f"✅ Órdenes corregidas: {corregidas}")
    
    # Verificar resultados
    print(f"\n=== VERIFICACIÓN ===")
    ordenes_verificacion = OrdenCompra.select().limit(5)
    for orden in ordenes_verificacion:
        importe_letras = orden.importe_en_letras or ""
        tiene_espacios = ' ' in importe_letras
        print(f"ID {orden.id}: {importe_letras[:50]}{'...' if len(importe_letras) > 50 else ''}")
        print(f"   Espacios: {'✅' if tiene_espacios else '❌'}")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
