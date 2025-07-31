"""
Prueba específica para verificar que los flags se mantienen correctamente
durante el proceso completo de división con factura duplicada.
"""

def test_flujo_completo_division_duplicada():
    """
    Simula el flujo completo paso a paso para identificar dónde se pierde la información.
    """
    print("=== FLUJO COMPLETO: División con Factura Duplicada ===\n")
    
    # Estado inicial de la aplicación
    app_state = {
        "factura_duplicada": False,
        "division_con_duplicado": False,
        "folio_interno_manual": None,
        "valores_ya_divididos": False,
        "dividir_var": True,  # Usuario tiene dividir marcado
        "dividir_habilitado": True
    }
    
    print("PASO 1: Cargar XML duplicado")
    print("-" * 40)
    print("Usuario selecciona XML que ya existe en BD")
    
    # Simular carga de XML (esto resetea flags)
    print("Reseteando flags (inicio de carga XML)...")
    app_state["factura_duplicada"] = False
    app_state["division_con_duplicado"] = False
    app_state["folio_interno_manual"] = None
    
    # Verificar si existe en BD
    xml_existe = True
    if xml_existe:
        print("✅ XML existe en BD")
        app_state["factura_duplicada"] = True
        
        # CRÍTICO: Verificar si dividir está activado
        if app_state["dividir_var"]:
            app_state["division_con_duplicado"] = True
            print("✅ Dividir está activado -> division_con_duplicado = True")
        
        # Pedir folio manual
        folio_usuario = "155"
        app_state["folio_interno_manual"] = folio_usuario
        print(f"✅ Usuario ingresa folio manual: {folio_usuario}")
    
    print(f"\nEstado después de cargar XML:")
    for k, v in app_state.items():
        print(f"  {k}: {v}")
    
    print(f"\nPASO 2: Generar Primera Factura (SC)")
    print("-" * 40)
    
    es_segunda_factura = False
    dividir_marcado = app_state["dividir_var"]
    dividir_habilitado = app_state["dividir_habilitado"]
    
    print(f"Variables de generación:")
    print(f"  es_segunda_factura: {es_segunda_factura}")
    print(f"  dividir_marcado: {dividir_marcado}")
    print(f"  dividir_habilitado: {dividir_habilitado}")
    
    # Lógica de guardado para primera factura
    es_contexto_no_guardar = (
        app_state["factura_duplicada"] or 
        (app_state["division_con_duplicado"] and es_segunda_factura)
    )
    
    print(f"\nes_contexto_no_guardar = {app_state['factura_duplicada']} or ({app_state['division_con_duplicado']} and {es_segunda_factura})")
    print(f"es_contexto_no_guardar = {es_contexto_no_guardar}")
    
    if es_contexto_no_guardar:
        folio_pdf = app_state["folio_interno_manual"] or "DUPLICADO"
        print(f"✅ Primera factura: NO guardar, folio PDF: {folio_pdf}")
        
        if folio_pdf == app_state["folio_interno_manual"]:
            print(f"✅ CORRECTO: PDF tendrá folio manual del usuario")
        else:
            print(f"❌ ERROR: PDF tendrá 'DUPLICADO' en lugar del folio")
    else:
        print(f"❌ ERROR: Primera factura se guardaría (no debería)")
    
    # Cambiar estado para segunda factura
    app_state["dividir_habilitado"] = False  # Se deshabilita después de primera
    app_state["valores_ya_divididos"] = True  # Se marcan valores como divididos
    
    print(f"\nPASO 3: Preparar Segunda Factura")
    print("-" * 40)
    print("Cambiar tipo a VC, deshabilitar dividir checkbox")
    print(f"Estado actualizado:")
    print(f"  dividir_habilitado: {app_state['dividir_habilitado']}")
    print(f"  valores_ya_divididos: {app_state['valores_ya_divididos']}")
    
    # PUNTO CRÍTICO: ¿Se mantienen los flags?
    print(f"\n¿Flags críticos se mantienen?")
    print(f"  factura_duplicada: {app_state['factura_duplicada']} (debe ser True)")
    print(f"  division_con_duplicado: {app_state['division_con_duplicado']} (debe ser True)")
    print(f"  folio_interno_manual: {app_state['folio_interno_manual']} (debe tener valor)")
    
    print(f"\nPASO 4: Generar Segunda Factura (VC)")
    print("-" * 40)
    
    # Pedir folio manual para segunda factura
    if app_state["factura_duplicada"]:
        folio_segunda = "156"
        app_state["folio_interno_manual"] = folio_segunda
        print(f"✅ Usuario ingresa folio para segunda: {folio_segunda}")
    
    es_segunda_factura = True
    
    # Lógica de guardado para segunda factura
    es_contexto_no_guardar_segunda = (
        app_state["factura_duplicada"] or 
        (app_state["division_con_duplicado"] and es_segunda_factura)
    )
    
    print(f"\nLógica para segunda factura:")
    print(f"es_contexto_no_guardar = {app_state['factura_duplicada']} or ({app_state['division_con_duplicado']} and {es_segunda_factura})")
    print(f"es_contexto_no_guardar = {es_contexto_no_guardar_segunda}")
    
    if es_contexto_no_guardar_segunda:
        folio_pdf_segunda = app_state["folio_interno_manual"] or "DUPLICADO"
        print(f"✅ Segunda factura: NO guardar, folio PDF: {folio_pdf_segunda}")
        print(f"✅ CORRECTO: Comportamiento consistente")
    else:
        print(f"❌ ERROR: Segunda factura se guardaría automáticamente")
        print(f"❌ CAUSA POSIBLE: Flag division_con_duplicado se perdió")
    
    # Completar proceso
    print(f"\nPASO 5: Completar Proceso")
    print("-" * 40)
    app_state["division_con_duplicado"] = False
    app_state["valores_ya_divididos"] = False
    app_state["dividir_var"] = False
    app_state["dividir_habilitado"] = True
    print("✅ Flags reseteados después de completar división")

def test_puntos_criticos():
    """
    Identifica los puntos críticos donde se pueden perder los flags.
    """
    print(f"\n{'='*60}")
    print("=== PUNTOS CRÍTICOS IDENTIFICADOS ===")
    print("="*60)
    
    puntos = [
        {
            "punto": "Carga inicial de XML",
            "riesgo": "Resetea todos los flags antes de detectar duplicado",
            "solucion": "Establecer division_con_duplicado DESPUÉS de detectar duplicado + dividir"
        },
        {
            "punto": "Entre primera y segunda factura",
            "riesgo": "Si se recarga XML, se pierden flags",
            "solucion": "No recargar XML entre primera y segunda factura"
        },
        {
            "punto": "Variable es_segunda_factura",
            "riesgo": "Puede no estar definida en scope correcto",
            "solucion": "Definir es_segunda_factura una sola vez al inicio"
        },
        {
            "punto": "Asignación de folio_interno_manual",
            "riesgo": "Se puede sobreescribir entre primera y segunda factura",
            "solucion": "Mantener folio hasta completar todo el proceso"
        }
    ]
    
    for i, punto in enumerate(puntos, 1):
        print(f"\n{i}. {punto['punto']}")
        print(f"   Riesgo: {punto['riesgo']}")
        print(f"   Solución: {punto['solucion']}")

if __name__ == "__main__":
    test_flujo_completo_division_duplicada()
    test_puntos_criticos()
