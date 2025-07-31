#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
sys.path.append('src')
sys.path.append('src/buscarapp')

try:
    from src.bd.models import OrdenCompra, Factura
    
    def verificacion_final():
        print("=== VERIFICACIÓN FINAL DEL SISTEMA ===")
        
        # Contar órdenes totales
        total_ordenes = OrdenCompra.select().count()
        print(f"📊 Total de órdenes: {total_ordenes}")
        
        # Verificar asociaciones
        ordenes_asociadas = OrdenCompra.select().where(OrdenCompra.factura_id.is_null(False)).count()
        print(f"🔗 Órdenes asociadas: {ordenes_asociadas}")
        print(f"📊 Porcentaje de asociación: {(ordenes_asociadas/total_ordenes*100):.1f}%")
        
        # Verificar espacios en importe_en_letras
        ordenes_con_espacios = 0
        ordenes_sin_espacios = 0
        
        for orden in OrdenCompra.select():
            if orden.importe_en_letras:
                if ' ' in orden.importe_en_letras:
                    ordenes_con_espacios += 1
                else:
                    ordenes_sin_espacios += 1
        
        print(f"✅ Órdenes con espacios en importe_en_letras: {ordenes_con_espacios}")
        print(f"❌ Órdenes sin espacios en importe_en_letras: {ordenes_sin_espacios}")
        
        print("\n=== DETALLES DE ÓRDENES ===")
        for orden in OrdenCompra.select():
            asociada = "✅" if orden.factura_id else "❌"
            espacios = "✅" if (orden.importe_en_letras and ' ' in orden.importe_en_letras) else "❌"
            proveedor = orden.nombre[:30] + "..." if len(orden.nombre) > 30 else orden.nombre
            importe_display = (orden.importe_en_letras[:40] + "...") if orden.importe_en_letras and len(orden.importe_en_letras) > 40 else orden.importe_en_letras
            
            print(f"ID {orden.id}: {proveedor}")
            print(f"   Asociada: {asociada} | Espacios: {espacios}")
            print(f"   Importe: {importe_display}")
            print()
        
        print("=== RESUMEN GENERAL ===")
        if ordenes_sin_espacios == 0:
            print("✅ PROBLEMA DE ESPACIOS RESUELTO: Todas las órdenes tienen espacios correctos")
        else:
            print(f"⚠️  PENDIENTE: {ordenes_sin_espacios} órdenes aún sin espacios")
            
        if ordenes_asociadas >= total_ordenes * 0.8:  # 80% o más
            print("✅ ASOCIACIONES BUENAS: Más del 80% de órdenes están asociadas")
        else:
            print(f"⚠️  ASOCIACIONES PENDIENTES: Solo {(ordenes_asociadas/total_ordenes*100):.1f}% asociadas")

    if __name__ == "__main__":
        verificacion_final()

except ImportError as e:
    print(f"❌ Error al importar: {e}")
except Exception as e:
    print(f"❌ Error: {e}")
