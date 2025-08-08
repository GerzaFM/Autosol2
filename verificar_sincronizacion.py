#!/usr/bin/env python3
"""
Verificar sincronización entre órdenes y proveedores
"""
import sys
import os
sys.path.insert(0, 'src')

from bd.models import Proveedor, OrdenCompra

print("=== VERIFICACIÓN DE SINCRONIZACIÓN ===")

# Obtener todas las órdenes con cuenta mayor
ordenes_con_cuenta = list(OrdenCompra.select().where(OrdenCompra.cuenta_mayor.is_null(False)))
print(f"Total órdenes con cuenta mayor: {len(ordenes_con_cuenta)}")

# Agrupar por código de cuenta
codigos_ordenes = {}
for orden in ordenes_con_cuenta:
    codigo = orden.cuenta
    if codigo not in codigos_ordenes:
        codigos_ordenes[codigo] = []
    codigos_ordenes[codigo].append(orden)

print(f"Códigos únicos con órdenes: {len(codigos_ordenes)}")
print()

# Verificar cada código
for codigo, ordenes in codigos_ordenes.items():
    proveedor = Proveedor.get_or_none(Proveedor.codigo_quiter == codigo)
    
    if not proveedor:
        print(f"❌ CÓDIGO {codigo}: No existe proveedor")
        continue
    
    cuenta_mayor_orden = ordenes[0].cuenta_mayor  # Todas deberían tener la misma
    
    print(f"🔍 CÓDIGO {codigo}:")
    print(f"   Proveedor: {proveedor.nombre or proveedor.nombre_en_quiter}")
    print(f"   Cuenta Mayor Proveedor: {proveedor.cuenta_mayor}")
    print(f"   Cuenta Mayor Orden: {cuenta_mayor_orden}")
    print(f"   Órdenes: {len(ordenes)}")
    
    if proveedor.cuenta_mayor == cuenta_mayor_orden:
        print(f"   ✅ SINCRONIZADO")
    else:
        print(f"   ❌ DESINCRONIZADO - NECESITA ACTUALIZACIÓN")
        print(f"      -> Debe actualizar proveedor de '{proveedor.cuenta_mayor}' a '{cuenta_mayor_orden}'")
    
    print()

print("=== FIN DE VERIFICACIÓN ===")
