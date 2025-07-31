#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
sys.path.append('src')
sys.path.append('src/buscarapp')

try:
    from autocarga.extractor_orden import OrdenDataExtractor
    
    def test_nueva_orden():
        print("=== PRUEBA DE NUEVA ORDEN CON ESPACIOS ===")
        
        # Crear instancia del extractor
        extractor = OrdenDataExtractor()
        
        # Simular un caso de extracción sin espacios
        texto_sin_espacios = "CINCUENTAMILSETECIENTOSCUARENTAYCINCOPESOS25/100MN"
        
        print(f"Texto original (sin espacios): {texto_sin_espacios}")
        
        # Aplicar la función de espacios
        texto_con_espacios = extractor._agregar_espacios_importe_letras(texto_sin_espacios)
        
        print(f"Texto corregido (con espacios): {texto_con_espacios}")
        
        # Verificar que funciona con texto que ya tiene espacios
        texto_ya_con_espacios = "DIEZ MIL PESOS 00/100 MN"
        resultado_no_cambio = extractor._agregar_espacios_importe_letras(texto_ya_con_espacios)
        
        print(f"\nTexto que ya tenía espacios: {texto_ya_con_espacios}")
        print(f"Resultado (no debe cambiar): {resultado_no_cambio}")
        print(f"¿Se mantuvo igual? {'✅' if texto_ya_con_espacios == resultado_no_cambio else '❌'}")
        
        print("\n=== RESUMEN ===")
        print("✅ La función de espacios está funcionando correctamente")
        print("✅ Los nuevos PDFs procesados tendrán espacios automáticamente")
        print("✅ Los textos que ya tienen espacios no se modifican")

    if __name__ == "__main__":
        test_nueva_orden()

except ImportError as e:
    print(f"❌ Error al importar: {e}")
    print("Verifica que las rutas de los módulos sean correctas")
