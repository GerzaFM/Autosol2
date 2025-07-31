#!/usr/bin/env python3
"""
Script de prueba para validar el nuevo formato de nombres de archivo.
"""

def construir_nombre_archivo(folio_interno_manual, solicitud_data, proveedor_data):
    """Simula la lógica del nuevo formato de nombres de archivo."""
    # Construir nombre de archivo con formato: Folio Interno Proveedor Folio factura Clase
    folio_interno = folio_interno_manual
    proveedor = proveedor_data.get("Nombre", "")
    folio_factura = solicitud_data.get("Folio", "")
    clase = solicitud_data.get("Tipo", "")
    
    # Si no hay folio interno manual, omitir ese campo para evitar duplicar el folio
    if folio_interno:
        nombre_elementos = [folio_interno, proveedor, folio_factura, clase]
    else:
        # Formato original cuando no hay folio interno: Folio factura Proveedor Clase
        nombre_elementos = [folio_factura, proveedor, clase]
    
    # Filtrar campos vacíos y construir nombre con espacios
    nombre_archivo = " ".join(filter(lambda x: x and x.strip(), nombre_elementos))
    
    return nombre_archivo

def test_formato_nombres():
    """Prueba diferentes escenarios de nombres de archivo."""
    print("=== PRUEBAS DE FORMATO DE NOMBRES DE ARCHIVO ===\n")
    
    # Escenario 1: Factura normal (no duplicada)
    print("1. Factura Normal (sin folio interno manual):")
    solicitud_data = {"Folio": "12345", "Tipo": "SC Servicios"}
    proveedor_data = {"Nombre": "EMPRESA SERVICIOS SA"}
    folio_interno_manual = None
    
    nombre = construir_nombre_archivo(folio_interno_manual, solicitud_data, proveedor_data)
    print(f"   Resultado: '{nombre}'")
    print(f"   Antes era: '12345 EMPRESA SERVICIOS SA'\n")
    
    # Escenario 2: Factura duplicada con folio manual
    print("2. Factura Duplicada (con folio interno manual):")
    solicitud_data = {"Folio": "12345", "Tipo": "SC Servicios"}
    proveedor_data = {"Nombre": "EMPRESA SERVICIOS SA"}
    folio_interno_manual = "155"
    
    nombre = construir_nombre_archivo(folio_interno_manual, solicitud_data, proveedor_data)
    print(f"   Resultado: '{nombre}'")
    print(f"   Antes era: '12345 EMPRESA SERVICIOS SA'\n")
    
    # Escenario 3: Segunda factura en división
    print("3. Segunda Factura (VC) en División:")
    solicitud_data = {"Folio": "12346", "Tipo": "VC Servicios"}
    proveedor_data = {"Nombre": "EMPRESA SERVICIOS SA"}
    folio_interno_manual = "156"
    
    nombre = construir_nombre_archivo(folio_interno_manual, solicitud_data, proveedor_data)
    print(f"   Resultado: '{nombre}'")
    print(f"   Antes era: '12346 EMPRESA SERVICIOS SA'\n")
    
    # Escenario 4: Datos incompletos
    print("4. Datos Incompletos:")
    solicitud_data = {"Folio": "", "Tipo": "SC Servicios"}
    proveedor_data = {"Nombre": "EMPRESA SERVICIOS SA"}
    folio_interno_manual = "157"
    
    nombre = construir_nombre_archivo(folio_interno_manual, solicitud_data, proveedor_data)
    print(f"   Resultado: '{nombre}'")
    print(f"   Antes era: ' EMPRESA SERVICIOS SA'\n")
    
    # Escenario 5: Tipo de vale largo
    print("5. Tipo de Vale Largo:")
    solicitud_data = {"Folio": "98765", "Tipo": "SC Servicios Constructivos"}
    proveedor_data = {"Nombre": "CONSTRUCTORA MATEHUALA SA DE CV"}
    folio_interno_manual = "200"
    
    nombre = construir_nombre_archivo(folio_interno_manual, solicitud_data, proveedor_data)
    print(f"   Resultado: '{nombre}'")
    print(f"   Antes era: '98765 CONSTRUCTORA MATEHUALA SA DE CV'\n")

if __name__ == "__main__":
    test_formato_nombres()
