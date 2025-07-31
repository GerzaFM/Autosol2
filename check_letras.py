#!/usr/bin/env python3
"""
Script para verificar el estado actual del importe en letras
"""
import sys
sys.path.append('src')

try:
    from src.bd.models import OrdenCompra
    
    print("=== ANÁLISIS IMPORTE EN LETRAS ===")
    
    ordenes = OrdenCompra.select().limit(10)
    
    for orden in ordenes:
        print(f"ID: {orden.id}")
        print(f"Importe: ${orden.importe}")
        importe_letras = orden.importe_en_letras or ""
        print(f"Importe en letras: \"{importe_letras}\"")
        print(f"Longitud: {len(importe_letras)}")
        
        # Análisis detallado
        tiene_espacios = ' ' in importe_letras
        print(f"Tiene espacios: {tiene_espacios}")
        
        if not tiene_espacios and len(importe_letras) > 20:
            print("❌ PROBLEMA: Texto largo sin espacios")
            # Mostrar primeros y últimos caracteres
            if len(importe_letras) > 50:
                print(f"Inicio: \"{importe_letras[:25]}...\"")
                print(f"Final: \"...{importe_letras[-25:]}\"")
        elif tiene_espacios:
            print("✅ OK: Contiene espacios")
        
        print("---")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
