"""
Script de prueba para reproducir el problema específico:
1. Factura duplicada + dividir -> Primera factura exporta con "ERROR" en lugar del folio manual
2. Segunda factura se sigue guardando en BD cuando no debería
"""

def test_problema_folio_error():
    """
    Simula el problema donde la primera factura se exporta con "ERROR"
    en lugar del folio manual ingresado por el usuario.
    """
    print("=== PROBLEMA: Primera factura exporta con 'ERROR' ===\n")
    
    # Estado simulado
    estado = {
        "factura_duplicada": True,
        "division_con_duplicado": True,
        "folio_interno_manual": "155",  # Usuario ingresó este folio
        "es_segunda_factura": False,
        "dividir_marcado": True
    }
    
    print("Estado actual:")
    for k, v in estado.items():
        print(f"  {k}: {v}")
    
    # Lógica actual
    print(f"\nLógica actual de asignación de folio:")
    es_contexto_no_guardar = (
        estado["factura_duplicada"] or 
        (estado["division_con_duplicado"] and estado["es_segunda_factura"])
    )
    
    print(f"es_contexto_no_guardar = {estado['factura_duplicada']} or ({estado['division_con_duplicado']} and {estado['es_segunda_factura']})")
    print(f"es_contexto_no_guardar = {es_contexto_no_guardar}")
    
    if es_contexto_no_guardar:
        folio_asignado = estado["folio_interno_manual"] or "DUPLICADO"
        print(f"✅ NO guardar en BD")
        print(f"✅ Folio asignado: {folio_asignado}")
        
        if folio_asignado == estado["folio_interno_manual"]:
            print(f"✅ CORRECTO: Usando folio manual del usuario")
        else:
            print(f"❌ ERROR: No usando folio manual")
    else:
        print(f"❌ ERROR: Debería ser contexto de no guardar")
    
    print(f"\n¿Por qué podría exportar 'ERROR'?")
    print(f"- Si folio_interno_manual es None o vacío")
    print(f"- Si hay una excepción durante el guardado")
    print(f"- Si la lógica de asignación no está funcionando")

def test_problema_segunda_factura_guarda():
    """
    Simula el problema donde la segunda factura se guarda en BD
    cuando no debería guardarse.
    """
    print(f"\n{'='*60}")
    print("=== PROBLEMA: Segunda factura se guarda en BD ===")
    print("="*60)
    
    # Estado para segunda factura
    estado_segunda = {
        "factura_duplicada": True,  # La original estaba duplicada
        "division_con_duplicado": True,  # Se estableció en primera carga
        "folio_interno_manual": "156",  # Usuario ingresó folio para segunda
        "es_segunda_factura": True,
        "dividir_marcado": True
    }
    
    print("\nEstado para segunda factura:")
    for k, v in estado_segunda.items():
        print(f"  {k}: {v}")
    
    # Verificar lógica
    es_contexto_no_guardar_segunda = (
        estado_segunda["factura_duplicada"] or 
        (estado_segunda["division_con_duplicado"] and estado_segunda["es_segunda_factura"])
    )
    
    print(f"\nLógica para segunda factura:")
    print(f"es_contexto_no_guardar = {estado_segunda['factura_duplicada']} or ({estado_segunda['division_con_duplicado']} and {estado_segunda['es_segunda_factura']})")
    print(f"es_contexto_no_guardar = {es_contexto_no_guardar_segunda}")
    
    if es_contexto_no_guardar_segunda:
        print(f"✅ CORRECTO: Segunda factura NO debería guardarse")
        print(f"✅ Debe usar folio manual: {estado_segunda['folio_interno_manual']}")
    else:
        print(f"❌ ERROR: Segunda factura se guardaría automáticamente")
        print(f"❌ PROBLEMA: Lógica no funcionando correctamente")

def test_posibles_causas():
    """
    Analiza las posibles causas de los problemas.
    """
    print(f"\n{'='*60}")
    print("=== ANÁLISIS DE POSIBLES CAUSAS ===")
    print("="*60)
    
    print(f"\nPROBLEMA 1: Primera factura exporta con 'ERROR'")
    print(f"Posibles causas:")
    print(f"  1. folio_interno_manual es None cuando se usa")
    print(f"  2. Exception en bloque try-catch que asigna 'ERROR'")
    print(f"  3. Variable es_segunda_factura no definida correctamente")
    print(f"  4. Condición es_contexto_no_guardar no funcionando")
    
    print(f"\nPROBLEMA 2: Segunda factura se guarda en BD")
    print(f"Posibles causas:")
    print(f"  1. division_con_duplicado no se mantiene para segunda factura")
    print(f"  2. es_segunda_factura no se detecta correctamente")
    print(f"  3. Lógica es_contexto_no_guardar fallando para segunda factura")
    print(f"  4. Flag se resetea prematuramente")
    
    print(f"\nSOLUCIONES RECOMENDADAS:")
    print(f"  1. Verificar que es_segunda_factura esté disponible en scope correcto")
    print(f"  2. Asegurar que folio_interno_manual se mantiene correctamente")
    print(f"  3. Agregar logging para debug de variables críticas")
    print(f"  4. Verificar que division_con_duplicado no se resetea prematuramente")

def test_debug_variables():
    """
    Simula el debug de variables que se debería agregar.
    """
    print(f"\n{'='*60}")
    print("=== DEBUG RECOMENDADO ===")
    print("="*60)
    
    debug_code = '''
    # Agregar antes de es_contexto_no_guardar
    logger.debug(f"DEBUG - factura_duplicada: {self.factura_duplicada}")
    logger.debug(f"DEBUG - division_con_duplicado: {self.division_con_duplicado}")
    logger.debug(f"DEBUG - es_segunda_factura: {es_segunda_factura}")
    logger.debug(f"DEBUG - folio_interno_manual: {self.folio_interno_manual}")
    logger.debug(f"DEBUG - dividir_marcado: {dividir_marcado}")
    logger.debug(f"DEBUG - dividir_habilitado: {dividir_habilitado}")
    
    es_contexto_no_guardar = (
        self.factura_duplicada or 
        (self.division_con_duplicado and es_segunda_factura)
    )
    
    logger.debug(f"DEBUG - es_contexto_no_guardar: {es_contexto_no_guardar}")
    '''
    
    print("Código de debug recomendado:")
    print(debug_code)

if __name__ == "__main__":
    test_problema_folio_error()
    test_problema_segunda_factura_guarda()
    test_posibles_causas()
    test_debug_variables()
