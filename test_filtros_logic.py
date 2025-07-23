"""
Script para probar los filtros de la aplicación de búsqueda
"""

# Simulamos los datos que tendríamos en la aplicación
facturas_data = [
    {
        'folio_interno': 1,
        'serie_folio': 'DUB SAN-146',
        'tipo': 'VC',
        'fecha': '2025-07-22',
        'nombre_emisor': 'SOCIEDAD CONSTRUCTORA DUBLEX',
        'conceptos': 'SERVICIOS DE LIMPIEZA Y MANTENIMIENTO',
        'total': '$307.48',
        'cargada': 'Sí',
        'pagada': 'No',
        'cargada_bool': True,
        'pagada_bool': False
    },
    {
        'folio_interno': 2,
        'serie_folio': '1-1002',
        'tipo': 'I',
        'fecha': '2025-07-20',
        'nombre_emisor': 'Servicios Tecnológicos S.A.',
        'conceptos': 'Servicios profesionales de consultoría / Capacitación técnica especializada',
        'total': '$2,250.00',
        'cargada': 'No',
        'pagada': 'Sí',
        'cargada_bool': False,
        'pagada_bool': True
    },
    {
        'folio_interno': 3,
        'serie_folio': '2-2001',
        'tipo': 'I',
        'fecha': '2025-07-21',
        'nombre_emisor': 'Materiales de Oficina S.A.',
        'conceptos': 'Suministro de materiales de oficina / Equipos de cómputo y accesorios',
        'total': '$986.00',
        'cargada': 'Sí',
        'pagada': 'Sí',
        'cargada_bool': True,
        'pagada_bool': True
    },
    {
        'folio_interno': 4,
        'serie_folio': '2-2002',
        'tipo': 'I',
        'fecha': '2025-07-22',
        'nombre_emisor': 'Consultores Empresariales S.C.',
        'conceptos': 'Servicios de mantenimiento preventivo / Reparación de equipos especializados / Repuestos y componentes',
        'total': '$4,500.00',
        'cargada': 'No',
        'pagada': 'No',
        'cargada_bool': False,
        'pagada_bool': False
    }
]

def test_filter(description, fecha_inicial="", fecha_final="", tipo_filtro="", proveedor_filtro="", solo_cargado=False, solo_pagado=False, texto_busqueda=""):
    """Simula la aplicación de filtros"""
    print(f"\n🧪 TEST: {description}")
    print(f"   Filtros: fecha_inicial='{fecha_inicial}', fecha_final='{fecha_final}', tipo='{tipo_filtro}', proveedor='{proveedor_filtro}', solo_cargado={solo_cargado}, solo_pagado={solo_pagado}, texto='{texto_busqueda}'")
    
    filtered_data = []
    
    for factura in facturas_data:
        include_factura = True
        exclusion_reason = ""
        
        # Filtro por fecha inicial - SOLO si se especifica fecha inicial
        if fecha_inicial and include_factura:
            fecha_factura = factura.get('fecha', '')
            if fecha_factura < fecha_inicial:
                include_factura = False
                exclusion_reason = f"fecha factura ({fecha_factura}) < fecha inicial ({fecha_inicial})"
        
        # Filtro por fecha final - SOLO si se especifica fecha final
        if fecha_final and include_factura:
            fecha_factura = factura.get('fecha', '')
            if fecha_factura > fecha_final:
                include_factura = False
                exclusion_reason = f"fecha factura ({fecha_factura}) > fecha final ({fecha_final})"
        
        # Filtro por tipo - SOLO si se especifica tipo
        if tipo_filtro and include_factura:
            if factura.get('tipo', '') != tipo_filtro:
                include_factura = False
                exclusion_reason = f"tipo {factura.get('tipo', '')} != {tipo_filtro}"
        
        # Filtro por proveedor - SOLO si se especifica proveedor
        if proveedor_filtro and include_factura:
            emisor = factura.get('nombre_emisor', '').lower()
            if proveedor_filtro.lower() not in emisor:
                include_factura = False
                exclusion_reason = f"proveedor '{proveedor_filtro}' no encontrado en emisor"
        
        # Filtro Solo Cargado - SOLO si el checkbox está marcado
        if solo_cargado and include_factura:
            if not factura.get('cargada_bool', False):
                include_factura = False
                exclusion_reason = f"solo_cargado=True pero factura.cargada={factura.get('cargada_bool', False)}"
        
        # Filtro Solo Pagado - SOLO si el checkbox está marcado
        if solo_pagado and include_factura:
            if not factura.get('pagada_bool', False):
                include_factura = False
                exclusion_reason = f"solo_pagado=True pero factura.pagada={factura.get('pagada_bool', False)}"
        
        # Filtro de búsqueda de texto - SOLO si hay texto de búsqueda
        if texto_busqueda and include_factura:
            searchable_text = ' '.join([
                str(factura.get("folio_interno", "")),
                str(factura.get("serie_folio", "")),
                str(factura.get("tipo", "")),
                str(factura.get("nombre_emisor", "")),
                str(factura.get("conceptos", "")),
            ]).lower()
            
            if texto_busqueda.lower() not in searchable_text:
                include_factura = False
                exclusion_reason = f"texto '{texto_busqueda}' no encontrado"
        
        # Resultado
        if include_factura:
            filtered_data.append(factura)
            print(f"   ✅ {factura['serie_folio']} ({factura['fecha']}) - INCLUIDA")
        else:
            print(f"   ❌ {factura['serie_folio']} ({factura['fecha']}) - EXCLUIDA: {exclusion_reason}")
    
    print(f"   📊 Resultado: {len(filtered_data)} de {len(facturas_data)} facturas")

def main():
    print("=== PRUEBAS DE FILTROS ===")
    
    # Prueba 1: Sin filtros (todas las facturas)
    test_filter("Sin filtros - debe mostrar todas las facturas")
    
    # Prueba 2: Filtro por fecha inicial
    test_filter("Facturas desde 2025-07-21", fecha_inicial="2025-07-21")
    
    # Prueba 3: Filtro por fecha final  
    test_filter("Facturas hasta 2025-07-21", fecha_final="2025-07-21")
    
    # Prueba 4: Filtro por rango de fechas
    test_filter("Facturas entre 2025-07-21 y 2025-07-22", fecha_inicial="2025-07-21", fecha_final="2025-07-22")
    
    # Prueba 5: Filtro por tipo
    test_filter("Solo facturas tipo 'I'", tipo_filtro="I")
    
    # Prueba 6: Solo cargadas
    test_filter("Solo facturas cargadas", solo_cargado=True)
    
    # Prueba 7: Solo pagadas
    test_filter("Solo facturas pagadas", solo_pagado=True)
    
    # Prueba 8: Cargadas Y pagadas
    test_filter("Facturas cargadas Y pagadas", solo_cargado=True, solo_pagado=True)
    
    # Prueba 9: Búsqueda por texto
    test_filter("Búsqueda: 'consultoría'", texto_busqueda="consultoría")
    
    # Prueba 10: Filtros combinados
    test_filter("Tipo 'I' + Solo cargadas + desde 2025-07-21", tipo_filtro="I", solo_cargado=True, fecha_inicial="2025-07-21")

if __name__ == "__main__":
    main()
