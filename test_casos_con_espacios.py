#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
sys.path.append('src')
sys.path.append('src/buscarapp')

try:
    from autocarga.extractor_orden import OrdenDataExtractor
    
    def test_casos_con_espacios():
        print("=== PRUEBA DE CASOS CON ESPACIOS PROBLEMÁTICOS ===")
        
        # Crear instancia del extractor
        extractor = OrdenDataExtractor()
        
        # Casos específicos que mencionaste
        casos_con_espacios = [
            "SEISMIL TRESCIENTOS",
            "CUARENTAMIL NOVECIENTOS OCHENTA", 
            "NUEVEMIL QUINIENTOS",
            "DOSMIL QUINIENTOS CINCUENTA",
            "TRESMIL SEISCIENTOS TREINTA",
            "DIEZMIL NOVECIENTOS CINCUENTA",
            "DOCEMIL DOSCIENTOS SESENTA",
            "SIETEMIL SETECIENTOS SESENTA",
            "VEINTIUN MILCIENTO CINCUENTA"
        ]
        
        print("🔍 PRUEBAS DE CORRECCIÓN:")
        print("=" * 50)
        
        for i, caso in enumerate(casos_con_espacios, 1):
            resultado = extractor._agregar_espacios_importe_letras(caso)
            mejora = "✅" if resultado != caso else "❌"
            
            print(f"{i:2d}. Original:  {caso}")
            print(f"    Corregido: {resultado}")
            print(f"    Mejorado: {mejora}")
            print()
        
        print("🧪 PRUEBAS CON IMPORTES COMPLETOS:")
        print("=" * 50)
        
        # Casos completos más realistas
        importes_completos = [
            "SEISMIL TRESCIENTOS OCHENTA PESOS 00/100 MN",
            "CUARENTAMIL NOVECIENTOS OCHENTA Y DOS PESOS 83/100 MN",
            "NUEVEMIL QUINIENTOS SETENTA Y CUATRO PESOS 12/100 MN",
            "DOSMIL QUINIENTOS CINCUENTA PESOS 00/100 MN",
            "TRESMIL SEISCIENTOS TREINTA Y CUATRO PESOS 00/100 MN",
            "VEINTIUN MILCIENTO CINCUENTA Y DOS PESOS 74/100 MN"
        ]
        
        for i, caso in enumerate(importes_completos, 1):
            resultado = extractor._agregar_espacios_importe_letras(caso)
            mejora = "✅" if resultado != caso else "❌"
            
            print(f"{i}. Original:  {caso}")
            print(f"   Corregido: {resultado}")
            print(f"   Mejorado: {mejora}")
            print()
        
        print("🎯 ANÁLISIS DE PATRONES:")
        print("=" * 50)
        print("Patrones agregados para corregir:")
        print("• SEISMIL → SEIS MIL")
        print("• NUEVEMIL → NUEVE MIL") 
        print("• CUARENTAMIL → CUARENTA MIL")
        print("• Patrón general: NÚMERO+MIL+ESPACIO+CENTENAS")

    if __name__ == "__main__":
        test_casos_con_espacios()

except ImportError as e:
    print(f"❌ Error al importar: {e}")
    print("Verifica que las rutas de los módulos sean correctas")
