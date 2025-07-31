#!/usr/bin/env python3
"""
Script de prueba para validar el formato correcto de nombres de archivo.

Formato solicitado: Folio Interno, Proveedor, Folio factura, Clase
- Folio Interno: El que se registra en la BD (obtenido de BD)
- Proveedor: Nombre del proveedor
- Folio factura: Folio del XML
- Clase: Campo específico del formulario en "Datos de solicitud"
"""

def simular_proximo_folio_interno():
    """Simula obtener el próximo folio interno de la BD."""
    # En la aplicación real, esto consultaría la BD
    return "158"

def construir_nombre_archivo_corregido(es_contexto_no_guardar, folio_interno_manual, solicitud_data, proveedor_data):
    """Simula la lógica corregida del nuevo formato de nombres de archivo."""
    
    # Obtener el folio interno que se usará en la BD (si no es contexto de no guardar)
    if not es_contexto_no_guardar:
        # Se guardará en BD: obtener el próximo folio interno
        folio_interno = str(simular_proximo_folio_interno())
    else:
        # No se guardará en BD: usar folio manual si existe
        folio_interno = folio_interno_manual
    
    proveedor = proveedor_data.get("Nombre", "")
    folio_factura = solicitud_data.get("Folio", "")
    clase = solicitud_data.get("Clase", "")  # Campo específico del formulario
    
    # Construcción del nombre según el formato solicitado: Folio Interno, Proveedor, Folio factura, Clase
    if folio_interno:
        nombre_elementos = [folio_interno, proveedor, folio_factura, clase]
    else:
        # Si no hay folio interno, usar formato reducido
        nombre_elementos = [proveedor, folio_factura, clase]
    
    # Filtrar campos vacíos y construir nombre con espacios
    nombre_archivo = " ".join(filter(lambda x: x and x.strip(), nombre_elementos))
    
    return nombre_archivo

def test_formato_nombres_corregido():
    """Prueba diferentes escenarios con el formato corregido."""
    print("=== PRUEBAS DE FORMATO CORREGIDO DE NOMBRES DE ARCHIVO ===\n")
    
    # Escenario 1: Factura normal (se guardará en BD)
    print("1. Factura Normal (se guardará en BD):")
    solicitud_data = {"Folio": "12345", "Clase": "Servicios Generales"}
    proveedor_data = {"Nombre": "EMPRESA SERVICIOS SA"}
    es_contexto_no_guardar = False
    folio_interno_manual = None
    
    nombre = construir_nombre_archivo_corregido(es_contexto_no_guardar, folio_interno_manual, solicitud_data, proveedor_data)
    print(f"   Resultado: '{nombre}'")
    print(f"   Elementos: Folio Interno BD (158) + Proveedor + Folio factura + Clase\n")
    
    # Escenario 2: Factura duplicada (NO se guardará en BD, folio manual)
    print("2. Factura Duplicada (NO se guardará en BD):")
    solicitud_data = {"Folio": "12345", "Clase": "Servicios Generales"}
    proveedor_data = {"Nombre": "EMPRESA SERVICIOS SA"}
    es_contexto_no_guardar = True
    folio_interno_manual = "155"
    
    nombre = construir_nombre_archivo_corregido(es_contexto_no_guardar, folio_interno_manual, solicitud_data, proveedor_data)
    print(f"   Resultado: '{nombre}'")
    print(f"   Elementos: Folio Interno Manual (155) + Proveedor + Folio factura + Clase\n")
    
    # Escenario 3: Segunda factura en división (NO se guardará en BD)
    print("3. Segunda Factura en División (NO se guardará en BD):")
    solicitud_data = {"Folio": "12346", "Clase": "Servicios Constructivos"}
    proveedor_data = {"Nombre": "CONSTRUCTORA MATEHUALA SA"}
    es_contexto_no_guardar = True
    folio_interno_manual = "156"
    
    nombre = construir_nombre_archivo_corregido(es_contexto_no_guardar, folio_interno_manual, solicitud_data, proveedor_data)
    print(f"   Resultado: '{nombre}'")
    print(f"   Elementos: Folio Interno Manual (156) + Proveedor + Folio factura + Clase\n")
    
    # Escenario 4: Sin clase definida
    print("4. Sin Clase Definida:")
    solicitud_data = {"Folio": "12347", "Clase": ""}
    proveedor_data = {"Nombre": "PROVEEDOR SIN CLASE SA"}
    es_contexto_no_guardar = False
    folio_interno_manual = None
    
    nombre = construir_nombre_archivo_corregido(es_contexto_no_guardar, folio_interno_manual, solicitud_data, proveedor_data)
    print(f"   Resultado: '{nombre}'")
    print(f"   Elementos: Folio Interno BD (158) + Proveedor + Folio factura (sin Clase)\n")
    
    # Escenario 5: Comparación con formato anterior
    print("5. Comparación con Formato Anterior:")
    solicitud_data = {"Folio": "98765", "Clase": "Servicios Administrativos"}
    proveedor_data = {"Nombre": "EMPRESA COMPLETA SA DE CV"}
    es_contexto_no_guardar = False
    folio_interno_manual = None
    
    nombre = construir_nombre_archivo_corregido(es_contexto_no_guardar, folio_interno_manual, solicitud_data, proveedor_data)
    print(f"   NUEVO: '{nombre}'")
    print(f"   ANTES: '98765 EMPRESA COMPLETA SA DE CV'")
    print(f"   MEJORA: Ahora incluye folio interno BD (158) y clase (Servicios Administrativos)\n")

if __name__ == "__main__":
    test_formato_nombres_corregido()
