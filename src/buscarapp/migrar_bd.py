#!/usr/bin/env python3
"""
Script para revisar y migrar bases de datos
"""
import sys
import os
import sqlite3
import shutil
from datetime import datetime

def revisar_bd(db_path, nombre):
    print(f"\n=== REVISANDO {nombre}: {db_path} ===")
    
    if not os.path.exists(db_path):
        print(f"❌ No existe: {db_path}")
        return None
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Ver tablas disponibles
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tablas = [t[0] for t in cursor.fetchall()]
        print(f"📋 Tablas encontradas: {tablas}")
        
        # Revisar tabla vales si existe
        if 'vales' in tablas:
            cursor.execute("SELECT COUNT(*) FROM vales")
            count_vales = cursor.fetchone()[0]
            print(f"💳 Vales en BD: {count_vales}")
            
            if count_vales > 0:
                # Mostrar algunos vales
                cursor.execute("SELECT noVale, proveedor, total FROM vales LIMIT 5")
                vales_muestra = cursor.fetchall()
                for v in vales_muestra:
                    print(f"  📄 {v[0]} - {v[1]} - ${v[2]}")
        
        # Revisar tabla proveedores si existe  
        if 'proveedores' in tablas:
            cursor.execute("SELECT COUNT(*) FROM proveedores")
            count_prov = cursor.fetchone()[0]
            print(f"🏢 Proveedores en BD: {count_prov}")
        
        # Revisar tabla facturas si existe
        if 'facturas' in tablas:
            cursor.execute("SELECT COUNT(*) FROM facturas")
            count_fact = cursor.fetchone()[0]
            print(f"📋 Facturas en BD: {count_fact}")
        
        conn.close()
        return {
            'path': db_path,
            'tablas': tablas,
            'vales': count_vales if 'vales' in tablas else 0,
            'proveedores': count_prov if 'proveedores' in tablas else 0,
            'facturas': count_fact if 'facturas' in tablas else 0
        }
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def migrar_datos():
    print("=== INICIANDO MIGRACIÓN DE BASES DE DATOS ===")
    
    # Rutas de las bases de datos
    bd_raiz = "../../facturas.db"
    bd_solicitud = "../../src/solicitudapp/facturas.db"
    bd_destino = "../../facturas.db"
    
    # Revisar ambas bases de datos
    info_raiz = revisar_bd(bd_raiz, "BD RAÍZ")
    info_solicitud = revisar_bd(bd_solicitud, "BD SOLICITUD")
    
    # Determinar cuál tiene más datos
    if info_solicitud and info_solicitud['vales'] > 0:
        print(f"\n✅ La BD de solicitud tiene datos, la usaremos como fuente")
        bd_fuente = bd_solicitud
        info_fuente = info_solicitud
    elif info_raiz and info_raiz['vales'] > 0:
        print(f"\n✅ La BD de raíz tiene datos, la mantendremos")
        bd_fuente = bd_raiz
        info_fuente = info_raiz
    else:
        print(f"\n⚠️ Ninguna BD tiene datos de vales, usaremos la de solicitud como base")
        bd_fuente = bd_solicitud
        info_fuente = info_solicitud
    
    if bd_fuente != bd_destino:
        print(f"\n🔄 Copiando {bd_fuente} → {bd_destino}")
        
        # Hacer backup de la BD destino si existe
        if os.path.exists(bd_destino):
            backup_name = f"../../facturas_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            shutil.copy2(bd_destino, backup_name)
            print(f"💾 Backup creado: {backup_name}")
        
        # Copiar la BD fuente al destino
        shutil.copy2(bd_fuente, bd_destino)
        print(f"✅ Base de datos migrada exitosamente")
    
    # Eliminar la BD duplicada
    if os.path.exists(bd_solicitud) and bd_solicitud != bd_destino:
        os.remove(bd_solicitud)
        print(f"🗑️ Eliminada BD duplicada: {bd_solicitud}")
    
    # Verificar resultado final
    print(f"\n=== RESULTADO FINAL ===")
    info_final = revisar_bd(bd_destino, "BD FINAL")
    
    print(f"\n✅ Migración completada. Base de datos única en: {bd_destino}")

if __name__ == "__main__":
    migrar_datos()
