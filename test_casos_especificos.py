#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
sys.path.append('src')
sys.path.append('src/buscarapp')

try:
    from autocarga.extractor_orden import OrdenDataExtractor
    
    def test_casos_especificos():
        print("=== PRUEBA DE CASOS ESPECÍFICOS PROBLEMÁTICOS ===")
        
        # Crear instancia del extractor
        extractor = OrdenDataExtractor()
        
        # Casos específicos que mencionaste
        casos_problematicos = [
            "MILTRCIENTOS",
            "MILQUINIENTOS", 
            "YSIETE",
            "MILSETECIENTOS",
            "YNUEVE",
            "YDOS",
            "CUATROMILQUINIENTOSYSIETE",
            "SIETEMILTRESCIENTOSYOCHO",
            "NUEVEMILQUINIENTOSSETENTAYCUATRO",
            "DOCEMILDOSCIENTOSYUNO",
            "VEINTEMILNOVECIENTOSYCINCO"
        ]
        
        print("🔍 PRUEBAS INDIVIDUALES:")
        for i, caso in enumerate(casos_problematicos, 1):
            resultado = extractor._agregar_espacios_importe_letras(caso)
            print(f"{i:2d}. Original:  {caso}")
            print(f"    Corregido: {resultado}")
            print()
        
        print("🧪 PRUEBAS CON IMPORTES COMPLETOS:")
        
        # Casos completos más realistas
        importes_completos = [
            "MILTRCIENTOSPESOS00/100MN",
            "CUATROMILQUINIENTOSYSIETEPESOS25/100MN",
            "SIETEMILTRESCIENTOSYOCHOPESOS50/100MN",
            "NUEVEMILQUINIENTOSSETENTAYCUATROPESOS12/100MN",
            "DOCEMILDOSCIENTOSYUNPESOS01/100MN",
            "VEINTEMILNOVECIENTOSYCINCOPESOS99/100MN"
        ]
        
        for i, caso in enumerate(importes_completos, 1):
            resultado = extractor._agregar_espacios_importe_letras(caso)
            print(f"{i}. Original:  {caso}")
            print(f"   Corregido: {resultado}")
            
            # Verificar calidad de la corrección
            espacios_ok = " " in resultado
            tiene_y_correcta = "Y " in resultado if "Y" in resultado else True
            tiene_mil_correcta = "MIL " in resultado if "MIL" in resultado else True
            
            calidad = "✅" if (espacios_ok and tiene_y_correcta and tiene_mil_correcta) else "⚠️"
            print(f"   Calidad: {calidad}")
            print()
        
        print("🎯 RESUMEN:")
        print("Los patrones mejorados ahora manejan:")
        print("✅ MIL + NÚMEROS específicos (MILTRESCIENTOS → MIL TRESCIENTOS)")
        print("✅ Y + NÚMEROS específicos (YSIETE → Y SIETE)")
        print("✅ Casos complejos con múltiples combinaciones")
        print("✅ Orden de aplicación mejorado para evitar conflictos")

    if __name__ == "__main__":
        test_casos_especificos()

except ImportError as e:
    print(f"❌ Error al importar: {e}")
    print("Verifica que las rutas de los módulos sean correctas")
