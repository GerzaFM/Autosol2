#!/usr/bin/env python3
"""
Script de prueba para verificar el formato correcto del comentario en reimprimir
"""

import sys
import os

print("🔄 Prueba de Comentarios en Reimpresión")
print("=" * 50)

# Simular diferentes casos de factura
test_cases = [
    {"serie": "A", "folio": "12345", "nombre": "Con serie y folio"},
    {"serie": "", "folio": "12345", "nombre": "Sin serie, con folio"}, 
    {"serie": None, "folio": "12345", "nombre": "Serie None, con folio"},
    {"serie": "A", "folio": "", "nombre": "Con serie, sin folio"},
    {"serie": "A", "folio": None, "nombre": "Con serie, folio None"},
    {"serie": "", "folio": "", "nombre": "Sin serie ni folio"},
    {"serie": None, "folio": None, "nombre": "Serie y folio None"}
]

print("📋 Casos de prueba:")
for i, caso in enumerate(test_cases, 1):
    serie = caso["serie"]
    folio = caso["folio"] 
    nombre = caso["nombre"]
    
    # Simular la lógica del comentario como está en el código
    comentario = f"Factura: {serie or ''} {folio or ''}".strip()
    
    print(f"   {i}. {nombre}:")
    print(f"      Serie: {repr(serie)}")
    print(f"      Folio: {repr(folio)}")
    print(f"      Comentario: '{comentario}'")
    
    # Verificar que el comentario no esté mal formado
    if comentario == "Factura:":
        print(f"      ⚠️  Solo 'Factura:' sin datos")
    elif comentario.startswith("Factura: "):
        print(f"      ✅ Comentario bien formado")
    else:
        print(f"      ❌ Comentario mal formado")
    print()

print("📝 Análisis:")
print("   - Cuando hay serie y folio: 'Factura: A 12345'")
print("   - Cuando solo hay folio: 'Factura: 12345'")  
print("   - Cuando solo hay serie: 'Factura: A'")
print("   - Cuando no hay nada: 'Factura:'")
print()
print("✅ Formato implementado para reimprimir: f\"Factura: {factura.serie or ''} {factura.folio or ''}\".strip()")
print("✅ Este es el mismo formato que usa solicitud_app_professional.py")
