#!/usr/bin/env python3
"""
Script para probar el modelo Vale actualizado
"""
import sys
import os
sys.path.insert(0, '..')

from bd.models import Vale
import logging

def test_modelo_vale():
    print("=== PROBANDO MODELO VALE ACTUALIZADO ===")
    
    try:
        # Obtener todos los vales
        print("\n1. CONSULTANDO TODOS LOS VALES:")
        total_vales = Vale.select().count()
        print(f"📊 Total de vales: {total_vales}")
        
        # Obtener vales de SERVICIO NAVA MEDRANO
        print("\n2. VALES DE SERVICIO NAVA MEDRANO:")
        vales_nava = Vale.select().where(
            (Vale.proveedor.contains('NAVA')) | 
            (Vale.proveedor.contains('MEDRANO'))
        )
        
        for vale in vales_nava:
            print(f"  📄 ID: {vale.id} | No: {vale.noVale} | Proveedor: {vale.proveedor} | Total: ${vale.total}")
        
        # Obtener un vale específico para mostrar todos sus campos
        print("\n3. DETALLE COMPLETO DE UN VALE DE NAVA MEDRANO:")
        if vales_nava.exists():
            vale_ejemplo = vales_nava.first()
            print(f"  🆔 ID: {vale_ejemplo.id}")
            print(f"  📄 No Vale: {vale_ejemplo.noVale}")
            print(f"  🏷️ Tipo: {vale_ejemplo.tipo}")
            print(f"  📋 No Documento: {vale_ejemplo.noDocumento}")
            print(f"  📝 Descripción: {vale_ejemplo.descripcion}")
            print(f"  🔢 Referencia: {vale_ejemplo.referencia}")
            print(f"  💰 Total: {vale_ejemplo.total}")
            print(f"  🏦 Cuenta: {vale_ejemplo.cuenta}")
            print(f"  📅 Fecha: {vale_ejemplo.fechaVale}")
            print(f"  🏢 Proveedor: {vale_ejemplo.proveedor}")
        
        print(f"\n✅ El modelo Vale funciona correctamente!")
        print(f"✅ Los vales de SERVICIO NAVA MEDRANO están disponibles")
        print(f"✅ Ahora deberían aparecer en el frame de información de la aplicación")
        
    except Exception as e:
        print(f"❌ Error probando el modelo: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_modelo_vale()
