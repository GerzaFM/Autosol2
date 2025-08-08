#!/usr/bin/env python3
"""
Script para sincronizar cuenta mayor de órdenes a proveedores
"""
import sys
import os
sys.path.insert(0, 'src')

from bd.models import Proveedor, OrdenCompra

print("=== SINCRONIZACIÓN DE CUENTA MAYOR ===")

# Obtener todas las órdenes con cuenta mayor
ordenes_con_cuenta = list(OrdenCompra.select().where(OrdenCompra.cuenta_mayor.is_null(False)))
print(f"Procesando {len(ordenes_con_cuenta)} órdenes con cuenta mayor...")

# Agrupar por código de cuenta
codigos_ordenes = {}
for orden in ordenes_con_cuenta:
    codigo = orden.cuenta
    if codigo not in codigos_ordenes:
        codigos_ordenes[codigo] = []
    codigos_ordenes[codigo].append(orden)

actualizaciones = 0
errores = 0

# Sincronizar cada código
for codigo, ordenes in codigos_ordenes.items():
    try:
        proveedor = Proveedor.get_or_none(Proveedor.codigo_quiter == codigo)
        
        if not proveedor:
            print(f"❌ CÓDIGO {codigo}: No existe proveedor")
            errores += 1
            continue
        
        cuenta_mayor_orden = ordenes[0].cuenta_mayor  # Todas deberían tener la misma
        
        # Solo actualizar si no tiene cuenta mayor o es diferente
        if proveedor.cuenta_mayor != cuenta_mayor_orden:
            print(f"🔄 Actualizando proveedor {codigo}:")
            print(f"   Nombre: {proveedor.nombre or proveedor.nombre_en_quiter}")
            print(f"   Antes: {proveedor.cuenta_mayor}")
            print(f"   Después: {cuenta_mayor_orden}")
            
            # ACTUALIZAR
            proveedor.cuenta_mayor = cuenta_mayor_orden
            proveedor.save()
            
            actualizaciones += 1
            print(f"   ✅ ACTUALIZADO")
        else:
            print(f"✅ {codigo} ya sincronizado: {cuenta_mayor_orden}")
    
    except Exception as e:
        print(f"❌ Error procesando código {codigo}: {e}")
        errores += 1

print(f"\n=== RESUMEN ===")
print(f"Actualizaciones realizadas: {actualizaciones}")
print(f"Errores: {errores}")
print(f"Total códigos procesados: {len(codigos_ordenes)}")

# Verificación final
print(f"\n=== VERIFICACIÓN FINAL ===")
desincronizados = 0
for codigo, ordenes in codigos_ordenes.items():
    proveedor = Proveedor.get_or_none(Proveedor.codigo_quiter == codigo)
    if proveedor:
        cuenta_mayor_orden = ordenes[0].cuenta_mayor
        if proveedor.cuenta_mayor != cuenta_mayor_orden:
            desincronizados += 1
            print(f"❌ Aún desincronizado: {codigo}")

if desincronizados == 0:
    print("🎉 ¡TODOS LOS PROVEEDORES ESTÁN SINCRONIZADOS!")
else:
    print(f"❌ Quedan {desincronizados} proveedores desincronizados")

print("=== FIN ===")
