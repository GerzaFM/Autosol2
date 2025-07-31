#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
sys.path.append('src')
sys.path.append('src/buscarapp')

try:
    from autocarga.extractor_orden import OrdenDataExtractor
    from src.bd.models import OrdenCompra
    
    def corregir_bd_con_patrones_mejorados():
        print("=== CORRECCIÓN BD CON PATRONES MEJORADOS ===")
        
        # Crear instancia del extractor
        extractor = OrdenDataExtractor()
        
        print("🔍 Analizando todas las órdenes...")
        ordenes = OrdenCompra.select()
        
        correcciones_realizadas = 0
        
        for orden in ordenes:
            if orden.importe_en_letras:
                # Probar si los patrones mejorados producen un resultado diferente
                texto_original = orden.importe_en_letras
                texto_mejorado = extractor._agregar_espacios_importe_letras(texto_original)
                
                # Solo actualizar si hay una mejora real
                if texto_mejorado != texto_original:
                    print(f"🔄 Mejorando orden ID={orden.id}")
                    print(f"Antes:  {texto_original}")
                    print(f"Después: {texto_mejorado}")
                    
                    # Verificar que la mejora es real (no empeoramiento)
                    if len(texto_mejorado.split()) > len(texto_original.split()):
                        orden.importe_en_letras = texto_mejorado
                        orden.save()
                        correcciones_realizadas += 1
                        print("✅ Aplicado")
                    else:
                        print("⚠️  Saltado (no es mejora)")
                    print()
        
        print(f"\n=== RESUMEN ===")
        print(f"Correcciones aplicadas: {correcciones_realizadas}")
        
        # Verificación final
        print(f"\n=== VERIFICACIÓN FINAL ===")
        ordenes_actualizadas = OrdenCompra.select()
        for orden in ordenes_actualizadas:
            if orden.importe_en_letras:
                # Buscar patrones problemáticos
                problemas = []
                texto = orden.importe_en_letras
                
                if 'MILTRC' in texto or 'MILTRES' in texto:
                    problemas.append("MIL+TRES")
                if 'MILQUI' in texto:
                    problemas.append("MIL+QUIN")  
                if 'YSIETE' in texto or 'YNUEVE' in texto or 'YDOS' in texto:
                    problemas.append("Y+NUM")
                    
                estado = "⚠️" if problemas else "✅"
                problemas_str = ", ".join(problemas) if problemas else "Ninguno"
                
                print(f"ID {orden.id}: {estado} - Problemas: {problemas_str}")
                if orden.importe_en_letras:
                    print(f"   Texto: {orden.importe_en_letras[:60]}...")

    if __name__ == "__main__":
        corregir_bd_con_patrones_mejorados()

except ImportError as e:
    print(f"❌ Error al importar: {e}")
    print("Verifica que las rutas de los módulos sean correctas")
