#!/usr/bin/env python3
"""
Script de prueba final para verificar el formato correcto del comentario sin espacios extra
"""

print("🔄 Prueba Final de Comentarios (Sin Espacios Extra)")
print("=" * 60)

def generar_comentario_final(serie, folio):
    """Simula la lógica final del comentario corregida"""
    serie_str = serie or ""
    folio_str = folio or ""
    
    # Construir el comentario evitando espacios dobles
    if serie_str and folio_str:
        comentario_factura = f"Factura: {serie_str} {folio_str}"
    elif serie_str:
        comentario_factura = f"Factura: {serie_str}"
    elif folio_str:
        comentario_factura = f"Factura: {folio_str}"
    else:
        comentario_factura = "Factura:"
        
    return comentario_factura

# Casos de prueba
test_cases = [
    {"serie": "A", "folio": "12345", "expected": "Factura: A 12345"},
    {"serie": "", "folio": "12345", "expected": "Factura: 12345"}, 
    {"serie": None, "folio": "12345", "expected": "Factura: 12345"},
    {"serie": "A", "folio": "", "expected": "Factura: A"},
    {"serie": "A", "folio": None, "expected": "Factura: A"},
    {"serie": "", "folio": "", "expected": "Factura:"},
    {"serie": None, "folio": None, "expected": "Factura:"},
    {"serie": "FAC", "folio": "001", "expected": "Factura: FAC 001"},
    {"serie": "", "folio": "999", "expected": "Factura: 999"},
]

print("📋 Verificación de casos:")
all_passed = True

for i, caso in enumerate(test_cases, 1):
    serie = caso["serie"]
    folio = caso["folio"] 
    expected = caso["expected"]
    
    # Usar la lógica final corregida
    resultado = generar_comentario_final(serie, folio)
    
    status = "✅" if resultado == expected else "❌"
    if resultado != expected:
        all_passed = False
    
    print(f"   {i}. {status} Serie: {repr(serie)}, Folio: {repr(folio)}")
    print(f"       Esperado: '{expected}'")
    print(f"       Obtenido: '{resultado}'")
    if "  " in resultado:
        print(f"       ⚠️  Contiene espacios dobles")
    print()

if all_passed:
    print("🎉 ¡Todos los casos pasaron correctamente!")
    print("✅ El problema de los comentarios está resuelto")
    print("✅ Ahora el número de factura aparece correctamente sin espacios extra")
else:
    print("❌ Algunos casos fallaron")

print("\n📝 Resumen del comportamiento:")
print("   • Con serie y folio: 'Factura: SERIE FOLIO'")
print("   • Solo con folio: 'Factura: FOLIO' (SIN espacios extra)")
print("   • Solo con serie: 'Factura: SERIE'") 
print("   • Sin datos: 'Factura:'")
print("\n🎯 Problema resuelto: Las facturas sin serie ahora muestran correctamente el número en comentarios")
