#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
sys.path.append('src')
sys.path.append('src/buscarapp')

try:
    from autocarga.extractor_orden import OrdenDataExtractor
    from src.bd.models import OrdenCompra
    
    def main():
        print("=== TESTING FUNCIÓN DE ESPACIOS MEJORADA ===")
        
        # Crear instancia del extractor para usar la función de espacios
        extractor = OrdenDataExtractor()
        
        # Casos de prueba
        casos_prueba = [
            "SEISMILTRESCIENTOSOCHENTAPESOS00/100MN",
            "CUARENTAMILNOVECIENTOSOCHENTAYDOSPESOS83/100MN", 
            "NUEVEMILQUINIENTOSSETENTAYCUATROPESOS12/100MN",
            "DOSMILQUINIENTOSCINCUENTAPESOS00/100MN",
            "OCHOCIENTOSPESOS00/100MN",
            "DOCEMILDOSCIENTOSSESENTAPESOS01/100MN",
            "VEINTIUNMILCIENTOCINCUENTAYDOSPESOS74/100MN",
            "DIEZMILDOSCIENTOSSETENTAYUNPESOS70/100MN",
            "SEISMILSETECIENTOSSESENTAYSIETEPESOS38/100MN",
            "DIEZMILNOVECIENTOSCINCUENTAPESOS01/100MN"
        ]
        
        print("=== PRUEBAS DE LA FUNCIÓN MEJORADA ===")
        for caso in casos_prueba:
            resultado = extractor._agregar_espacios_importe_letras(caso)
            print(f"Original: {caso}")
            print(f"Corregido: {resultado}")
            print("---")
        
        print("\n=== CORRECCIÓN DE BD CON VERSIÓN MEJORADA ===")
        
        # Buscar órdenes sin espacios (sin espacios en importe_en_letras)
        ordenes_sin_espacios = []
        ordenes = OrdenCompra.select()
        
        for orden in ordenes:
            if orden.importe_en_letras and ' ' not in orden.importe_en_letras:
                ordenes_sin_espacios.append(orden)
        
        print(f"Órdenes encontradas sin espacios: {len(ordenes_sin_espacios)}")
        
        # Corregir cada orden
        corregidas = 0
        for orden in ordenes_sin_espacios:
            print(f"🔄 Corrigiendo orden ID={orden.id}")
            print(f"Antes: {orden.importe_en_letras}")
            
            # Aplicar corrección
            nuevo_importe = extractor._agregar_espacios_importe_letras(orden.importe_en_letras)
            orden.importe_en_letras = nuevo_importe
            orden.save()
            
            print(f"Después: {nuevo_importe}")
            print("✅ Guardado")
            corregidas += 1
        
        print(f"\n=== RESUMEN ===")
        print(f"✅ Órdenes corregidas: {corregidas}")
        
        # Verificar que ahora todas tienen espacios
        print(f"\n=== VERIFICACIÓN ===")
        todas_ordenes = OrdenCompra.select()
        for orden in todas_ordenes:
            if orden.importe_en_letras:
                tiene_espacios = ' ' in orden.importe_en_letras
                status = "✅" if tiene_espacios else "❌"
                # Truncar para display
                texto_display = orden.importe_en_letras[:50] + "..." if len(orden.importe_en_letras) > 50 else orden.importe_en_letras
                print(f"ID {orden.id}: {texto_display}")
                print(f"   Espacios: {status}")

    if __name__ == "__main__":
        main()

except ImportError as e:
    print(f"❌ Error al importar: {e}")
    print("Verifica que las rutas de los módulos sean correctas")
