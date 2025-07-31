#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
sys.path.append('src')
sys.path.append('src/buscarapp')

try:
    from src.bd.models import OrdenCompra
    
    def listar_archivos_originales():
        print("=== ARCHIVOS PDF ORIGINALES EN LA BASE DE DATOS ===")
        
        ordenes = OrdenCompra.select()
        
        for orden in ordenes:
            archivo = orden.archivo_original if orden.archivo_original else "No especificado"
            espacios = "✅" if (orden.importe_en_letras and ' ' in orden.importe_en_letras) else "❌"
            print(f"ID {orden.id}: {archivo}")
            print(f"   Proveedor: {orden.nombre}")
            print(f"   Importe en letras tiene espacios: {espacios}")
            if orden.importe_en_letras:
                print(f"   Texto: {orden.importe_en_letras[:60]}...")
            print()

    if __name__ == "__main__":
        listar_archivos_originales()

except ImportError as e:
    print(f"❌ Error al importar: {e}")
    print("Verifica que las rutas de los módulos sean correctas")
