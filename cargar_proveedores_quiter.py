#!/usr/bin/env python3
"""
Script para cargar todos los proveedores de Quiter desde cero en base de datos limpia
"""

import sys
import os
import re

# Agregar el directorio src al path para importar los modelos
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from bd.models import db, Proveedor

def generar_rfc_dummy(nombre, codigo):
    """Genera un RFC dummy basado en el nombre y código del proveedor"""
    if not nombre:
        nombre = "PROVEEDOR"
    
    # Tomar las primeras 3 consonantes del nombre
    consonantes = ''.join([c for c in nombre.upper() if c.isalpha() and c not in 'AEIOUÑ'])[:3]
    if len(consonantes) < 3:
        consonantes = consonantes.ljust(3, 'X')
    
    # Agregar 6 dígitos basados en el código
    codigo_str = str(codigo).zfill(6)[-6:]  # Tomar últimos 6 dígitos
    
    # Agregar 3 caracteres finales
    rfc = f"{consonantes}{codigo_str}XXX"
    
    return rfc[:13]  # RFC máximo 13 caracteres

def cargar_proveedores_quiter():
    """Carga todos los proveedores desde el archivo BD.txt"""
    if not os.path.exists('BD.txt'):
        print("❌ Archivo BD.txt no encontrado")
        print("Por favor, coloca el archivo BD.txt en la raíz del proyecto")
        return False
    
    proveedores_agregados = 0
    errores = 0
    rfcs_usados = set()
    
    print("🔄 Cargando proveedores desde BD.txt...")
    
    try:
        with open('BD.txt', 'r', encoding='utf-8') as f:
            for linea_num, linea in enumerate(f, 1):
                linea = linea.strip()
                if not linea:
                    continue
                
                try:
                    # Separar por tabulación
                    partes = linea.split('\t')
                    if len(partes) < 2:
                        print(f"⚠️  Línea {linea_num} inválida: {linea}")
                        continue
                    
                    codigo_str = partes[0].strip()
                    nombre = partes[1].strip()
                    
                    # Manejar códigos numéricos y alfanuméricos
                    try:
                        codigo = int(codigo_str)
                    except ValueError:
                        # Para códigos como F4, F5, F6, convertir a string
                        codigo = codigo_str
                    
                    # Generar RFC único
                    rfc_base = generar_rfc_dummy(nombre, codigo)
                    rfc = rfc_base
                    contador = 1
                    
                    while rfc in rfcs_usados:
                        if contador > 999:
                            rfc = f"QTR{str(hash(f'{codigo}{nombre}'))[-9:]}"
                            break
                        rfc = f"{rfc_base[:-3]}{contador:03d}"
                        contador += 1
                    
                    # Crear el proveedor
                    proveedor = Proveedor.create(
                        nombre=nombre,
                        nombre_en_quiter=nombre,
                        codigo_quiter=codigo,
                        rfc=rfc,
                        telefono=None,
                        email=None,
                        nombre_contacto=None,
                        cuenta_mayor=None
                    )
                    
                    rfcs_usados.add(rfc)
                    proveedores_agregados += 1
                    
                    print(f"✅ {nombre} (código: {codigo}, RFC: {rfc})")
                    
                except Exception as e:
                    errores += 1
                    print(f"❌ Error en línea {linea_num} ({linea[:50]}...): {e}")
                    
    except FileNotFoundError:
        print("❌ No se pudo leer el archivo BD.txt")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False
    
    print(f"\n🎉 Carga completada:")
    print(f"   • Proveedores agregados: {proveedores_agregados}")
    print(f"   • Errores: {errores}")
    
    return True

def main():
    print("🚀 Iniciando carga de proveedores de Quiter...")
    
    # Conectar a la base de datos y crear tablas
    try:
        db.connect(reuse_if_open=True)
        # Asegurar que las tablas existan
        db.create_tables([Proveedor], safe=True)
        print("✅ Conectado a la base de datos")
    except Exception as e:
        print(f"❌ Error al conectar a la base de datos: {e}")
        return False
    
    # Verificar estado actual
    count_actual = Proveedor.select().count()
    print(f"📊 Proveedores actuales en BD: {count_actual}")
    
    if count_actual > 0:
        print("⚠️  Ya existen proveedores en la base de datos")
        respuesta = input("¿Deseas continuar agregando más proveedores? (y/n): ").lower()
        if respuesta not in ['y', 'yes', 's', 'si', 'sí']:
            print("❌ Operación cancelada")
            return False
    
    # Cargar proveedores
    success = cargar_proveedores_quiter()
    
    if success:
        final_count = Proveedor.select().count()
        print(f"📊 Total final de proveedores: {final_count}")
    
    return success

if __name__ == "__main__":
    success = main()
    if success:
        print("🎉 Script ejecutado exitosamente!")
    else:
        print("💥 Script falló!")
        sys.exit(1)
